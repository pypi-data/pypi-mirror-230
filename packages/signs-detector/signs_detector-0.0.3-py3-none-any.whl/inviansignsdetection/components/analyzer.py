from numpy.typing import NDArray
import onnxruntime as ort
import numpy as np
import cv2
from abstract.analyzer import AbstractSignDeviationAnalyzer
from components.image_processor import ImageProcessor
from utils.utils import calculate_iou
import _config.config as config




class SignDeviationAnalyzer(AbstractSignDeviationAnalyzer):

    def __init__(
        self,
    ) -> None:
        self.onnx_model_path = config.MODEL_PATH
        self.image_processor = ImageProcessor()
        self.model = ort.InferenceSession(self.onnx_model_path)
        self.mask = None

    
    def preprocess(self, image: NDArray) -> NDArray:
        """ Preprocess image

        Args:
            image (NDArray): Query image from system

        Returns:
            NDArray: Processed image
        """
        preprocessed_image = self.image_processor.preprocess(image)
        return preprocessed_image
    
    def set_mask(self, mask) -> None:
        """ Mask setter

        Args:
            mask (_type_): _description_
        """
        self.mask = mask
        
    def predict(self, preprocessed: NDArray) -> NDArray:
        """ Predict boxes with signs

        Args:
            preprocessed (NDArray): Preprocessed image

        Returns:
            NDArray: Sign bboxes arraay
        """
        predictions =  self.model.run(None, {'images': preprocessed})[0]
        return predictions

    def postprocess(self, predictions, img_res) -> list:
        """ Preparing bboxes from predictions

        Args:
            predictions (_type_): Model predictions
            img_res (_type_): Original image

        Returns:
            list: _description_
        """
        postprocessed_image = self.image_processor.postprocess(predictions=predictions, img_res=img_res)
        return postprocessed_image

    @staticmethod
    def to_bbox(points) -> tuple[tuple[int, int], tuple[int, int]]:
        """_summary_

        Args:
            points (_type_): _description_

        Returns:
            tuple[tuple[int, int], tuple[int, int]]: _description_
        """
        x_coords = [point for idx, point in enumerate(points) if idx % 2 == 0]
        y_coords = [point for idx, point in enumerate(points) if idx % 2 == 1]

        xmin = round(min(x_coords))
        xmax = round(max(x_coords))
        ymin = round(min(y_coords))
        ymax = round(max(y_coords))

        return [xmin, ymin, xmax, ymax]


    def analyze(self, query_image: NDArray) -> tuple:
        """_summary_

        Args:
            query_image (NDArray): _description_

        Returns:
            tuple: _description_
        """
        preprocessed = self.preprocess(query_image)
        predictions = self.predict(preprocessed)
        processed = self.postprocess(
            predictions,
            query_image.shape[:2][::-1]
        )
        zone = self.to_bbox(self.mask)
        score, matched_box = self.analyze_zone(reference_bbox=zone, bboxes=processed[0])
        mask = self.draw_box(matched_box, query_image.shape[:2])
        return score, mask

    def analyze_zone(self, reference_bbox, bboxes) -> tuple:
        """_summary_

        Args:
            reference_bbox (_type_): _description_
            bboxes (_type_): _description_

        Returns:
            tuple: _description_
        """
        score, matched_box = self.get_nearest_detection_score(reference_bbox, bboxes)
        return score, matched_box

    def get_nearest_detection_score(self, ref_box, candidates) -> tuple:
        """_summary_

        Args:
            ref_box (_type_): _description_
            candidates (_type_): _description_

        Returns:
            tuple: _description_
        """
        best_iou = 0.0
        best_box = None
        for bbox in candidates:
            iou = calculate_iou(ref_box, bbox)
            if iou > best_iou:
                best_iou = iou
                best_box = bbox
        return 1.0 - best_iou, best_box

    def draw_box(self, bbox, size) -> NDArray:
        """_summary_

        Args:
            bbox (_type_): _description_
            size (_type_): _description_

        Returns:
            NDArray: _description_
        """
        mask = np.zeros(size, dtype=np.uint8)
        if bbox is None:
            return mask

        if len(bbox) > 4:
            bbox = self.to_bbox(bbox)
        return cv2.rectangle(
            mask,
            (bbox[0], bbox[1]),
            (bbox[2], bbox[3]),
            (1),
            -1
        )
    

