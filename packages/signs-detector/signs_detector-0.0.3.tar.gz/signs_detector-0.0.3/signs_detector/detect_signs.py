from components.analyzer import SignDeviationAnalyzer
from utils.utils import visualize, generate_mask
from numpy.typing import NDArray
from pathlib import Path

import cv2

from numpy.typing import NDArray

 

def main():   
    markup = Path('/Users/jokkojja/Desktop/invian/camera/signs_detection/data/test_bad_markup.json')
    query_image = cv2.imread('/Users/jokkojja/Desktop/invian/camera/signs_detection/data/test_image.jpeg')
    masks = generate_mask(markup, query_image.shape[:2]) 
    analyzer = SignDeviationAnalyzer()
    for i, mask in enumerate(masks):
        analyzer.set_mask(mask)
        shift_confidence, sign_mask = analyzer.analyze(query_image)
        print(f'{i}: confidence {shift_confidence}, mask {sign_mask}')
        # visualize(
        #     query_image=query_image,
        #     mask=analyzer.draw_box(mask, query_image.shape[:2]),
        #     sign_mask=sign_mask,
        #     shift_confidence=shift_confidence,
        # )

    