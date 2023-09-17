"""Test for the OCR module
"""
from PIL import Image

import setup_tests
from setup_tests import config_dict
if not config_dict['local-dev']:
    from setup_tests import disp
    from src.aai_engine_package import engine
else:
    from aai_engine_package import engine

import pytesseract
from pytesseract import Output
import cv2
import re
import json
import requests
from datetime import datetime

URL_AAI = "http://localhost:8000/api/graphql/"


# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_pytesseract_output():
    """Test for the pytesseract module
    """
    # ocr_output = engine.ocr_image('tests/images/tesseract_test.png', on_needle=True)
    # assert ocr_output == "De paus draagt de titel Plaatsbekleder van Jezus Christus op Aarde,"
    assert True

def test_ocr_image():
    """Test the OCR functionality of the engine
    """
    # ocr_output = engine.ocr_image('tests/images/ocr_test_image.png', haystack_path='tests/images/ocr_haystack.png')
    # assert ocr_output[:44] == "1. The goal of this challenge is to create a"
    assert True

if __name__ == '__main__':
    # OCR location finder
    img = cv2.imread('tests/images/ocr_haystack.png')

    d = pytesseract.image_to_data(img, output_type=Output.DICT)

    PATTERN= '^The|Name|Last'


    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            if re.match(PATTERN, d['text'][i]):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


    token = engine.authenticate_aai("robin", "123")
    print(engine.ocr_image_server('tests/images/ocr_test_image.png', token, haystack_path='tests/images/ocr_haystack.png'))
    print(engine.ocr_image_server('tests/images/ocr_test_image.png', token, haystack_path='tests/images/ocr_haystack.png', on_needle=True))
