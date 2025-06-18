import os
from PIL import Image, ImageOps
import pytesseract
import re
import queue
import threading
import pandas as pd  # need for pytesseract OUTPUT.DATAFRAME

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

COVER_ICON_MARGIN = (0, 0.16, 0.05, 1)  # left,top, size_x, size_y

TITLE_REGION = (0, 0, 1, 0.16)  # left, top, sizex, sizey
STAT_1_REGION = (0.05, 0.18, 0.93, 0.26)
STAT_2_REGION = (0.05, 0.43, 0.93, 0.26)
STAT_3_REGION = (0.05, 0.73, 0.93, 0.26)


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
                processed = self.process(screenshot)
                self.result.append(processed)
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

    def image_preprocess(self, image, margin=(0, 0, 0, 0)):
        img = image.convert("L")  # Convert to grayscale
        # Apply a threshold to polarize the image
        threshold = 118 - 10
        polarized = img.point(lambda p: 255 if p > threshold else 0)
        polarized = img
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
        pixel_regions = self.get_pixel_regions(image)

        data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DATAFRAME)
        data = data[data.text.notnull()]

        data['row'] = data['top'].apply(lambda y : self.assign_row(y, image))
        data = data[data['row'] != -1]

        grouped_rows = data.groupby('row')

        for row_index, group in grouped_rows:
            sorted_group = group.sort_values(by="left")
            line = ' '.join(sorted_group['text'])
            result.append(line.strip())

        return result

    def assign_row(self, y, image):
        row_regions = self.get_pixel_regions(image)

        for i, (start_x, start_y, size_x, size_y) in enumerate(row_regions):
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

    def get_pixel_regions(self, image):
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
