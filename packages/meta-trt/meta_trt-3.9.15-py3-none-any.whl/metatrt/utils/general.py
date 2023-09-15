import cv2
import numpy as np

_COLORS = np.array(
    [
        0.000, 0.447, 0.741,
        0.850, 0.325, 0.098,
        0.929, 0.694, 0.125,
        0.494, 0.184, 0.556,
        0.466, 0.674, 0.188,
        0.301, 0.745, 0.933,
        0.635, 0.078, 0.184,
        0.300, 0.300, 0.300,
        0.600, 0.600, 0.600,
        1.000, 0.000, 0.000,
        1.000, 0.500, 0.000,
        0.749, 0.749, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 1.000,
        0.667, 0.000, 1.000,
        0.333, 0.333, 0.000,
        0.333, 0.667, 0.000,
        0.333, 1.000, 0.000,
        0.667, 0.333, 0.000,
        0.667, 0.667, 0.000,
        0.667, 1.000, 0.000,
        1.000, 0.333, 0.000,
        1.000, 0.667, 0.000,
        1.000, 1.000, 0.000,
        0.000, 0.333, 0.500,
        0.000, 0.667, 0.500,
        0.000, 1.000, 0.500,
        0.333, 0.000, 0.500,
        0.333, 0.333, 0.500,
        0.333, 0.667, 0.500,
        0.333, 1.000, 0.500,
        0.667, 0.000, 0.500,
        0.667, 0.333, 0.500,
        0.667, 0.667, 0.500,
        0.667, 1.000, 0.500,
        1.000, 0.000, 0.500,
        1.000, 0.333, 0.500,
        1.000, 0.667, 0.500,
        1.000, 1.000, 0.500,
        0.000, 0.333, 1.000,
        0.000, 0.667, 1.000,
        0.000, 1.000, 1.000,
        0.333, 0.000, 1.000,
        0.333, 0.333, 1.000,
        0.333, 0.667, 1.000,
        0.333, 1.000, 1.000,
        0.667, 0.000, 1.000,
        0.667, 0.333, 1.000,
        0.667, 0.667, 1.000,
        0.667, 1.000, 1.000,
        1.000, 0.000, 1.000,
        1.000, 0.333, 1.000,
        1.000, 0.667, 1.000,
        0.333, 0.000, 0.000,
        0.500, 0.000, 0.000,
        0.667, 0.000, 0.000,
        0.833, 0.000, 0.000,
        1.000, 0.000, 0.000,
        0.000, 0.167, 0.000,
        0.000, 0.333, 0.000,
        0.000, 0.500, 0.000,
        0.000, 0.667, 0.000,
        0.000, 0.833, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 0.167,
        0.000, 0.000, 0.333,
        0.000, 0.000, 0.500,
        0.000, 0.000, 0.667,
        0.000, 0.000, 0.833,
        0.000, 0.000, 1.000,
        0.000, 0.000, 0.000,
        0.143, 0.143, 0.143,
        0.286, 0.286, 0.286,
        0.429, 0.429, 0.429,
        0.571, 0.571, 0.571,
        0.714, 0.714, 0.714,
        0.857, 0.857, 0.857,
        0.000, 0.447, 0.741,
        0.314, 0.717, 0.741,
        0.50, 0.5, 0
    ]
).astype(np.float32).reshape(-1, 3)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)


def _force_forder(x):
    """
    Converts arrays x to fortran order. Returns
    a tuple in the form (x, is_transposed).
    """
    if x.flags.c_contiguous:
        return x.T, True
    else:
        return x, False


def fast_dot(A, B):
    """
    Uses blas libraries directly to perform dot product
    """
    from scipy import linalg

    a, trans_a = _force_forder(A)
    b, trans_b = _force_forder(B)
    gemm_dot = linalg.get_blas_funcs("gemm", arrays=(a, b))

    # gemm is implemented to compute: C = alpha * AB  + beta * C
    return gemm_dot(alpha=1.0, a=a, b=b, trans_a=trans_a, trans_b=trans_b)


def nms(boxes, scores, nms_thr):
    """Single class NMS implemented in Numpy."""
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= nms_thr)[0]
        order = order[inds + 1]

    return keep


def singleclass_nms(boxes, scores, nms_thr, score_thr, predictions=None, v8=False):
    """Multiclass NMS implemented in Numpy"""
    num_classes = scores.shape[1]
    mi = (4 if v8 else 5) + num_classes  # mask start index

    cls_scores = np.max(scores, axis=1)
    cls_indexes = np.argmax(scores, axis=1)
    valid_score_mask = cls_scores > score_thr
    if valid_score_mask.sum() == 0:
        return None
    else:
        valid_indexes = cls_indexes[valid_score_mask]
        valid_scores = cls_scores[valid_score_mask]
        valid_boxes = boxes[valid_score_mask]
        valid_predictions = predictions[valid_score_mask]
        keep = nms(valid_boxes, valid_scores, nms_thr)
        if len(keep) > 0:
            if predictions is None:
                dets = np.concatenate([valid_boxes[keep], valid_scores[keep, None], valid_indexes[keep]], 1)
            else:
                if not v8: valid_predictions[:, mi:] *= valid_predictions[:, 4:5]
                dets = np.concatenate(
                    [valid_boxes[keep], valid_scores[keep, None], valid_indexes[keep, None],
                     valid_predictions[keep, mi:]], 1)

    if len(dets) == 0:
        return None
    return dets


