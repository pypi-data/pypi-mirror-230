import time
import cv2
import numpy as np
from ..model_zoo import DetectionTrtPredictor


class ObjectDetectionTrt:
    def __init__(self,
                 trt_file="models/yolov7.trt",
                 input_shape=(640, 640),
                 conf=0.01,
                 iou=0.45,
                 end2end=False):
        self.conf = conf
        self.iou = iou
        self.end2end = end2end
        self.model = DetectionTrtPredictor(trt_file=trt_file, image_size=input_shape)

    def predict(self, image, class_names, use_preprocess=False):
        return self.model.predict(image, class_names, use_preprocess, self.conf, self.iou, self.end2end)

    @staticmethod
    def show(image, results):
        if results is None or len(results) == 0:
            return image
        index = 1
        for (box, score) in zip(list(results[:, :-2].astype(int)), list(results[:, -2])):
            cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (255, 0, 255), 2)
            cv2.putText(image, 'id: %d, score: %.2f' % (index, score),
                        (box[0], box[1] - 4), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=2)
            index += 1
        return image

    def predict_video(self, file_path=0, class_names=['person'], show=False):
        capture = cv2.VideoCapture(file_path)
        if capture.isOpened():
            if show:
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            frame_id = 0
            while True:
                read_code, frame = capture.read()
                if not read_code: break
                s = time.time()
                results = self.predict(frame, class_names)
                print("object nums: ", frame_id, len(results) if results is not None else 0, time.time() - s)
                frame = self.show(frame, results)
                if show:
                    cv2.imshow("object_detect", frame)
                    if cv2.waitKey(1) == ord('q'):
                        break
                else:
                    cv2.imwrite('images/' + str(frame_id) + '.jpg', frame)
                frame_id += 1
            capture.release()
            if show: cv2.destroyWindow("object_detect")
