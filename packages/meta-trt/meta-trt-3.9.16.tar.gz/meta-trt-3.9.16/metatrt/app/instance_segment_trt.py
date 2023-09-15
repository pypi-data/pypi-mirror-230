import time
import cv2
from ..model_zoo import InstanceTrtPredictor


class InstanceSegmentTrt:
    def __init__(self,
                 trt_file="models/yolov7-seg.trt",
                 input_shape=(640, 640),
                 conf=0.01,
                 iou=0.45,
                 use_mask=False,
                 use_cupy=False,
                 v8=False):
        self.conf = conf
        self.iou = iou
        self.use_mask = use_mask
        self.use_cupy = use_cupy
        self.v8 = v8
        self.model = InstanceTrtPredictor(trt_file=trt_file, image_size=input_shape)

    def predict(self, image, class_names, use_preprocess=False, output_contour=False):
        if output_contour:
            return self.model.predict_mask(image, class_names, use_preprocess, self.conf, self.iou, self.use_mask,
                                           self.use_cupy, self.v8)
        else:
            return self.model.predict(image, class_names, use_preprocess, self.conf, self.iou, self.use_mask,
                                      self.use_cupy, self.v8)[0]

    @staticmethod
    def show(image, results):
        if results is None or len(results) == 0:
            return image

        for i, result in enumerate(results):
            x1, y1, x2, y2, x3, y3, x4, y4, score, label = result
            cv2.line(image, pt1=(x1, y1), pt2=(x2, y2), color=(255, 255, 0), thickness=10)
            cv2.line(image, pt1=(x2, y2), pt2=(x3, y3), color=(255, 255, 0), thickness=10)
            cv2.line(image, pt1=(x3, y3), pt2=(x4, y4), color=(255, 255, 0), thickness=10)
            cv2.line(image, pt1=(x4, y4), pt2=(x1, y1), color=(255, 255, 0), thickness=10)
            cv2.putText(image, '%d(%.2f)' % (label, score),
                        (x1, y1 - 4), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=2)
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