def multiclass_nms(boxes, scores, nms_thr, score_thr, predictions=None):
    """Multiclass NMS implemented in Numpy"""
    final_dets = []
    num_classes = scores.shape[1]
    mi = 5 + num_classes  # mask start index
    for cls_ind in range(num_classes):
        cls_scores = scores[:, cls_ind]
        valid_score_mask = cls_scores > score_thr
        if valid_score_mask.sum() == 0:
            continue
        else:
            valid_scores = cls_scores[valid_score_mask]
            valid_boxes = boxes[valid_score_mask]
            valid_predictions = predictions[valid_score_mask]
            keep = nms(valid_boxes, valid_scores, nms_thr)
            if len(keep) > 0:
                cls_inds = np.ones((len(keep), 1)) * cls_ind
                if predictions is None:
                    dets = np.concatenate([valid_boxes[keep], valid_scores[keep, None], cls_inds], 1)
                else:
                    valid_predictions[:, mi:] *= valid_predictions[:, 4:5]
                    dets = np.concatenate(
                        [valid_boxes[keep], valid_scores[keep, None], cls_inds, valid_predictions[keep, mi:]], 1)
                final_dets.append(dets)
    if len(final_dets) == 0:
        return None
    return np.concatenate(final_dets, 0)


def preproc(image, input_size, mean, std, swap=(2, 0, 1)):
    img = np.array(image)
    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])

    if img.shape[:2] == input_size:
        padded_img = img.astype(np.float32)
    else:
        # 传入图像默认为RGB
        if len(image.shape) == 3:
            padded_img = np.ones((input_size[0], input_size[1], 3)) * 114.0
        else:
            padded_img = np.ones(input_size) * 114.0
        resized_img = cv2.resize(
            img,
            (int(round(img.shape[1] * r)), int(round(img.shape[0] * r))),
            interpolation=cv2.INTER_LINEAR,
        ).astype(np.float32)
        padded_img[: int(round(img.shape[0] * r)), : int(round(img.shape[1] * r))] = resized_img
    padded_img /= 255.0
    if mean is not None:
        padded_img -= mean
    if std is not None:
        padded_img /= std
    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r


def preproc2(image, input_size, mean, std, swap=(2, 0, 1)):
    if len(image.shape) == 3:
        padded_img = np.ones((input_size[0], input_size[1], 3)) * 114.0
    else:
        padded_img = np.ones(input_size) * 114.0
    img = np.array(image)
    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    new_unpad = int(round(img.shape[1] * r)), int(round(img.shape[0] * r))
    dw, dh = input_size[1] - new_unpad[0], input_size[0] - new_unpad[1]
    dw /= 2
    dh /= 2
    resized_img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR).astype(np.float32)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    padded_img[top: input_size[1] - bottom, left: input_size[0] - right] = resized_img

    padded_img = padded_img[:, :, ::-1]
    padded_img /= 255.0
    if mean is not None:
        padded_img -= mean
    if std is not None:
        padded_img /= std
    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r


def preprocess(image, input_size, mean, std, swap=(2, 0, 1)):
    imh, imw = image.shape[:2]
    m = min(imh, imw)  # min dimension
    top, left = (imh - m) // 2, (imw - m) // 2
    padded_img = cv2.resize(image[top:top + m, left:left + m], input_size, interpolation=cv2.INTER_LINEAR)
    padded_img = padded_img[:, :, ::-1].astype(np.float32)
    padded_img /= 255.0
    if mean is not None:
        padded_img -= np.array(mean)
    if std is not None:
        padded_img /= np.array(std)
    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img


def vis(img, boxes, scores, cls_ids, conf=0.5, class_names=None):
    for i in range(len(boxes)):
        box = boxes[i]
        cls_id = int(cls_ids[i])
        score = scores[i]
        if score < conf:
            continue
        x0 = int(box[0])
        y0 = int(box[1])
        x1 = int(box[2])
        y1 = int(box[3])

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()
        text = '{}:{:.1f}%'.format(class_names[cls_id], score * 100)
        txt_color = (0, 0, 0) if np.mean(_COLORS[cls_id]) > 0.5 else (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        txt_size = cv2.getTextSize(text, font, 0.4, 1)[0]
        cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)

        txt_bk_color = (_COLORS[cls_id] * 255 * 0.7).astype(np.uint8).tolist()
        cv2.rectangle(
            img,
            (x0, y0 + 1),
            (x0 + txt_size[0] + 1, y0 + int(1.5 * txt_size[1])),
            txt_bk_color,
            -1
        )
        cv2.putText(img, text, (x0, y0 + txt_size[1]), font, 0.4, txt_color, thickness=1)

    return img
