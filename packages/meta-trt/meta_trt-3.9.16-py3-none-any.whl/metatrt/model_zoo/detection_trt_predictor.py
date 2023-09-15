import numpy as np
from ..utils import preproc, multiclass_nms
from ..utils import BaseEngine


class DetectionTrtPredictor(BaseEngine):
    def __init__(self, trt_file, image_size=(640, 640)):
        super(DetectionTrtPredictor, self).__init__(trt_file)
        self.image_size = image_size  # (h, w)
        # self.mean = [0.485, 0.456, 0.406]
        # self.std = [0.229, 0.224, 0.225]

    def predict(self, origin_img, class_names, use_preprocess, conf, iou, end2end=False):
        n_classes = len(class_names)
        img, ratio = preproc(origin_img, self.image_size, self.mean, self.std) if use_preprocess else (origin_img, 1.0)
        data = self.infer(img)
        if end2end:
            num, final_boxes, final_scores, final_cls_inds = data
            final_boxes = np.reshape(final_boxes / ratio, (-1, 4))
            dets = np.concatenate([final_boxes[:num[0]], np.array(final_scores)[:num[0]].reshape(-1, 1),
                                   np.array(final_cls_inds)[:num[0]].reshape(-1, 1)], axis=-1)
        else:
            predictions = np.reshape(data, (1, -1, int(5 + n_classes)))[0]
            dets = self.postprocess(predictions, ratio, conf, iou)

        return dets

    @staticmethod
    def postprocess(predictions, ratio, score_thr, nms_thr):
        boxes = predictions[:, :4]
        scores = predictions[:, 4:5] * predictions[:, 5:6]
        boxes_xyxy = np.ones_like(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
        boxes_xyxy /= ratio
        dets = multiclass_nms(boxes_xyxy, scores, nms_thr=nms_thr, score_thr=score_thr)
        return dets
