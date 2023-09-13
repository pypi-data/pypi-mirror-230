from abstract.image_processor import AbstractImageProcessor
import cv2
import numpy as np
from numpy.typing import NDArray
import _config.config as config


class ImageProcessor(AbstractImageProcessor):
    
    def __init__(self): #image
        pass

    @staticmethod
    def adjust_color_size(img: NDArray, net_res=config.NET_RES):
        adj_color = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        adj_color_size = cv2.resize(adj_color, net_res, interpolation=cv2.INTER_NEAREST)
        return adj_color_size

    @staticmethod
    def normalize(img: NDArray):
        batch = np.array(img, dtype=np.float32)[np.newaxis]
        batch /= 255.0 
        return batch.transpose(0, 3, 1, 2) 

    def preprocess(self, img: NDArray):
        adjusted = self.adjust_color_size(img)
        return self.normalize(adjusted)

    def postprocess(self, predictions, img_res, net_res=config.NET_RES):
        w_ratio = img_res[0] / net_res[0]
        h_ratio = img_res[1] / net_res[1]

        box_scaling_factor = np.array([w_ratio, h_ratio, w_ratio, h_ratio])
        results = [self.select_best_result(out, box_scaling_factor) for out in predictions]
        
        return results

    @staticmethod
    def draw_bboxes(bboxes, images):
        for img_bboxes, img in zip(bboxes, images):
            for bbox in img_bboxes:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,0), thickness=2)  
                
    @staticmethod          
    def select_best_result(yolov5_out, box_scaling_factor, score_thresh=config.SCORE_TRESH, nms_iou_thresh=config.NMS_IO_TREASH):
        bboxes = yolov5_out[:, :4]
        bboxes[:, :2] = bboxes[:, :2] - bboxes[:, 2:4] / 2
        obj_scores = yolov5_out[:, 4]
        #class_scores = yolov5_out[:, 5:] # delete
        kept_idx = cv2.dnn.NMSBoxes(bboxes, obj_scores, score_thresh, nms_iou_thresh)

        bboxes = bboxes[kept_idx]
        bboxes[:, 2:4] = bboxes[:, :2] + bboxes[:, 2:4]
        postprocessed_bboxes = (bboxes * box_scaling_factor).astype(np.int64)
        return postprocessed_bboxes