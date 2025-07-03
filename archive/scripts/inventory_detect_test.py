from PIL import Image, ImageDraw
import numpy as np
import os

# Define threshold value (0-255)
THRESHOLD = 75

# Open the image
image = Image.open(r'C:\Users\jason\Desktop\side\elden ring nightreign relic export\screen_shot_temp\screenshot_9.png')

# Convert to grayscale
gray_image = image.convert('L')

# Convert to numpy array
gray_array = np.array(gray_image)

# Polarize the image using the threshold
polarized_array = np.where(gray_array > THRESHOLD, 255, 0).astype(np.uint8)

# Convert back to PIL Image (grayscale)
polarized_image = Image.fromarray(polarized_array)

# Convert to RGB so colored drawing is visible
polarized_image_rgb = polarized_image.convert('RGB')

# Parameters for the grid
# All values below are margins (0.0 - 1.0), relative to image size
inventory_rect_width_margin = 0.1
rect_height_margin = 0.17
offset_x_margin = 0.024
offset_y_margin = 0.028
start_x_margin = 0.01
start_y_margin = 0.02
cols = 8
rows = 5

def draw_grid_on_image(
    polarized_image_rgb,
    polarized_array,
    rect_width_margin, rect_height_margin,
    offset_x_margin, offset_y_margin,
    start_x_margin, start_y_margin,
    cols, rows
):
    """
    Draws a grid of rectangles on the given image, coloring each rectangle based on the pixel values in the corresponding region of the polarized array.
    Margins are relative (0.0 - 1.0) of image size.
    """
    img_w, img_h = polarized_image_rgb.size

    rect_width = int(rect_width_margin * img_w)
    rect_height = int(rect_height_margin * img_h)
    offset_x = int(offset_x_margin * img_w)
    offset_y = int(offset_y_margin * img_h)
    start_x = int(start_x_margin * img_w)
    start_y = int(start_y_margin * img_h)

    draw = ImageDraw.Draw(polarized_image_rgb)
    for row in range(rows):
        for col in range(cols):
            x1 = start_x + col * (rect_width + offset_x)
            y1 = start_y + row * (rect_height + offset_y)
            x2 = x1 + rect_width
            y2 = y1 + rect_height

            # Extract the region from the polarized array
            region = polarized_array[y1:y2, x1:x2]
            # Create a mask that is True only on the frame (border) of the region
            frame_mask = get_frame_mask(region)
            frame_pixels = region[frame_mask]
            frame_pixel_count = np.sum(frame_pixels == 255)
            white_pixel_count = np.sum(region == 255)
            if frame_pixel_count > 50:
                color = "blue"
            elif white_pixel_count > 0 and frame_pixel_count < 50:
                color = "green"
            else:
                color = "red"
            draw.rectangle([x1, y1, x2, y2], outline=color, width=1)


def get_frame_mask(region):
    frame_mask = np.zeros_like(region, dtype=bool)
    frame_mask[[0, -1], :] = True
    frame_mask[:, [0, -1]] = True
    return frame_mask

if __name__ == "__main__":
    # draw_grid_on_image(
    #     polarized_image_rgb,
    #     polarized_array,
    #     inventory_rect_width_margin, rect_height_margin,
    #     offset_x_margin, offset_y_margin,
    #     start_x_margin, start_y_margin,
    #     cols, rows
    # )
    gray_image.save('your_image_grayscale.png')
    # Save the polarized image with the debug square
    polarized_image_rgb.save('your_image_polarized.png')

    # Print shape to verify
    print(polarized_array.shape)
    # Use Microsoft Photos to open the image for debugging (Windows only)
    os.startfile('your_image_polarized.png')