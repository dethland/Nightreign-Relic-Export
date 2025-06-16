import os
from PIL import Image, ImageOps
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



class ImageProcessor:
    def __init__(self, output_dir="screen_shot_temp_processed"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_image(self, image_path):
        """
        Load an image from the given path and return a PIL Image object.
        """
        return Image.open(image_path)
    
    def clean_text(self, text):
        cleaned_text = re.sub(r"[^\w\s]", "", title)
        cleaned_text = cleaned_text.strip()
        return cleaned_text


    def convert(self, image_path, margin=(0, 0, 0, 0)):
        """
        Preprocess the image into a 'polarised' image and save to output_dir.
        Optionally black out a rectangular region defined by margin ratios (top, left, right, bottom).
        margin: tuple of 4 floats (top, left, right, bottom), each in [0, 1] as a ratio of image size.
        """
        img = Image.open(image_path).convert("L")  # Convert to grayscale
        # Apply a threshold to polarize the image
        threshold = 128 - 10
        polarized = img.point(lambda p: 255 if p > threshold else 0)
        # Black out region if margin is specified
        if any(margin):
            width, height = polarized.size
            top = int(height * margin[0])
            left = int(width * margin[1])
            right = int(width * margin[2])
            bottom = int(height * margin[3])
            # Draw black rectangle
            for y in range(top, bottom):
                for x in range(left, right):
                    polarized.putpixel((x, y), 0)
        # Save the processed image
        base_name = os.path.basename(image_path)
        save_path = os.path.join(self.output_dir, base_name)
        polarized.save(save_path)
        return save_path



    def extract_title(self, image : Image.Image):
        size = image.size
        factor = 0.12  # Adjust this factor as needed for the title region height
        crop_region = (0, 0, size[0], int(size[1] * factor))
        img = image.crop(crop_region)
        text = pytesseract.image_to_string(img)
        return text
    

    # def extract_


    def extract_region_text(self, image_path, crop_box):
        pass

    def extract_text(self, image_path):
        """
        Extract text from the given image using pytesseract.
        """
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        text = self.text_to_array(text)
        return text


    def crop_image(self, img, crop_box):
        return img.crop(crop_box)
    

    def text_to_array(self, text):
        lines = text.split("\n")
        # Remove empty strings from the array
        return [line for line in lines if line.strip()]

# Example usage:
if __name__ == "__main__":
    processor = ImageProcessor()
    for i in range(1, 11):
        image_path = f"screen_shot_temp/screenshot_{i}.png"
        processed_path = processor.convert(image_path, (0.16, 0, 0.046, 1))
        extracted_text = processor.extract_text(processed_path)
        print(f"Extracted text for screenshot_{i}.png:")
        print(extracted_text)
        print("-" * 40)
    # loaded_image = processor.load_image(processed_path)
    # title = processor.extract_title(loaded_image)
    # title = re.sub(r"[^\w\s]", "", title)
    # title = title.strip()
    # print(title)