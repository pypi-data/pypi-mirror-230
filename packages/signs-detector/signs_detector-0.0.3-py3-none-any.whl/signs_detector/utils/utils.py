import numpy as np
import cv2
from numpy.typing import NDArray
import json
from pathlib import Path
from typing import Optional

def select_best_result(yolov5_out, box_scaling_factor, score_thresh=0.25, nms_iou_thresh=0.45):
    bboxes = yolov5_out[:, :4]
    bboxes[:, :2] = bboxes[:, :2] - bboxes[:, 2:4] / 2
    obj_scores = yolov5_out[:, 4]
    class_scores = yolov5_out[:, 5:]
    kept_idx = cv2.dnn.NMSBoxes(bboxes, obj_scores, score_thresh, nms_iou_thresh)

    bboxes = bboxes[kept_idx]
    bboxes[:, 2:4] = bboxes[:, :2] + bboxes[:, 2:4]
    postprocessed_bboxes = (bboxes * box_scaling_factor).astype(np.int64)
    return postprocessed_bboxes

def get_nearest_detection_score(
    self, reference_bbox: NDArray, predicted_boxes: NDArray
) -> float:
    best_iou = 0.0
    for bbox in predicted_boxes:
        iou = calculate_iou(reference_bbox, bbox)
        if iou > best_iou:
            best_iou = iou

    return 1.0 - best_iou

def calculate_iou(box1: NDArray[np.int64], box2: NDArray[np.int64]) -> float:
    """
    Calculates intersection over union (IoU) of two rectangles in xyxy format
    """
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    boxBArea = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def write_info(image: NDArray, additional_info: list[str] = []):
    height, width = image.shape[:2]

    channels = 1
    if len(image.shape) > 2:
        channels = image.shape[2]

    min_vals = np.min(image)
    max_vals = np.max(image)
    canvas = image.copy()

    full_msg = [
        f'h: {height}',
        f'w: {width}',
        f'c: {channels}',
        f'min: {min_vals}',
        f'max: {max_vals}',
    ] + additional_info

    for idx, l in enumerate(full_msg):
        canvas = cv2.putText(
            canvas,
            l,
            (10, 30 + idx * 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    return canvas

def blend(im1, im2):
    return cv2.addWeighted(im1, 0.5, im2, 0.5, 0)

def visualize(
    query_image: NDArray,
    mask: NDArray,
    sign_mask: NDArray,
    shift_confidence: float,
):

    mask = np.stack((mask,mask,mask), axis=2)
    mask *= 255
    mask = blend(query_image, mask)

    sign_mask = np.stack((sign_mask,sign_mask,sign_mask), axis=2)
    sign_mask *= 255
    sign_mask = blend(sign_mask, query_image)
    sign_mask = write_info(sign_mask, [f'confidence: {shift_confidence:.4f}'])

    full = np.column_stack((query_image, mask, sign_mask))

    cv2.imshow('visualization', full)

    cv2.waitKey(0)

    cv2.destroyAllWindows()


def generate_mask(markup: Optional[Path], shape):
    if markup is None:
        return [[0, 0, shape[1], shape[0]]]

    markup_json = json.loads(markup.read_text())

    def construct_countour(points):
        """
        points format:
        [
            {'x': x, 'y': y},
            {'x': x, 'y': y},
            ...
        ]
        """
        h, w = shape

        contour = []
        for p in points[:4]:
            contour += [p['x'] * w, p['y'] * h]
        return np.array(contour, dtype=np.int32)

    masks = []
    for _, zone_info in markup_json.items():
        points = zone_info['points']
        masks.append(
            construct_countour(points),
        )
    return masks