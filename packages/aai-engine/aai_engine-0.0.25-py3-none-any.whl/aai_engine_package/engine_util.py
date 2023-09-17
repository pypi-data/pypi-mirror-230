"""The intention of this file is to make the implementations of the core function fully customizable"""


####################################################################################################
###----------------------------------------Imports-----------------------------------------------###
####################################################################################################
import time
import cv2
import sys
import numpy
import os
import collections
import subprocess
import errno
import functools

from datetime import datetime
from PIL import ImageGrab
try:
    from PIL import Image
    from PIL import ImageOps
    from PIL import ImageDraw
    if sys.platform == 'win32': # TODO - Pillow now supports ImageGrab on macOS.
        from PIL import ImageGrab
    _PILLOW_UNAVAILABLE = False
except ImportError:
    # We ignore this because failures due to Pillow not being installed
    # should only happen when the functions that specifically depend on
    # Pillow are called. The main use case is when PyAutoGUI imports
    # PyScreeze, but Pillow isn't installed because the user is running
    # some platform/version of Python that Pillow doesn't support, then
    # importing PyAutoGUI should not automatically fail because it
    # imports PyScreeze.
    # So we have a `pass` statement here since a failure to import
    # Pillow shouldn't crash PyScreeze.
    _PILLOW_UNAVAILABLE = True

USE_IMAGE_NOT_FOUND_EXCEPTION = False

GRAYSCALE_DEFAULT = False

LARGE_FONT = ("Courier", 12)
NORM_FONT = ("Courier", 10)
SMALL_FONT = ("Courier", 8)

REGION_PICK_VIEW = 0
OFFSET_PICK_VIEW = 1
SIMILARITY_PICK_VIEW = 2
NAME_PICK_VIEW = 3
SW_MINIMIZE = 6


Box = collections.namedtuple('Box', 'left top width height')
Point = collections.namedtuple('Point', 'x y')
RGB = collections.namedtuple('RGB', 'red green blue')

