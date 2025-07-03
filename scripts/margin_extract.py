import cv2


def adjust_rect_for_aspect_ratio(original_size, new_size, margin_rect):
    """
    Adjust margin-based rect (normalized values) to fit the new image
    without visual distortion, preserving the same aspect ratio as original.

    original_size: (orig_w, orig_h)
    new_size: (new_w, new_h)
    margin_rect: (x_margin, y_margin, w_margin, h_margin) — all relative (0–1)
    """

    orig_w, orig_h = original_size
    new_w, new_h = new_size

    orig_aspect = orig_w / orig_h
    new_aspect = new_w / new_h

    x_margin, y_margin, w_margin, h_margin = margin_rect

    if new_aspect > orig_aspect:
        # New image is wider, so we need to "shrink" width proportionally
        scale = orig_h / new_h
        scale_w = (orig_w / orig_h) / (new_w / new_h)
        scale_h = 1
    else:
        # New image is taller, shrink height proportionally
        scale = orig_w / new_w
        scale_w = 1
        scale_h = (orig_h / orig_w) / (new_h / new_w)

    # Apply scaled margins
    new_x = int(x_margin * new_w * scale_w)
    new_y = int(y_margin * new_h * scale_h)
    new_w_rect = int(w_margin * new_w * scale_w)
    new_h_rect = int(h_margin * new_h * scale_h)

    return (new_x, new_y, new_w_rect, new_h_rect)


wild_card_image_filepath = "screen_shot_temp/other_img.png"
temp_image_filepath = "screen_shot_temp/nightreign_vYm4s9i1Zk.jpg"
normal_extract_filepath = 'screen_shot_temp/screenshot_testing.png'


TITLE_REGION = (0.002190580503833516, 0.0033783783783783786, 0.9014238773274917, 0.12837837837837837)  # left, top, sizex, sizey
# Original regions
STAT_1_REGION = (0.05147864184008762, 0.1858108108108108, 0.9649507119386638, 0.44932432432432434)
STAT_2_REGION = (0.04928806133625411, 0.4391891891891892, 0.963855421686747, 0.7027027027027027)
STAT_3_REGION = (0.050383351588170866, 0.7094594594594594, 0.9627601314348302, 0.9797297297297297)
# Combine all regions into a list
regions = [
    TITLE_REGION,
    STAT_1_REGION,
    STAT_2_REGION,
    STAT_3_REGION
]

progress_bar_region_tuple = (
    0.9427083333333334, 0.21203703703703702, 0.9473958333333333, 0.6574074074074074)


# Load an image
image = cv2.imread(normal_extract_filepath)
clone = image.copy()

# Draw rectangles for relic_inveotry and progress_bar
if image is not None:
    h, w = image.shape[:2]
    print("🐍 DEBUG: Loaded image with shape (h={}, w={})".format(h, w))
else:
    h, w = 1080, 1920  # Fallback values if image is None
    print("🐍 DEBUG: Image is None, using fallback shape (h=1080, w=1920)")

# # Draw rectangles for each region
# for region in regions:
#     # Use the actual image size instead of hardcoded (1080, 1920)
#     x1, y1, x2, y2 = adjust_rect_for_aspect_ratio((w, h), (w, h), region)
#     # x, y, w_rect, h_rect = adjust_rect_for_aspect_ratio((1080, 1920), (w, h), region)
#     pt1 = (x1, y1)
#     pt2 = (x2, y2)
#     cv2.rectangle(image, pt1, pt2, (255, 0, 0), 2)
#     cv2.rectangle(clone, pt1, pt2, (255, 0, 0), 2)  

for rect in [progress_bar_region_tuple]:
    adjust_rect_for_aspect_ratio((1080,1920), (h, w), rect)
    x1, y1, x2, y2 = rect
    pt1 = (int(x1 * w), int(y1 * h))
    pt2 = (int(x2 * w), int(y2 * h))
    cv2.rectangle(image, pt1, pt2, (255, 0, 0), 2)
    cv2.rectangle(clone, pt1, pt2, (255, 0, 0), 2)


# Variables for rectangle drawing
drawing = False
start_point = (-1, -1)

# Mouse callback function
rectangles = []

def draw_rectangle(event, x, y, flags, param):
    global start_point, drawing, image, rectangles

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            image = clone.copy()
            cv2.rectangle(image, start_point, (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(clone, start_point, (x, y), (0, 255, 0), 2)
        image = clone.copy()
        h, w = image.shape[:2]
        x1, y1 = start_point
        x2, y2 = x, y
        margin_rect = (
            x1 / w, y1 / h,
            x2 / w, y2 / h
        )
        rectangles.append(margin_rect)

# Create window and set mouse callback
cv2.namedWindow('Draw Rectangles')
cv2.setMouseCallback('Draw Rectangles', draw_rectangle)


# Main loop
while True:
    cv2.imshow('Draw Rectangles', image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print(rectangles)
        break

cv2.destroyAllWindows()
