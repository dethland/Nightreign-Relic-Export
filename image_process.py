import os
from PIL import Image, ImageOps
import pytesseract
import re
import queue
import threading

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

COVER_ICON_MARGIN = (0.16, 0, 0.05, 1) # top, left, right, down

TITLE_REGION = (0, 0, 1, 0.16) # left, top, sizex, sizey
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
        # title = self.extract_text_from_region(image=image, region=TITLE_REGION)
        # stat1 = self.extract_text_from_region(image=image, region=STAT_1_REGION)
        # stat2 = self.extract_text_from_region(image=image, region=STAT_2_REGION)
        # stat3 = self.extract_text_from_region(image=image, region=STAT_3_REGION)
        text_array = self.extract_text(image)
        return [title, stat1, stat2, stat3]

    def clean_text(self, text):
        cleaned_text = re.sub(r"[^\w\s]", "", text)
        cleaned_text = cleaned_text.strip()
        return cleaned_text

    def image_preprocess(self, image, margin=(0, 0, 0, 0)):
        img = image.convert("L")  # Convert to grayscale
        # Apply a threshold to polarize the image
        threshold = 118 - 10
        polarized = img.point(lambda p: 255 if p > threshold else 0)
        polarized = img
        # Black out region if margin is specified
        if any(margin):
            width, height = polarized.size
            top = int(height * margin[0])
            left = int(width * margin[1])
            right = int(width * margin[2])
            bottom = int(height * margin[3])
            for y in range(top, bottom):
                for x in range(left, right):
                    polarized.putpixel((x, y), 0)

        return polarized


    def extract_text(self, image):
        # image is PIL image.Image
        rows = []
        current_row = []
        last_top = None
        last_top_y

        data = pytesseract.image_to_boxes(image)
        data.
        
        # text = text.replace('\n', ' ').strip()
        # text = self.text_to_array(text)
        return text


    def crop_image(self, img, crop_box):
        return img.crop(crop_box)


    def text_to_array(self, text):
        lines = re.split(r'(?<!\w)\n', text)
        return [line for line in lines if line.strip()]
    

    def extract_text_from_region(self, image, region):
        width, height = image.size
        left = int(region[0] * width)
        top = int(region[1] * height)
        right = int((region[0] + region[2]) * width)
        bottom = int((region[1] + region[3]) * height)
        crop_box = (left, top, right, bottom)
        cropped_img = image.crop(crop_box)
        return self.extract_text(cropped_img)


    def assign_row(y):
        for i, (start, end) in enumerate(row_regions):
            if start <= y <= end:
                return i
        return -1  # or None, for items not in any region