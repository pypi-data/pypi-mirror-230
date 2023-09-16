import cv2
import numpy as np
from PIL import Image
import io


def decode_image(image_bytes: bytes):
    return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_ANYCOLOR)


def preprocess_image(image):
    image = cv2.Canny(image, 100, 200)
    return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)


def slide_match(background_bytes: bytes,target_bytes: bytes):
    try:
        target, _, _ = get_target(target_bytes)
        target = cv2.cvtColor(np.asarray(target), cv2.IMREAD_ANYCOLOR)
    except Exception:
        target = decode_image(target_bytes)

    background = decode_image(background_bytes)
    target = preprocess_image(target)
    background = preprocess_image(background)

    res = cv2.matchTemplate(background, target, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)

    h, w = target.shape[:2]
    bottom_right = (max_loc[0] + w, max_loc[1] + h)

    return {
        "target": [int(max_loc[0]), int(max_loc[1]), int(bottom_right[0]), int(bottom_right[1])]
    }


def get_target(img_bytes: bytes):
    image = Image.open(io.BytesIO(img_bytes))
    w, h = image.size
    start_x, start_y, end_x, end_y = 0, 0, 0, 0

    if image.mode == "RGBA":
        check_transparency = lambda pixel: pixel[-1] == 0
    else:
        check_transparency = lambda pixel: False

    for x in range(w):
        for y in range(h):
            pixel = image.getpixel((x, y))

            if check_transparency(pixel):
                if start_y and not end_y:
                    end_y = y
                if start_x and not end_x:
                    end_x = x
            else:
                if not start_y or y < start_y:
                    start_y = y
                    end_y = 0

        if not start_x and start_y:
            start_x = x
        if end_y:
            break

    return image.crop((start_x, start_y, end_x, end_y)), start_x, start_y