GNOME_SCREENSHOT_EXISTS = False
try:
    if sys.platform not in ('java', 'darwin', 'win32'):
        whichProc = subprocess.Popen(
            ['which', 'gnome-screenshot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GNOME_SCREENSHOT_EXISTS = whichProc.wait() == 0
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: gnome-screenshot installed: {GNOME_SCREENSHOT_EXISTS}")
except OSError as ex:
    if ex.errno == errno.ENOENT:
        # if there is no "which" program to find gnome-screenshot, then assume there
        # is no gnome-screenshot.
        pass
    else:
        raise

RUNNING_PYTHON_2 = sys.version_info[0] == 2

if not RUNNING_PYTHON_2:
    UniCode = str # On Python 3, all the isinstance(spam, (str, unicode)) calls will work the same as Python 2.
####################################################################################################
###----------------------------------------------------------------------------------------------###
####################################################################################################



####################################################################################################
###---------------------------------------Exceptions---------------------------------------------###
####################################################################################################
class PyScreezeException(Exception):
    """PyScreezeException is a generic exception class raised when a
    PyScreeze-related error happens. If a PyScreeze function raises an
    exception that isn't PyScreezeException or a subclass, assume it is
    a bug in PyScreeze."""
    pass

class ImageNotFoundException(PyScreezeException):
    """ImageNotFoundException is an exception class raised when the
    locate functions fail to locate an image. You must set
    pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION to True to enable this feature.
    Otherwise, the locate functions will return None."""
    pass
####################################################################################################
###----------------------------------------------------------------------------------------------###
####################################################################################################





####################################################################################################
###----------------------------------------Functions---------------------------------------------###
####################################################################################################
def locate_on_screen(image, min_search_time=0, **kwargs):
    """TODO - rewrite this
    minSearchTime - amount of time in seconds to repeat taking
    screenshots and trying to locate a match.  The default of 0 performs
    a single search.
    """
    start = time.time()
    while True:
        try:
            screenshot_img = screenshot(region=None) # the locateAll() function must handle cropping to return accurate coordinates, so don't pass a region here.
            ret_val = locate(image, screenshot_img, **kwargs)
            try:
                screenshot_img.fp.close()
            except AttributeError:
                # Screenshots on Windows won't have an fp since they came from
                # ImageGrab, not a file. Screenshots on Linux will have fp set
                # to None since the file has been unlinked
                pass
            if ret_val or time.time() - start > min_search_time:
                return ret_val
        except ImageNotFoundException:
            if time.time() - start > min_search_time:
                if USE_IMAGE_NOT_FOUND_EXCEPTION:
                    raise
                return None

def locate(needle_image, haystack_image, **kwargs):
    """
    TODO
    """
    # Note: The gymnastics in this function is because we want to make sure to exhaust the iterator so that the needle and haystack files are closed in locateAll.
    kwargs['limit'] = 10
    points = list(locate_all(needle_image, haystack_image, **kwargs))
    if len(points) > 1:
        return points
    if len(points) == 1:
        return points[0]
    if USE_IMAGE_NOT_FOUND_EXCEPTION:
        raise ImageNotFoundException('Could not locate the image.')
    return None

def locate_all_opencv(needle_image, haystack_image, grayscale=None, limit=10000, region=None, step=1,
                      confidence=0.999):
    """
    TODO - rewrite this
        faster but more memory-intensive than pure python
        step 2 skips every other row and column = ~3x faster but prone to miss;
            to compensate, the algorithm automatically reduces the confidence
            threshold by 5% (which helps but will not avoid all misses).
        limitations:
          - OpenCV 3.x & python 3.x not tested
          - RGBA images are treated as RBG (ignores alpha channel)
    """
    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT

    confidence = float(confidence)

    needle_image = load_cv2(needle_image, grayscale)
    needle_height, needle_width = needle_image.shape[:2]
    haystack_image = load_cv2(haystack_image, grayscale)

    if region:
        haystack_image = haystack_image[region[1]:region[1]+region[3],
                                      region[0]:region[0]+region[2]]
    else:
        region = (0, 0)  # full image; these values used in the yield statement
    if (haystack_image.shape[0] < needle_image.shape[0] or
        haystack_image.shape[1] < needle_image.shape[1]):
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError('needle dimension(s) exceed the haystack image or region dimensions')

    if step == 2:
        confidence *= 0.95
        needle_image = needle_image[::step, ::step]
        haystack_image = haystack_image[::step, ::step]
    else:
        step = 1

    # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystack_image, needle_image, cv2.TM_CCOEFF_NORMED)
    match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    matches = numpy.unravel_index(match_indices[:limit], result.shape)

    if len(matches[0]) == 0:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('Could not locate the image (highest confidence = %.3f)' % result.max())
        return

    # use a generator for API consistency:
    matchx = matches[1] * step + region[0]  # vectorized
    matchy = matches[0] * step + region[1]
    for x, y in zip(matchx, matchy):
        yield Box(x, y, needle_width, needle_height)

def requires_pillow(wrapped_function):
    """
    A decorator that marks a function as requiring Pillow to be installed.
    This raises PyScreezeException if Pillow wasn't imported.
    """
    @functools.wraps(wrapped_function)
    def wrapper(*args, **kwargs):
        if _PILLOW_UNAVAILABLE:
            raise PyScreezeException('The Pillow package is required to use this function.')
        return wrapped_function(*args, **kwargs)
    return wrapper


@requires_pillow
def _screenshot_win32(image_filename=None, region=None):
    """
    TODO
    """
    # TODO - Use the winapi to get a screenshot, and compare performance with ImageGrab.grab()
    # https://stackoverflow.com/a/3586280/1893164
    img = ImageGrab.grab()
    if region is not None:
        assert len(region) == 4, 'region argument must be a tuple of four ints'
        region = [int(x) for x in region]
        img = img.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
    if image_filename is not None:
        img.save(image_filename)
    return img


def _screenshot_osx(image_filename=None, region=None):
    """
    TODO
    """
    # TODO - use tmp name for this file.
    if image_filename is None:
        tmp_filename = 'screenshot%s.png' % (datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    else:
        tmp_filename = image_filename

    tmp_filename_parts = tmp_filename.split("/")
    if tmp_filename_parts[-1].startswith("."):
        # the screencapture command does not work with hidden files, so
        # temporarily remove the dot from the filename, take screenshot and
        # rename file to hidden filename
        tmp_filename_parts[-1] = tmp_filename_parts[-1][1:]
        tmp_filename_unhidden = "/".join(tmp_filename_parts)
        subprocess.call(["screencapture", "-x", tmp_filename_unhidden])
        subprocess.call(["mv", tmp_filename_unhidden, tmp_filename])
    else:
        subprocess.call(["screencapture", "-x", tmp_filename])

    img = Image.open(tmp_filename)

    if region is not None:
        assert len(region) == 4, 'region argument must be a tuple of four ints'
        region = [int(x) for x in region]
        img = img.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
        os.unlink(tmp_filename) # delete image of entire screen to save cropped version
        img.save(tmp_filename)
    else:
        # force loading before unlinking, Image.open() is lazy
        img.load()

    if image_filename is None:
        os.unlink(tmp_filename)
    return img


def _screenshot_linux(image_filename=None, region=None):
    """
    TODO
    """
    if not GNOME_SCREENSHOT_EXISTS:
        raise NotImplementedError('"gnome-screenshot" must be installed to use screenshot functions in Linux. Run: sudo apt-get install gnome-screenshot')
    if image_filename is None:
        tmp_filename = '.screenshot%s.png' % (datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    else:
        tmp_filename = image_filename
        # print(tmp_filename)
    if GNOME_SCREENSHOT_EXISTS:
        subprocess.call(['gnome-screenshot', '-f', tmp_filename])
        img = Image.open(tmp_filename)

        if region is not None:
            assert len(region) == 4, 'region argument must be a tuple of four ints'
            region = [int(x) for x in region]
            img = img.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
            os.unlink(tmp_filename) # delete image of entire screen to save cropped version
            img.save(tmp_filename)
        else:
            # force loading before unlinking, Image.open() is lazy
            img.load()

        if image_filename is None:
            os.unlink(tmp_filename)
        return img
    raise Exception('The gnome-screenshot program must be installed to take a screenshot with PyScreeze on Linux. Run: sudo apt-get install gnome-screenshot')




def load_cv2(img, grayscale=None):
    """
    TODO
    """
    # load images if given filename, or convert as needed to opencv
    # Alpha layer just causes failures at this point, so flatten to RGB.
    # RGBA: load with -1 * cv2.CV_LOAD_IMAGE_COLOR to preserve alpha
    # to matchTemplate, need template and image to be the same wrt having alpha

    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT
    if isinstance(img, (str, UniCode)):
        # The function imread loads an image from the specified file and
        # returns it. If the image cannot be read (because of missing
        # file, improper permissions, unsupported or invalid format),
        # the function returns an empty matrix
        # http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html
        if grayscale:
            img_cv = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        else:
            img_cv = cv2.imread(img, cv2.IMREAD_COLOR)
        if img_cv is None:
            raise IOError("Failed to read %s because file is missing, "
                          "has improper permissions, or is an "
                          "unsupported or invalid format" % img)
    elif isinstance(img, numpy.ndarray):
        # don't try to convert an already-gray image to gray
        if grayscale and len(img.shape) == 3:  # and img.shape[2] == 3:
            img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_cv = img
    elif hasattr(img, 'convert'):
        # assume its a PIL.Image, convert to cv format
        img_array = numpy.array(img.convert('RGB'))
        img_cv = img_array[:, :, ::-1].copy()  # -1 does RGB -> BGR
        if grayscale:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        raise TypeError('expected an image filename, OpenCV numpy array, or PIL image')
    return img_cv

def _kmp(needle, haystack, _dummy): # Knuth-Morris-Pratt search algorithm implementation (to be used by screen capture)
    """
    TODO
    """
    # build table of shift amounts
    shifts = [1] * (len(needle) + 1)
    shift = 1
    for pos in range(len(needle)):
        while shift <= pos and needle[pos] != needle[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    start_pos = 0
    match_len = 0
    for elem in haystack:
        while match_len == len(needle) or \
              match_len >= 0 and needle[match_len] != elem:
            start_pos += shifts[match_len]
            match_len -= shifts[match_len]
        match_len += 1
        if match_len == len(needle):
            yield start_pos


def _stepping_find(needle, haystack, step):
    """
    TODO
    """
    for start_pos in range(0, len(haystack) - len(needle) + 1):
        found_match = True
        for pos in range(0, len(needle), step):
            if haystack[start_pos + pos] != needle[pos]:
                found_match = False
                break
        if found_match:
            yield start_pos


def center(coords):
    """
    Returns a `Point` object with the x and y set to an integer determined by the format of `coords`.
    The `coords` argument is a 4-integer tuple of (left, top, width, height).
    For example:
    >>> center((10, 10, 6, 8))
    Point(x=13, y=14)
    >>> center((10, 10, 7, 9))
    Point(x=13, y=14)
    >>> center((10, 10, 8, 10))
    Point(x=14, y=15)
    """

    # TODO - one day, add code to handle a Box namedtuple.
    return Point(coords[0] + int(coords[2] / 2), coords[1] + int(coords[3] / 2))


def pixel_matches_color(x, y, expected_rgb_color, tolerance=0):
    """
    TODO
    """
    pix = pixel(x, y)
    if len(pix) == 3 or len(expected_rgb_color) == 3: #RGB mode
        r, g, b = pix[:3]
        ex_r, ex_g, ex_b = expected_rgb_color[:3]
        return (abs(r - ex_r) <= tolerance) and (abs(g - ex_g) <= tolerance) and (abs(b - ex_b) <= tolerance)
    if (len(pix) == 4 and len(expected_rgb_color) == 4): #RGBA mode
        r, g, b, a = pix
        ex_r, ex_g, ex_b, ex_a = expected_rgb_color
        return (abs(r - ex_r) <= tolerance) and (abs(g - ex_g) <= tolerance) and (abs(b - ex_b) <= tolerance) and (abs(a - ex_a) <= tolerance)
    assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (len(pix), len(expected_rgb_color))

def pixel(x, y):
    """
    TODO
    """
    # Need to select only the first three values of the color in
    # case the returned pixel has an alpha channel
    return RGB(*(screenshot().getpixel((x, y))[:3]))


# This makes sure that the openCV implementation of that function is used
locate_all = locate_all_opencv

if sys.platform.startswith('java'):
    raise NotImplementedError('Jython is not yet supported by PyScreeze.')
if sys.platform == 'darwin':
    screenshot = _screenshot_osx
elif sys.platform == 'win32':
    screenshot = _screenshot_win32
else: # TODO - Make this more specific. "Anything else" does not necessarily mean "Linux".
    screenshot = _screenshot_linux
####################################################################################################
###----------------------------------------------------------------------------------------------###
####################################################################################################
