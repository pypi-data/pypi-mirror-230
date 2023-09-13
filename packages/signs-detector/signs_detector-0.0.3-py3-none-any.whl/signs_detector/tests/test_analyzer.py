import unittest
from components.analyzer import SignDeviationAnalyzer

#TODO: Add tests
class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SignDeviationAnalyzer()
        
    def test_preprocess(self, image: NDArray) -> NDArray:
        pass
    
    def test_set_mask(self, mask):
        pass
        
    def test_predict(self, preprocessed: NDArray) -> NDArray:
        pass

    def test_postprocess(self, predictions, img_res, net_res=[1920,1088]) -> list:
        pass

    def test_to_bbox(self, points) -> tuple[tuple[int, int], tuple[int, int]]:
        pass

    def test_analyze(self, query_image: NDArray) -> tuple:
        pass

    def test_analyze_zone(self, reference_bbox, bboxes) -> tuple:
        pass

    def test_get_nearest_detection_score(self, ref_box, candidates) -> tuple:
        pass

    def test_raw_box(self, bbox, size) -> NDArray:
        pass