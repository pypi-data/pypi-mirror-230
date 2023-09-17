import numpy as np
from ..model_zoo import SegmentTrtPredictor


class SaliencySegmentTrt:
    def __init__(self,
                 trt_file="models/model-32.trt",
                 input_shape=(352, 352),
                 conf=0.01,
                 iou=0.45,
                 end2end=False):
        self.conf = conf
        self.iou = iou
        self.end2end = end2end
        self.model = SegmentTrtPredictor(trt_file=trt_file, image_size=input_shape)

    def predict(self, image, class_names):
        return self.model.predict(image, class_names)

    @staticmethod
    def show(image, mask):
        result = image * (mask[:, :, np.newaxis] / 255)
        return result.astype(np.uint8)
