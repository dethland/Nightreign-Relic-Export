import pytesseract
import queue
import threading
from PIL import Image
import pandas as pd  # need for pytesseract OUTPUT.DATAFRAME
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

COVER_ICON_MARGIN = (0.0032858707557502738, 0.15202702702702703, 0.04819277108433735, 0.8378378378378378)

# TITLE_REGION = (0.002190580503833516, 0.0033783783783783786, 0.9014238773274917, 0.12837837837837837)  # left, top, sizex, sizey
# # Original regions
# STAT_1_REGION = (0.05147864184008762, 0.1858108108108108, 0.9649507119386638, 0.44932432432432434)
# STAT_2_REGION = (0.04928806133625411, 0.4391891891891892, 0.963855421686747, 0.7027027027027027)
# STAT_3_REGION = (0.050383351588170866, 0.7094594594594594, 0.9627601314348302, 0.9797297297297297)

TITLE_REGION = (0, 0, 1, 0.16)  # left, top, sizex, sizey
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
                screenshot = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            start_time = time.time()
            processed = self.process(screenshot)
            self.result.append(processed)
            self.queue.task_done()

            queue_size = self.queue.qsize()
            elapsed = time.time() - start_time
            if queue_size > 0:
                est_total = elapsed * queue_size
                print(f"Estimated remaining time: {est_total:.2f}s for {queue_size} images")
    
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
        # Extract text from image using pytesseract and organize by row and line
        result = []
        data = pytesseract.image_to_data(
            image, config=' --psm 6', output_type=pytesseract.Output.DATAFRAME)
        data = data[data.text.notnull()]

        # Assign each detected text box to a row and line
        data['row'] = data['top'].apply(lambda y: self.assign_row(y, image))
        data = data[data['row'] != -1]
        data['line'] = data['top'].apply(lambda y: self.assign_line(y, image))
        data = data[data['line'] != -1]

        # Group by row, then by line within each row, and concatenate text
        for row_index, row_group in data.groupby('row'):
            lines = []
            for line_index, line_group in row_group.groupby('line'):
                sorted_line = line_group.sort_values(by="left")
                line_text = ' '.join(sorted_line['text'])
                lines.append(line_text.strip())
            result.append(' '.join(lines).strip())

        return result

    def assign_row(self, y, image):
        # use to assign text to row block, data process, dont touch
        row_regions = self.get_row_regions(image)

        for i, (start_x, start_y, size_x, size_y) in enumerate(row_regions):
            start = start_y
            end = start_y + size_y
            if start <= y <= end:
                return i
        return -1  # or None, for items not in any region
    
    def assign_line(self, y, image):
        # use to assign text to line block, data process, dont touch
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
        threshold = 75
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
        
    def extract_remain_relic_count(self, image):
         # 1. Preprocess the image (convert to grayscale and threshold)
        img = image.convert("L")
        threshold = 60
        binary = img.point(lambda p: 255 if p > threshold else 0)


if __name__ == "__main__":   
    image_path = "screen_shot_temp/other_img.png"
    image = Image.open(image_path)
    processor = ImageProcessor(thread_flag=False)
    value = processor.process(image)
    print(value)
    # print(f"Progress bar margin value: {value:.4f}")