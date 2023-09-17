import cv2
import numpy as np
from ..utils import softmax
from ..utils import BaseEngine


def preprocess(image, input_size, mean, std, swap=(2, 0, 1)):
    # 传入图像默认为RGB
    padded_img = cv2.resize(image, input_size, interpolation=cv2.INTER_LINEAR)
    padded_img = padded_img.astype(np.float32)
    padded_img /= 255.0
    if mean is not None:
        padded_img -= np.array(mean)
    if std is not None:
        padded_img /= np.array(std)
    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img


class ClassificationTrtPredictor(BaseEngine):
    def __init__(self, trt_file, image_size=(224, 224)):
        super(ClassificationTrtPredictor, self).__init__(trt_file)
        self.image_size = image_size  # (h, w)
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def predict(self, origin_img, class_names: list, use_preprocess=False):
        if isinstance(origin_img, list):
            batch_size = len(origin_img)
            if use_preprocess:
                img = [preprocess(im, self.image_size, self.mean, self.std) for im in
                       origin_img] if use_preprocess else origin_img
            else:
                img = origin_img
        else:
            batch_size = 1
            img = preprocess(origin_img, self.image_size, self.mean, self.std) if use_preprocess else origin_img

        data = self.infer(np.array(img))[-1]
        predictions = np.reshape(data, (batch_size, -1))
        output_score = np.array([softmax(p) for p in predictions])
        output_class = np.argmax(output_score, axis=1)

        return [{'category_id': int(c),
                 'category': class_names[int(c)] if len(class_names) else str(c),
                 'score': float(s[int(c)])} for c, s in zip(output_class, output_score)]

    def feature(self, origin_img, num_classes=1000, use_preprocess=False):
        if isinstance(origin_img, list):
            batch_size = len(origin_img)
            if use_preprocess:
                img = [preprocess(im, self.image_size, self.mean, self.std) for im in
                       origin_img] if use_preprocess else origin_img
            else:
                img = origin_img
        else:
            batch_size = 1
            img = preprocess(origin_img, self.image_size, self.mean, self.std) if use_preprocess else origin_img
        data = self.infer(np.array(img))[0]
        predictions = np.reshape(data, (batch_size, -1))

        return predictions
