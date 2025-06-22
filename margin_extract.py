import cv2
import screenshot


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



relic_inveotry = (0.48125, 0.19537037037037036, 0.9338541666666667, 0.6787037037037037)
progress_bar = (0.9427083333333334, 0.21203703703703702, 0.9473958333333333, 0.6574074074074074)
relic_info = (0.558984375, 0.7201388888888889, 0.878125, 0.8958333333333334)
sorting = (0.76796875, 0.15625, 0.835546875, 0.18055555555555555)

# Load an image
image = cv2.imread('screen_shot_temp/screenshot_testing.png')
clone = image.copy()

# Draw rectangles for relic_inveotry and progress_bar
if image is not None:
    h, w = image.shape[:2]
else:
    h, w = 1080, 1920  # Fallback values if image is None
if image is not None:
    h, w = image.shape[:2]

for rect in [relic_inveotry, progress_bar]:
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
