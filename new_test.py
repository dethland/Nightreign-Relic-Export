import pytesseract
from PIL import Image
import pandas as pd

# Load your image
image = Image.open(r'C:\Users\jason\Desktop\side\elden ring nightreign relic export\screen_shot_temp\screenshot_1.png')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Get OCR results with bounding box data
data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)

# Remove empty rows
data = data[data.text.notnull()]

# Define row boundaries (top and bottom Y values of each region)
# Format: [(y_start, y_end), ...] — list of known row regions
row_regions = [
    (0, 30),    # Row 1: from y=0 to y=50
    (31, 99),  # Row 2
    (101, 160), # Row 3
    (161, 220)
]

# Assign each word to a row based on its 'top' Y coordinate
def assign_row(y):
    for i, (start, end) in enumerate(row_regions):
        if start <= y <= end:
            return i
    return -1  # or None, for items not in any region

data['row'] = data['top'].apply(assign_row)
data = data[data['row'] != -1]  # Keep only words assigned to a row

# Group words by row and sort by X (left position)
grouped_rows = data.groupby('row')

for row_index, group in grouped_rows:
    # Sort words left to right
    sorted_group = group.sort_values(by='left')
    line = ' '.join(sorted_group['text'])
    print(f"Row {row_index + 1}: {line}")

