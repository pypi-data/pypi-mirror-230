import cv2
import numpy as np
from ..utils import sigmoid
from ..utils import BaseEngine


def preprocess(image, input_size, mean, std, swap=(2, 0, 1)):
    resized_img = cv2.resize(image, (input_size[1], input_size[0]), interpolation=cv2.INTER_LINEAR)
    resized_img = resized_img[:, :, ::-1].astype(np.float32)
    resized_img /= 255.0
    if mean is not None:
        resized_img -= np.array(mean)
    if std is not None:
        resized_img /= np.array(std)
    resized_img = resized_img.transpose(swap)
    resized_img = np.ascontiguousarray(resized_img, dtype=np.float32)
    return resized_img


class SegmentTrtPredictor(BaseEngine):
    def __init__(self, trt_file, image_size=(640, 640)):
        super(SegmentTrtPredictor, self).__init__(trt_file)
        self.image_size = image_size  # (h, w)
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def predict(self, origin_img, class_names: list):
        n_classes = len(class_names)
        h, w = origin_img.shape[:2]
        img = preprocess(origin_img, self.image_size, self.mean, self.std)
        data = self.infer(img)[0]   # fix 1 -> 0

        pred = np.reshape(data, (-1, n_classes, self.image_size[0], self.image_size[1]))
        pred = sigmoid(pred[0, 0])
        pred = np.asarray(pred * 255).astype(np.uint8)

        pred = cv2.resize(pred, (w, h), interpolation=cv2.INTER_LINEAR)
        return pred
