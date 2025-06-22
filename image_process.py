from PIL import Image
import pytesseract
import re
import queue
import threading
from PIL import Image
import time
import pandas as pd  # need for pytesseract OUTPUT.DATAFRAME

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

COVER_ICON_MARGIN = (0, 0.16, 0.05, 1)  # left,top, size_x, size_y

TITLE_REGION = (0, 0, 1, 0.16)  # left, top, sizex, sizey
# Original regions
STAT_1_REGION = (0.05, 0.18, 0.93, 0.26)
STAT_2_REGION = (0.05, 0.43, 0.93, 0.26)
STAT_3_REGION = (0.05, 0.73, 0.93, 0.26)

RADIUS_MARGIN = 0.14

# Split each region into two: FIRST and SECOND
def split_region_vertically(region):
    left, top, width, height = region
    half_height = height / 2
    first_region = (left, top, width, half_height)
    second_region = (left, top + half_height, width, half_height)
    return first_region, second_region

STAT_1_FIRST_REGION, STAT_1_SECOND_REGION = split_region_vertically(STAT_1_REGION)
STAT_2_FIRST_REGION, STAT_2_SECOND_REGION = split_region_vertically(STAT_2_REGION)
STAT_3_FIRST_REGION, STAT_3_SECOND_REGION = split_region_vertically(STAT_3_REGION)


class ImageProcessor:
    # can star in seprate thread if mutilple file need to process, can also instant as a object to do process
    def __init__(self, thread_flag: bool):
        self.queue = queue.Queue()
        self.result = []
        self._stop_event = threading.Event()
        self.thread = None
        if thread_flag:
            self.thread = threading.Thread(target=self._worker)
            self.thread.start()

    def _worker(self):
        while not self._stop_event.is_set() or not self.queue.empty():
            try:
                start_time = time.time()
                # Estimate time for remaining images in queue
                queue_size = self.queue.qsize()
               
                est_time_per_image = 0.0
                temp_start = time.time()

                screenshot = self.queue.get()
                processed = self.process(screenshot)
                self.result.append(processed)
            
                temp_end = time.time()
                est_time_per_image = temp_end - temp_start
                est_total = est_time_per_image * queue_size
                print(f"Estimated remaining time: {est_total:.2f}s for {queue_size} images")
                self.queue.task_done()
            except queue.Empty:
                continue
    
    def add_screenshot(self, screenshot):
        self.queue.put(screenshot)

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def get_result(self):
        return self.result

    def process(self, image):
        image = self.image_preprocess(image, COVER_ICON_MARGIN)
        text_array = self.extract_text(image)
        return text_array

    def image_preprocess(self, image, margin=(0, 0, 0, 0), tencity=0):
        img = image.convert("L")  # Convert to grayscale
        # Apply a threshold to polarize the image
        threshold = 108 - tencity
        polarized = img.point(lambda p: 255 if p > threshold else 0)

        # Black out region if margin is specified
        if any(margin):
            width, height = polarized.size
            left = int(width * margin[0])
            top = int(height * margin[1])
            right = int(width * margin[2])
            bottom = int(height * margin[3])
            for y in range(top, bottom):
                for x in range(left, right):
                    polarized.putpixel((x, y), 0)
        return polarized

    def extract_text(self, image):
        # image is PIL image.Image
        result = []
        pixel_regions = self.get_row_regions(image)

        data = pytesseract.image_to_data(
            image, config=' --psm 6', output_type=pytesseract.Output.DATAFRAME)
        data = data[data.text.notnull()]

        data['row'] = data['top'].apply(lambda y : self.assign_row(y, image))
        data = data[data['row'] != -1]

        data['line'] = data['top'].apply(lambda y: self.assign_line(y, image))
        data = data[data['line'] != -1]


        grouped_rows = data.groupby('row')



        for row_index, group in grouped_rows:
            sorted_group = group.sort_values(by=["line","left"])
            line = ' '.join(sorted_group['text'])
            result.append(line.strip())

        return result

    def assign_row(self, y, image):
        row_regions = self.get_row_regions(image)

        for i, (start_x, start_y, size_x, size_y) in enumerate(row_regions):
            start = start_y
            end = start_y + size_y
            if start <= y <= end:
                return i
        return -1  # or None, for items not in any region
    
    def assign_line(self, y, image):
        line_regions = self.get_line_regions(image)
        for i, (start_x, start_y, size_x, size_y) in enumerate(line_regions):
            start = start_y
            end = start_y + size_y
            if start <= y <= end:
                return i
        return -1  # or None, for items not in any region

    def margin_to_pixel(self, image, margin_tuple):
        width, height = image.size
        left_up_x = int(width * margin_tuple[0])
        left_up_y = int(height * margin_tuple[1])
        size_x = int(width * margin_tuple[2])
        size_y = int(height * margin_tuple[3])
        return (left_up_x, left_up_y, size_x, size_y)

    def get_row_regions(self, image):
        # retunr regions in pixel that contain the title, and each stats
        title_pixel_region = self.margin_to_pixel(image, TITLE_REGION)
        stat1_pixel_region = self.margin_to_pixel(image, STAT_1_REGION)
        stat2_pixel_region = self.margin_to_pixel(image, STAT_2_REGION)
        stat3_pixel_region = self.margin_to_pixel(image, STAT_3_REGION)
        pixel_regions = [
            title_pixel_region,
            stat1_pixel_region,
            stat2_pixel_region,
            stat3_pixel_region
        ]
        return pixel_regions
    
    def get_line_regions(self, image):
        # return regions in pixel that contain each line of the image
        title_pixel_region = self.margin_to_pixel(image, TITLE_REGION)
        stat1_first = self.margin_to_pixel(image, STAT_1_FIRST_REGION)
        stat1_second = self.margin_to_pixel(image, STAT_1_SECOND_REGION)
        stat2_first = self.margin_to_pixel(image, STAT_2_FIRST_REGION)
        stat2_second = self.margin_to_pixel(image, STAT_2_SECOND_REGION)
        stat3_first = self.margin_to_pixel(image, STAT_3_FIRST_REGION)
        stat3_second = self.margin_to_pixel(image, STAT_3_SECOND_REGION)
        pixel_line_regions = [
            title_pixel_region,
            stat1_first,
            stat1_second,
            stat2_first,
            stat2_second,
            stat3_first,
            stat3_second
        ]
        return pixel_line_regions

    def extract_progress_bar(self, image):
        # 1. Preprocess the image (convert to grayscale and threshold)
        img = image.convert("L")
        threshold = 60
        binary = img.point(lambda p: 255 if p > threshold else 0)

        # 2. Get center x coordinate
        width, height = binary.size
        center_x = width // 2

        # 3. Loop through all pixels at center_x
        temp_array = []
        for y in range(height):
            pixel = binary.getpixel((center_x, y))
            # 4. If pixel is "full" (white), append coord
            if pixel == 255:
                temp_array.append((center_x, y))

        # 5. Find pixel with highest y value (lowest on image)
        if temp_array:
            max_y = max(coord[1] for coord in temp_array)
            margin_value = max_y / height
            return margin_value
        else:
            return 0.0


if __name__ == "__main__":   
    image_path = "screen_shot_temp/other_img.png"
    image = Image.open(image_path)
    processor = ImageProcessor(thread_flag=False)
    value = processor.extract_progress_bar(image)
    print(f"Progress bar margin value: {value:.4f}")