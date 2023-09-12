import numpy as np
from scipy import optimize
from skimage import draw
import cv2 

def crop_img(img, crop):
    # crop is: ymin, ymax, xmin, xmax
    ymin, ymax, xmin, xmax = crop
    img = img[ymin:ymax, xmin:xmax, :]
    y, x, _ = img.shape
    delta = x - y
    if delta > 0:
        _padding = [(abs(delta), 0), (0, 0), (0, 0)]
        img = np.pad(img, _padding)
    elif delta < 0:
        _padding = [(0, 0), (abs(delta), 0), (0, 0)]
        img = np.pad(img, _padding)

    return img

class Cropper:
    def __init__(self):
        pass

    def __call__(self, img, crop=None, scale=None, scale_method=cv2.INTER_AREA):
        """
        img: numpy array of image
        crop: [y_min, y_max, x_min, x_max]
        scale: [width, height]
        """

        if crop is not None:
            img = crop_img(img, crop)
        else:
            raise Exception("Automatic crop detection not implemented yet")

        if scale is not None:
            img = cv2.resize(img, dsize=scale, interpolation=scale_method)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return np.array(img)
