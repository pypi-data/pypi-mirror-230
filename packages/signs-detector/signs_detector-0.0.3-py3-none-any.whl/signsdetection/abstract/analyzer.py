from abc import ABC, abstractmethod, abstractstaticmethod
from numpy.typing import NDArray

class AbstractSignDeviationAnalyzer(ABC):
    
    def __init__(self, onnx_model_path) -> None:
        ...
    
    @abstractmethod
    def preprocess(self, image: NDArray):
        raise NotImplementedError
    
    def mask(self):
        raise NotImplementedError
            
    @abstractmethod
    def predict(self, preprocessed: NDArray):
        raise NotImplementedError

    @abstractstaticmethod
    def postprocess(self, predictions, img_res, net_res=[1920, 1088]):
        raise NotImplementedError

    @abstractstaticmethod
    def to_bbox(self, points) -> tuple[tuple[int, int], tuple[int, int]]:
        raise NotImplementedError

    @abstractmethod
    def analyze(self, query_image: NDArray):
        raise NotImplementedError

    @abstractmethod
    def analyze_zone(self, reference_bbox, bboxes):
        raise NotImplementedError

    @abstractstaticmethod
    def get_nearest_detection_score(self, ref_box, candidates):
        raise NotImplementedError

    @abstractstaticmethod
    def draw_box(self, bbox, size):
        raise NotImplementedError       
    

