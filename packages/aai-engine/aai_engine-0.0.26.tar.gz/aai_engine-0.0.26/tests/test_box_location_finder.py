"""Test the dynamic box location finder"""
from PIL.PngImagePlugin import PngImageFile, PngInfo

import collections
Box = collections.namedtuple('Box', 'left top width height')

import setup_tests

from datetime import datetime

from src.aai_engine_package.engine import get_box_location


def test_box_location_finder():
    """Tests the get_box_location function
    """
    haystack_image = PngImageFile("tests/images/dynamic_finder_haystack.png")
    haystack_image_fake = PngImageFile("tests/images/dynamic_finder_fake_haystack.png")
    needle_img_location = "tests/images/dynamic_finder_needle.png"

    # Test low amount of steps
    start1 = datetime.now()
    box = get_box_location(needle_img_location,haystack=haystack_image,steps_per_iteration=2,cache_confidence=False)
    stop1 = datetime.now()
    print(f"First call: {stop1 - start1}")
    assert box
    assert not isinstance(box,list)
    assert box == Box(left=584, top=404, width=82, height=42)

    # Steps very high amount of steps for upper bound setting
    start2 = datetime.now()
    box = get_box_location(needle_img_location,haystack=haystack_image,steps_per_iteration=100000000,cache_confidence=False)
    stop2 = datetime.now()
    print(f"Second call: {stop2 - start2}")
    assert box
    assert not isinstance(box,list)
    assert box == Box(left=584, top=404, width=82, height=42)

    # Test normal use
    start3 = datetime.now()
    box = get_box_location(needle_img_location,haystack=haystack_image,steps_per_iteration=4,cache_confidence=False)
    stop3 = datetime.now()
    print(f"Third call: {stop3 - start3}")
    assert box
    assert not isinstance(box,list)
    assert box == Box(left=584, top=404, width=82, height=42)

    # Test unfindable needle
    start4 = datetime.now()
    box = get_box_location(needle_img_location,haystack=haystack_image_fake,steps_per_iteration=4,cache_confidence=False)
    stop4 = datetime.now()
    print(f"Fourth call: {stop4 - start4}")
    assert not box

def test_cache_confidence():
    """Tests if the confidence gets cached correctly
    """
    haystack_image = PngImageFile("tests/images/dynamic_finder_haystack.png")
    cache_confidence_img_path = "tests/images/get_box_cache_confidence.png"
    cache_confidence_img = PngImageFile("tests/images/get_box_cache_confidence.png")

    start5 = datetime.now()
    box1 = get_box_location(cache_confidence_img_path,haystack=haystack_image, steps_per_iteration=4)
    stop5 = datetime.now()
    print(f"Box1: {box1}")
    print(f"NOT cached found  in {stop5 - start5}")

    cache_confidence_img = PngImageFile("tests/images/get_box_cache_confidence.png")
    assert cache_confidence_img.text['cached_confidence']
    print(f"Cached confidence value: {cache_confidence_img.text['cached_confidence']}")

    start6 = datetime.now()
    box2 = get_box_location(cache_confidence_img_path,haystack=haystack_image,steps_per_iteration=4)
    stop6 = datetime.now()
    print(f"Box2: {box2}")
    print(f"Cached found in {stop6 - start6}")
    assert box2
    assert box2 == box1

    # Cleanup
    info = PngInfo()
    for key,value in cache_confidence_img.text.items():
        if key != 'cached_confidence':
            info.add_text(key,value)
    cache_confidence_img.save(cache_confidence_img_path,pnginfo=info)

if __name__ == "__main__":
    test_box_location_finder()
    test_cache_confidence()
