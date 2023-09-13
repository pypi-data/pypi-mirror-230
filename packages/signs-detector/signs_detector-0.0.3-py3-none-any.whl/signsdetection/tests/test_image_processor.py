import unittest
from components.analyzer import ImageProcessor

#TODO: Add tests
class TestImageProcessor(unittest.TestCase):
    
    def setUp(self):
        self.image_processor = ImageProcessor()
        
    def adjust_color_size(self, img, net_res=[1920,1088]): #TODO: Typing, doc
        pass

    def normalize(self, img):#TODO: Typing, doc
        pass
    
    def preprocess(img):
        pass
    
    def postprocess(self, predictions, img_res, net_res=[1920,1088]):
        pass

    def draw_bboxes(self, bboxes, images):
        pass   

    def select_best_result(self, yolov5_out, box_scaling_factor, score_thresh=0.25, nms_iou_thresh=0.45):
        pass    