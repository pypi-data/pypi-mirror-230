"""If get_box_location returns multiple boxes, check if they are close enough so the first box can still be returned"""
import collections
from tabnanny import check
Box = collections.namedtuple('Box', 'left top width height')

from src.aai_engine_package.engine import check_boxes_list

test0 = [Box(10,9,50,50),Box(11,10,50,50),Box(10,15,50,50),Box(10,10,50,50),Box(10,6,50,50),Box(10,14,50,50),Box(9,10,50,50),Box(9,10,50,50)]

test1 = [Box(10,10,50,50),Box(10,10,51,50)]

test2 = [Box(10,10,50,50),Box(10,10,50,49)]

test3 = [Box(12,10,50,50),Box(10,9,50,50),Box(10,10,50,50)]

test4 = [Box(500,0,50,50),Box(10,9,50,50),Box(10,10,50,50)]

test5 = [Box(11,0,50,50),Box(15,9,50,50),Box(5,4,50,50)]

test6 = [Box(10,10,50,50),Box(15,5,50,50)]

test7 = [Box(10,10,50,50),Box(12,10,50,50),Box(10,11,50,50),Box(10,8,50,50)]

test8 = [Box(10,10,50,50),Box(5,16,50,50)]


def test_multiple_boxes():
    """Unit test for check_boxes_list
    """
    # Case: too many boxes
    result = check_boxes_list(test0)
    assert result is None

    # Case: not same width
    result = check_boxes_list(test1)
    assert result is None

    # Case: not same height
    result = check_boxes_list(test2)
    assert result is None

    # Good case
    result = check_boxes_list(test3)
    assert result == test3[0]

    # Outlier box
    result = check_boxes_list(test4)
    assert result is None

    # Too different
    result = check_boxes_list(test5)
    assert result is None

    # Good case
    result = check_boxes_list(test6)
    assert result == test6[0]

    # Good case
    result = check_boxes_list(test7)
    assert result == test7[0]

    # Too different
    result = check_boxes_list(test8)
    assert result is None

if __name__ == '__main__':
    test_multiple_boxes()
