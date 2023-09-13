from abc import ABC, abstractmethod, abstractstaticmethod


class AbstractImageProcessor(ABC):
    
    def __init__(self): #image
        pass

    @abstractstaticmethod
    def adjust_color_size(self, img, net_res=[1920, 1088]): #TODO: Typing, doc
        raise NotImplementedError

    @abstractstaticmethod
    def normalize(self, img):#TODO: Typing, doc
        raise NotImplementedError
    
    @abstractstaticmethod
    def preprocess(img):
        raise NotImplementedError
    
    @abstractmethod
    def postprocess(self, predictions, img_res, net_res=[1920, 1088]):
        raise NotImplementedError

    @abstractstaticmethod
    def draw_bboxes(self, bboxes, images):
        raise NotImplementedError   

    @abstractstaticmethod
    def select_best_result(self, yolov5_out, box_scaling_factor, score_thresh=0.25, nms_iou_thresh=0.45):
        raise NotImplementedError