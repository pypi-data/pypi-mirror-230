"""""" #Left empty because its prettier in mkdocs
from csv import get_dialect
from tabnanny import check
from pynput.keyboard import Controller
import pyautogui
import sys
import time
import random
import os
import json
import platform
import subprocess
import pandas as pd
import numpy as np
from random import choice
from string import digits
from datetime import datetime
import tempfile
import yaml
import traceback
import cv2
import requests

from src.aai_engine_package.engine_util import locate_on_screen, screenshot, locate
from src.aai_engine_package.engine_util import LARGE_FONT, NORM_FONT, SMALL_FONT, REGION_PICK_VIEW, OFFSET_PICK_VIEW, SIMILARITY_PICK_VIEW, NAME_PICK_VIEW
from cron_descriptor import get_description

import collections
Box = collections.namedtuple('Box', 'left top width height')

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import tkinter
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
from PIL.PngImagePlugin import PngImageFile, PngInfo


import zmq

import pytesseract
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3

ZMQ_PORT = 5555
ZMQ_MSG_TYPE_PROGRESS = "progress"
ZMQ_MSG_TYPE_DATA = "data"
ZMQ_MSG_TYPE_QUEUE_TASK = "queue_task"

pyautogui.FAILSAFE = True

CWD = os.getcwd()

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
REL_PATH = "my_screenshot.png"
abs_file_path = os.path.join(script_dir, REL_PATH)
SCREENSHOT = abs_file_path

dirname = os.path.dirname(__file__)



# Global variables to check if internal display is used as main display on OSX. Needed because of bug which causes the
# screen resolution to be doubled when said condition is met.
USING_OSX = os.name == 'posix' and platform.system() == "Darwin"
USING_INTERNAL_DISPLAY_AS_MAIN_ON_OSX = False

FILLING_SPACE = 103

try:
    with open(os.path.join(dirname, "config.yml"), "r", encoding="utf-8") as config:
        conf = yaml.load(config,yaml.Loader)
        URL_AAI = conf['URL_AAI']
        URL_OCR = conf['URL_OCR']
except:
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Could not set the URL's!")

STDOUT_FILENAME = "stdout.txt"
EXECUTION_LOG_FILENAME = "execution_log.txt"
ZMQ_LOG_FILENAME = "zmq_log.txt"



def internal_display_used_as_main_on_osx() -> bool:
        '''
        Checks if internal display is used as main display on macOS
        '''
        if not USING_OSX:
            return False

        # read display information on mac
        display_profiler_output = json.loads(subprocess.getoutput('system_profiler SPDisplaysDataType -json'))

        # search for info object for internal display
        display_infos = display_profiler_output['SPDisplaysDataType'][0]['spdisplays_ndrvs']
        internal_display_as_main = False
        i = 0
        while i < len(display_infos) and not internal_display_as_main:
            display_info = display_infos[i]
            internal_display_as_main = 'spdisplays_connection_type' in display_info \
                and display_info['spdisplays_connection_type'] == 'spdisplays_internal' \
                and 'spdisplays_main' in display_info \
                and display_info['spdisplays_main'] == 'spdisplays_yes'
            i += 1

        return internal_display_as_main


def log(filename, line, time=True):
    """Log to file"""
    with open(filename, "a+", encoding="utf-8") as file:
        if time:
            now = datetime.strftime(datetime.now(), '%H:%M:%S') + ": "
        else:
            now = ""
        file.write(now + line + "\n")


class TaskWrapper():
    """
    Task wrapper class to control execution of task
    """

    def __init__(self, task_id, name, cwd, script, scheduled_time, execution_type=-1, priority=15, trigger=lambda _: True):
        self.task_id = task_id
        self.name = name
        self.cwd = cwd
        self.steps = []
        self.script = script
        self.scheduled_time = scheduled_time
        self.execution_type = execution_type
        self.trigger = trigger
        self.priority = priority
        self.company = ""

    def execute(self, logdir: str):
        """_summary_

        Returns:
            _type_: _description_
        """
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Executing task script")

        filepath=self.script # TODO: checks on file

        # info = subprocess.STARTUPINFO()
        # info.dwFlags = subprocess.STARTUPINFO()
        # info.wShowWindow = SW_MINIMIZE

        stdout_filename = os.path.join(logdir, STDOUT_FILENAME)
        with open(stdout_filename, "w+", encoding="utf-8") as stdout_file:
            # check if python command exists on current machine and has version 3.x, otherwise run python3
            status, output = subprocess.getstatusoutput('python --version')
            python_command = "python" if status == 0 and output.startswith("Python 3") else "python3"
            process = subprocess.Popen(
                [python_command, filepath, logdir, self.company],  # pass log_dir as cli arg # Pass company name for the current context of the task
                cwd=self.cwd,
                stdout=stdout_file,
                shell=False
            )
            return process

    def __str__(self) -> str:
        """str format for TaskWrapper"""
        if self.execution_type == 'SC':
            return f"ID:{self.task_id} = {self.name}||scheduled at: {get_description(self.scheduled_time)}"
        if self.execution_type == 'MA':
            return f"ID:{self.task_id} = {self.name}||scheduled at: manually"
        return f"ID:{self.task_id} = {self.name}||scheduled at: continuously"

class Task():
    """
    Task class to control and keep track of all information and steps within a task.
    """
    def __init__(self, name, cwd, script=None, standalone=False):
        """

        Args:
            name (str): Name of the task.
            cwd (str): The current working directory.
            script (str, optional): Optional path to a script you can provide for the give task. If a script is given this will override the steps that are listed in the task. Defaults to None.
            standalone (bool, optional): Put this value to True if you run your robot independently without the task manager. Defaults to False.
        """
        self.name = name
        self.cwd = cwd
        self.steps = []
        self.script = script
        self.standalone = standalone

        self._data = {}  # task-specific data
        if standalone:
            log_time = datetime.strftime(datetime.now(), '%Y-%m-%dT%H%M%S')
            self.logdir = os.path.join(cwd, 'logs', name, log_time)
            os.makedirs(self.logdir, exist_ok=True)
        else:
            self.logdir = sys.argv[1]

        self.zmq_client_socket = self._get_zmq_client_socket()
        self.last_box_location = None
        self.error = False
        # read execution and zmq logfile names from command line args if not run as standalone

        self._print_title()

    def _get_zmq_client_socket(self):
        """Establishes ZMQ connection with engine manager process and returns Socket"""
        if self.standalone:
            return None
        self._log_zmq("Connecting to ZMQ client socket.")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://localhost:{ZMQ_PORT}")
        return socket

    def add_step(self, step):
        """Add a step to the current list of steps.

        Args:
            step (Step): The step you want to add.
        """
        self.steps.append(step)
        step.set_task(self)

    def execute(self):
        """Execute all steps within this task"""

        # Only check if internal display is used as main on OSX once per task execution for efficiency reasons
        global USING_INTERNAL_DISPLAY_AS_MAIN_ON_OSX
        USING_INTERNAL_DISPLAY_AS_MAIN_ON_OSX = internal_display_used_as_main_on_osx()

        self._log_execution("STARTING TASK EXECUTION")


        if self.script is None:
            self.error = False
            if not self.standalone:
                self._update_progress(f"0/{len(self.steps)}")
            for idx, step in enumerate(self.steps):
                self._print_step(step,idx)
                if not self.error:
                    step.execute()
                else:
                    self._log_execution("Execution stopped due to an error in a previous step!")
                if not self.standalone:
                    self._update_progress(f"{idx + 1}/{len(self.steps)}")
            if not self.error:
                print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: TASK SUCCESSFULLY FINISHED!\n")
                self._log_execution("TASK SUCCESSFULLY FINISHED!\n")
            if not self.standalone:
                # task finished, send task data as JSON string to engine manager process
                # TODO maybe don't send task data immediately but allow control for when this happens outside of this function?
                self._send_task_data()
        else:
            # For legacy scripts or external scripts outside the engine
            print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Executing script")
            filepath=self.script # TODO: checks on file
            proc = subprocess.Popen(filepath, shell=True, stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: return code={proc.returncode}") # is 0 if success

    def _task_failed(self):
        """Function that logs the most important things after a failure
        """
        self.error = True
        screenshot_path = os.path.join(self.logdir, "last_screenshot.png")
        try:
            img = PngImageFile(os.path.join(self.cwd,".temp_screenshot.png"))
            img.save(screenshot_path)
        except Exception as ex:
            screenshot_path = "No screenshot could be found"
        self._log_execution(f"The last screenshot can be found at: {screenshot_path}", time=False)
        self._log_execution(f"The last box was: {self.last_box_location}", time=False)
        self._log_execution(f"TASK FAILED!")

    def _set_last_box_location(self, new_box_location):
        """Setter for the last box location used for logging purposes

        Args:
            new_box_location (Box): new box location
        """
        self.last_box_location = new_box_location

    def _print_step(self,step, idx):
        """Print the current step information

        Args:
            step (Step): The step we want to log
            idx (int): Step number
        """
        self._log_execution("-"*(len(self.name) + FILLING_SPACE), time=False)
        self._log_execution("\tExecuting step ({idx}/{total}) - {name}".format(idx=(idx+1), total=len(self.steps), name=step.name), time=False)
        self._log_execution("-"*(len(self.name) + FILLING_SPACE), time=False)

    def _print_title(self):
        """Log the title of the task in the execution logs
        """
        title_length = len(self.name) + FILLING_SPACE
        s_char = "="
        str1 = s_char*int((FILLING_SPACE - len("Task Name: "))/2)
        str2 = s_char*title_length
        self._log_execution(str2, time=False)
        self._log_execution(str1 + "Task Name: " + self.name + str1, time=False)
        self._log_execution(str2, time=False)

    def _log_execution(self, line, time=True):
        """Log the execution process"""
        log(f"{self.logdir}/{EXECUTION_LOG_FILENAME}", line, time)

    def _log_zmq(self, line, time=True):
        """Log ZMQ communication"""
        log(f"{self.logdir}/{ZMQ_LOG_FILENAME}", line, time)

    def _send_zmq_msg(self, type, msg):
        msg = {"type": type, "msg": msg}
        self.zmq_client_socket.send_json(msg, ensure_ascii=False)
        reply = self.zmq_client_socket.recv()
        self._log_zmq(f"Server replied: {reply}")

    def _update_progress(self, progress):
        """Update progress on task

        Args:
            progress (str): Description of the current progress
        """
        self._log_zmq(f"Sending progress: {progress}")
        self._send_zmq_msg(ZMQ_MSG_TYPE_PROGRESS, progress)

    def _send_task_data(self):
        '''Send task data to ZMQ server'''
        self._log_zmq(f"Sending task data: {self._data}")
        self._send_zmq_msg(ZMQ_MSG_TYPE_DATA, self._data)

    def set_data_item(self, key, val):
        """Set key-value pair in task data"""
        self._data[key] = val

    def get_data_item(self, key):
        """Get item with given key from task data"""
        return self._data[key]

    def get_data(self):
        """Get task data"""
        return self._data

    # ENGINE FUNCTIONS
    def kill_processes(self, process_names=[]):
        """Calls engine.kill_processes
        """
        kill_processes(process_names=process_names, task=self)

    def click(self, img_location):
        """Calls engine.click
        """
        click(img_location, task=self)
        self._log_execution(f"-> click on {img_location} located at {self.last_box_location}")

    def click_right(self, img_location):
        """Calls engine.click_right
        """
        click_right(img_location, task=self)
        self._log_execution(f"-> right click on {img_location} located at {self.last_box_location}")

    def double_click(self, img_location):
        """Calls engine.double_click
        """
        double_click(img_location, task=self)
        self._log_execution(f"-> double click on {img_location} located at {self.last_box_location}")

    def click_n(self, img_location, nr_clicks, button='left'):
        """Calls engine.click_n
        """
        click_n(img_location, nr_clicks, button=button, task=self)
        self._log_execution(f"-> click {button}, {nr_clicks} times on {img_location} located at {self.last_box_location}")

    def exists(self, img_location):
        """Calls engine.exists
        """
        self._log_execution("-> check if image exists")
        return try_exists(img_location, task=self)

    def get_box_location(self, img_location,haystack=None,iterations=5,steps_per_iteration=4,cache_confidence=True,debug=False):
        """Calls engine.get_box_location
        """
        return get_box_location(img_location,haystack=haystack,iterations=iterations,steps_per_iteration=steps_per_iteration,cache_confidence=cache_confidence,debug=debug, task=self)

    def check_boxes_list(self, boxes,limit=5, treshold=10):
        """Calls engine.check_box_list
        """
        self._log_execution("-> Verify how close boxes are")
        return check_boxes_list(boxes, limit=limit, treshold=treshold, task=self)

    def wait(self,img_location, seconds):
        """Calls engine.wait
        """
        self._log_execution(f"-> Wait for {seconds}s, then try to find the image")
        wait(img_location, seconds, task=self)

    def sleep(self, seconds):
        """Calls engine.sleep
        """
        self._log_execution(f"-> sleep for {seconds}s")
        sleep(seconds, task=self)

    def type_text(self, text):
        """Calls engine.type_text
        """
        self._log_execution(f"-> Write '{text}'")
        type_text(text, task=self)

    def key_combo(self, *keys):
        """Calls engine.key_combo
        """
        self._log_execution(f"-> click_right")
        key_combo(*keys, task=self)

    def remove_char(self, nr_characters=1):
        """Calls engine.remove_char
        """
        remove_char(nr_characters=nr_characters, task=self)

    def copy_to_clipboard(self):
        """Calls engine.copy_to_clipboard
        """
        self._log_execution(f"-> Copy to clipboard")
        copy_to_clipboard(task=self)

    def get_clipboard(self):
        """Calls engine.get_clipboard
        """
        self._log_execution(f"-> Get clipboard contents")
        return get_clipboard(task=self)

    def read_excel(self, path):
        """Calls engine.read_excel
        """
        self._log_execution(f"-> Read excel file")
        result = read_excel(path, task=self)
        self._log_execution(f"\tDATA from {path}: ", time=False)
        for point in result:
            self._log_execution("\t\t" + str(point), time=False)
        return result

    def ocr_image_server(self, img_location, token, haystack_path = None, on_needle=False):
        """Calls engine.ocr_image_server
        """
        ocr_image_server(img_location=img_location, token=token, haystack_path=haystack_path, on_needle=on_needle, task=self)

    def drag(self, start_x, start_y, x_offset, y_offset, duration):
        """Calls engine.drag
        """
        drag(start_x=start_x, start_y=start_y, x_offset=x_offset, y_offset=y_offset, duration=duration, task=self)


class Step():
    """
    Keep track of a certain step within a task
    """

    def __init__(self, name, func, *args):
        self.name = name
        self.func = func
        self.args = args
        self.task = None  # Task object which the step is part of

    def execute(self):
        """Execute the step
        """
        try:
            self.func(self.task, *self.args)
        except Exception as ex:
            self.task._log_execution("ERROR: ")
            self.task._log_execution(traceback.format_exc(), time=False)
            self.task._task_failed()

    def set_task(self, task: Task):
        """Set the step's corresponding Task"""
        self.task = task

def try_click(img_path, tries = 5, sleep_duration = 1, task = None, nr_clicks = 1):
    """Tries to click on the specified image

    Args:
        img_path (str): Path to the image
    """
    for _ in range(tries):
        try:
            click_n(img_path, nr_clicks=nr_clicks, task=task)
            if task:
                task._log_execution(f"Clicked on {img_path}")
            return
        except:
            time.sleep(sleep_duration)
    raise Exception(f"Image not found: {img_path}")

def try_exists(img_path, tries = 5, sleep_duration = 1, task = None):
    """Checks if a given image exists on the screen.

    Args:
        img_location (str): Path to the image.
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    Returns:
        exist(bool): True if the image exists, False otherwise.
    """
    for _ in range(tries):
        try:
            box = get_box_location(img_path, task=task, cache_confidence=False)
            if box is not None:
                print(f"Image exists on the screen!")
                return True
        except:
            time.sleep(sleep_duration)
    print(f"Image not found on the screen")
    return False

def click(img_location,task=None):
    """Locate the given image on the screen and click it. Calls click_n.


    Args:
        img_location (str): Location of the image that needs to be clicked
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    click_n(img_location, 1, task=task)


def click_right(img_location, task=None):
    """Locate the given image on the screen and right click it. Calls click_n.


    Args:
        img_location (str): Location of the image that needs to be clicked
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    click_n(img_location, 1, button="right", task=task)


def double_click(img_location, task=None):
    """Locate the given image on the screen and double click it. Calls click_n.


    Args:
        img_location (str): Location of the image that needs to be clicked
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    click_n(img_location, 2, task=task)

def click_n(img_location, nr_clicks, button='left', task=None):
    """This function will try to find the image on the screen. If the image is found, a click event happens on the provided location offset.
       This offset is saved in the image metadata as: 'offset_x' and 'offset_y'.
    Args:
        img_location (str): The location of the image that you want to find on the screen.
        nr_clicks (int): Amount of times the image needs to be clicked.
        button (str, optional): Type of click [left,right,middle]. Defaults to 'left'.
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Raises:
        RuntimeError: Raised when the image is not find on the current screen.
    """
    img = PngImageFile(img_location)
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Trying to click on {img_location}")
    print(f"\t image metadata: {img.text}")

    haystack = screenshot(CWD + "/.temp_screenshot.png")

    if task:
        box_location = get_box_location(img_location,haystack=haystack,cache_confidence=False, task=task)
    else:
        box_location = get_box_location(img_location,haystack=haystack,cache_confidence=False)

    if box_location is None:
        raise RuntimeError("Image not found on current screen.")

    print(f"\tImage found on screen at: {box_location}")

    x_coord = int(float(img.text["offset_x"]))
    y_coord = int(float(img.text["offset_y"]))

    if USING_INTERNAL_DISPLAY_AS_MAIN_ON_OSX:
        # resolution is half the size on macos when using internal display as main screen
        x_coord /= 2
        y_coord /= 2
        x_coord += (box_location.left + box_location.width / 2) / 2
        y_coord += (box_location.top + box_location.height / 2) / 2
    else:
        x_coord += box_location.left + box_location.width / 2
        y_coord += box_location.top + box_location.height / 2

    for _ in range(0,nr_clicks):
        pyautogui.click(x=x_coord,
                        y=y_coord,
                        button=button)
    print(f"\tClicked: {img_location}")


def get_box_location(img_location,haystack=None,iterations=5,steps_per_iteration=4,cache_confidence=True,debug=False, task=None):
    """Checks if the images exists on the current screen or haystack image, and returns the box location

    Args:
        img_location (str): Path to the needle image (Image to be found on the screen)
        haystack (str, optional): Image where the needle image needs to be found. Defaults to None.
        iterations (int, optional): Maximum iterations of the algorithm. Defaults to 5.
        steps_per_iteration (int, optional): Amount of steps per iteration. This determines the step size of the confidence values. Defaults to 4.
        cache_confidence (bool, optional): Tells to this algorithm to look for a cache confidence value before running the iterations. Defaults to True.
        debug (bool, optional): Debug toggle for logging some useful information about the process. Defaults to False.
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Returns:
        box_location(Box): The location of the box that was found by the algorithm
    """
    img = PngImageFile(img_location)
    upper_confidence = float(img.text["upper_confidence"])
    lower_confidence = float(img.text["lower_confidence"])

    box_location = None
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Trying to find the image on the screen")
    # CHECK IF CONFIDENCE VALUE IS CACHED
    if cache_confidence:
        # TODO this does not work well
        try:
            confidence = float(img.text['cached_confidence'])
            print(f"\tCached confidence available: {confidence}")
            if haystack:
                box_location = locate(img, haystack_image=haystack, confidence=float(confidence))
            else:
                box_location = locate_on_screen(img_location, confidence=float(confidence))
            if box_location and not isinstance(box_location,list):
                print(f"\tbox found in cache!")
                if task:
                    task._set_last_box_location(box_location)
                return box_location
        except Exception as ex:
            print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: An error occured while searching for the image")

    # ITERATE OVER SEVERAL RANGES UNTIL BOX IS FOUND OR MAX ITERATIONS IS EXCEEDED
    if debug:
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Executing the dynamic confidence finder algorithm")
    for iteration in range(iterations):
        step_size = (upper_confidence - lower_confidence)/(steps_per_iteration*1.0)
        upper_confidence_fixated = upper_confidence
        if debug:
            print(f"ITERATION: {iteration}")
            print(f"\tcurrent step size: {step_size:.2f}")
            print(f"\tcurrent upper bound: {upper_confidence:.2f}")
            print(f"\tcurrent lower bound: {lower_confidence:.2f}\n")


        for i in range(steps_per_iteration):
            # Try to find a single box for the current needle
            current_confidence = upper_confidence_fixated - i*step_size
            if debug:
                print(f"\tSTEP {i}")
                print(f"\t\tConfidence value: {current_confidence}")
            try:
                if haystack:
                    box_location = locate(img, haystack_image=haystack, confidence=float(current_confidence))
                else:
                    box_location = locate_on_screen(img_location, confidence=float(current_confidence))
            except Exception as ex:
                pass

            # Check the box_location
            if not box_location:
                # The confidence was too high and the new upperbound of the confidence should be lowered!
                upper_confidence = current_confidence
                if debug:
                    print(f"\t\tnew upper: {upper_confidence}")
            elif isinstance(box_location,list):
                if debug:
                    print(f"\t\tToo many boxes: {len(box_location)}")
                # If box_location is array, more than 1 match is found -> lower confidence bound should be raised + break the inner for loop!
                lower_confidence = current_confidence
                break
            else:
                # Box location exists and is singular -> return the box + cache the found confidence value if cache=True!
                if cache_confidence:
                    info = PngInfo()
                    for key,value in img.text.items():
                        info.add_text(key,value)
                    info.add_text('cached_confidence',str(current_confidence))
                    img.save('/'.join([CWD, img_location]),pnginfo=info)
                if task:
                    task._set_last_box_location(box_location)
                return box_location

    # If max iterations is exceeded and multiple boxes remain: Check if they are close to each other and if so, return the first box
    if box_location:
        if task:
            task._set_last_box_location(box_location)
        return check_boxes_list(box_location, task=task)

    if task:
        task._set_last_box_location(None)
    return None

def check_boxes_list(boxes,limit=5, treshold=10, task=None):
    """Checks if the box locations are close to each other. Returns the first box if they are close.
       Otherwise it will return None.

    Args:
        boxes (list): list of box locations
        limit (int, optional): Limit of boxes to take into consideration. Defaults to 5.
        treshold (int, optional): Treshold for the similarity metric. Defaults to 10.
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Returns:
        Box(Box): The final box location or None if they are too far apart
    """
    # Check if amount of boxes goes over the allowed number
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Check if boxes are close to each other")
    if len(boxes) > limit:
        return None

    mae = 0
    for box in boxes:
        # All boxes need to have the same dimensions
        if box.width != boxes[0].width or box.height != boxes[0].height:
            print(f"\tBoxes didn't have the same dimensions")
            return None
        if box != boxes[0]:
            mae += abs(box.left - boxes[0].left)
            mae += abs(box.top - boxes[0].top)

    print(f"\tThe MAE for this case is: {mae}")
    if mae <= treshold:
        print(f"\tThe boxes where close enough! Returning the first one.")
        return boxes[0]

    return None

def update_usage_user(token, usage):
    """Update the usage of a certain feature of the user

    Args:
        token (str): The authentication token of the user
        usage (str): The feature that needs to be updated ('ocr',...)
    """
    headers = {"authorization": 'JWT '+str(token)}
    query = """
        mutation ($input: FeatureInputType!, $usage:String){
            updateUser(input: $input, usage: $usage){
                    user {
                            username
                            features{
                                    ocr
                                    ocrUsage
                            }
                    }
            }
        }
    """
    variables = {
        "input": {},
        "usage": usage
    }
    r = requests.post(URL_AAI, json={'query': query, 'variables': variables}, headers=headers)


def get_user_features(token):
    """Get the features of the user

    Args:
        token (str): Authtentication token of the user

    Returns:
        dict: The features object
    """
    try:
        headers = {"authorization": 'JWT '+str(token)}
        query = """
            query {
                userFeatures{
                    features{
                        id
                        ocr
                        ocrResourceLimitReached
                        ocrUsage
                        ocrTimeframe
                    }
                }
            }
        """
        r = requests.post(URL_AAI, json={'query': query}, headers=headers)
        res = json.loads(r.text)
        features = res["data"]["userFeatures"]["features"]
        return features
    except Exception as ex:
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Could not verify the user! \n{ex}")
    return None

def update_user_activity(token, feature_id, date, usage):
    """Update the activity of the user

    Args:
        token (str): Authtentication token of the user
        feature_id(int): Id of the features objct the user activity is linked to
        date(str): String version of the date to look for
        usage(str): Resource that the user consumed ('ocr',...)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        headers = {"authorization": 'JWT '+str(token)}
        query = """
            mutation ($featureId: Int!, $date: String!, $usage: String){
                updateUserActivity (featureId: $featureId, date: $date, usage: $usage){
                    userActivity{
                        id
                        feature {
                            id
                        }
                        date
                        ocr
                    }
                }
            }
        """
        variables = {
            "featureId": feature_id,
            "date": date,
            "usage": usage
        }
        r = requests.post(URL_AAI, json={'query': query, 'variables':variables}, headers=headers)
        res = json.loads(r.text)
        return 'errors' not in res.keys()
    except Exception as ex:
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Could not verify the user! \n{ex}")
    return False

def ocr_image_server(img_location, token, haystack_path = None, on_needle=False, task=None):
    """Perform OCR on an image on the server

    Args:
        img_location (str): Location of the needle image
        token: Authentication token of the current user
        haystack_path (str, optional): Path to a self-specified haystack. If None a new screenshot will be taken. Defaults to None.
        on_needle (bool, optional): Perform OCR on the needle image (True) or the OCR box, given in the metadata of the image (False). Defaults to False.
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Returns:
        str: Tesseract output of the text in the image
    """
    features = get_user_features(token)
    if features:
        # Check if user has the privilege to use the feature
        if features and features['ocr']:
            try:
                needle = PngImageFile(img_location)
                metadata = needle.text
                if haystack_path:
                    haystack = PngImageFile(haystack_path)
                else:
                    haystack = screenshot(CWD + "/.temp_screenshot.png")
                anchor_box = get_box_location(img_location, haystack=haystack)

                ocr_box = [2*int(i) for i in metadata['ocr_box_relative'][1:-1].split(',')]

                ocr_img = haystack.crop((anchor_box.left + ocr_box[0],anchor_box.top + ocr_box[1],anchor_box.left + ocr_box[0] + ocr_box[2],anchor_box.top + ocr_box[1] + ocr_box[3]))

                if on_needle:
                    needle.save(CWD + "/.temp_ocr.png")
                else:
                    ocr_img.save(CWD + "/.temp_ocr.png")

                # Check if user did not consume to many resources already
                update_usage_user(token, 'ocr')
                # Reload the features because the update might have changed the values
                features = get_user_features(token)
                print(features)
                # Ask server to do OCR on the image
                if features['ocrResourceLimitReached']:
                    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: You exceeded the daily limit!")
                    return None
                response = requests.post(URL_OCR, files={'image':open(CWD + "/.temp_ocr.png", "rb")}, data=needle.text)
                # Update the user activity
                if not features['ocrResourceLimitReached']:
                    result = update_user_activity(token, features['id'], datetime.strftime(datetime.now(), '%Y-%m-%d'), 'ocr')
                    if result:
                        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: User activity successfully updated!")
                    else:
                        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: User activity update failed!")
                return response.text
            except Exception as ex:
                print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Could not load the needle and haystack image! \n{ex}")
        else:
            print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: You do not have the rights to use the OCR functionality!")
    else:
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: The Feature object is not set for this user!")
    return None

def wait(img_location, seconds, task=None):
    """ Wait a given amount of seconds for a given image, checking its existence.

    Args:
        img_location (str): Path to the image.
        seconds (int): Amount of seconds to wait.
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Raises:
        RuntimeError: Raised when the image was not found.
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Waiting for: {img_location}")
    starttime = time.time()
    for _ in range(0, seconds):
        if try_exists(img_location, task=task):
            return
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))
    raise RuntimeError("\tTimeout: Image not found.")


def sleep(seconds, task=None):
    """Sleep for a certain amount of time

    Args:
        seconds (int): Amount of seconds to sleep
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Sleeping for {seconds}s")
    time.sleep(seconds)

def kill_processes(process_names = [], task=None):
    """_summary_

    Args:
        process_names (list, optional): List with names of processes to be killed. Defaults to [].
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    for process in process_names:
        # Kill process
        output = os.popen(f'taskkill /im {process} /F').read()
        if task:
            task._log_execution(f"Executing command to kill {process.lower().split('.exe')[0]} process:\n\ttaskkill /im {process} /F\n{output}")
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Executing command to kill {process.lower().split('.exe')[0]} process:\n\ttaskkill /im {process} /F\n{output}")

def drag(start_x, start_y, x_offset, y_offset, duration=0, task=None):
    """Drags the mouse from the start coordinates to the given offset

    Args:
        start_x (int): Start position of mouse for x-coordinate
        start_y (int): Start position of mouse for y-coordinate
        x_axis (int): Negative = to the left, Positive = to the right
        y_axis (int): Negative = up, Positive = down
        duration (int): How long the drag should take. Defaults to 0
    """
    # Move mouse to starting position
    pyautogui.moveTo(start_x, start_y)

    # Drag mouse over given offset
    pyautogui.drag(x_offset, y_offset, duration=duration)

    # Logging
    logging_str = f"Drag mouse from ({start_x}, {start_y}) to ({start_x + x_offset}, {start_y + y_offset})"
    if task:
        task._log_execution(logging_str)
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: {logging_str}")

def type_text(text, task=None):
    """Type the given text.

    Args:
        text (str): The text to write.
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    keyboard = Controller()
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Write {text}")
    keyboard.type(text)

def key_combo(*keys, task=None):
    """Type a given key comination (ctrl, shift, esc, f1, ...).

    Args:
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Pressing keys: {str(keys)}")
    pyautogui.hotkey(*keys)

def remove_char(nr_characters=1, task=None):
    """Remove n characters (backspace).

    Args:
        nr_characters (int, optional): Amount of characters to remove. Defaults to 1.
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Removing {nr_characters} characters")
    for _ in range(0, nr_characters):
        pyautogui.hotkey("backspace")


def copy_to_clipboard(task=None):
    """Copy data to clipboard

    Args:
        task (Task, optional): Task object to log the information of this function. Defaults to None.
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Copy to clipboard")
    tcl = tkinter.Tk()
    tcl.withdraw()
    tcl.clipboard_clear()

    data = sys.stdin.read()

    tcl.clipboard_append(data)

    if sys.platform != 'win32':
        if len(sys.argv) > 1:
            print('\tData was copied into clipboard. Paste and press ENTER to exit...')
        else:
            # stdin already read; use GUI to exit
            print('\tData was copied into clipboard. Paste, then close popup to exit...')
            tcl.deiconify()
            tcl.mainloop()
    else:
        tcl.destroy()


def get_clipboard(task=None):
    """Get clipboard text independently from the OS

    Args:
        task (Task, optional): Task object to log the information of this function. Defaults to None.

    Returns:
        str: The text in the current clipboard
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Get clipboard contents")
    return tkinter.Tk().clipboard_get()


def authenticate(login, url, query, variables):
    """Request token at given URL (for either AAI or QSFS backend)"""
    r = requests.post(url, json={'query': query, 'variables': variables})
    print(f"Request response: {r}")
    res = json.loads(r.text)

    if r.status_code == 200:
        print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Login at {url} of user {login} succeeded\n")
        return res["data"]["tokenAuth"]["token"]
    print(r.status_code)
    raise ValueError('Could not authenticate.')

def authenticate_aai(username, password):
    """Request token for AAI backend"""
    query = """
        mutation auth($username: String!, $password: String!){
            tokenAuth(username: $username, password: $password) {
                success,
                errors,
                unarchiving,
                token,
                unarchiving,
                user {
                    id,
                    username,
                }
            }
        }
    """

    variables = {
        "username": username,
        "password": password,
    }

    return authenticate(username, URL_AAI, query, variables)

### FILE READ UTILS ###
def read_excel(path, task=None, sheet_name=0, dtype=str):
    """Read in the data from an excel file

    Args:
        path (str): Path to the excel file
        task (Task, optional): Task object to log the information of this function. Defaults to None.
        sheet_name (int or str, optional): Specifies which sheet will be picked in the excel workbook. Defaults to 0 (the first sheet in the workbook)

    Returns:
        Dict: A dictionary that contains the information in the excel file
    """
    print(f"{datetime.strftime(datetime.now(), '%H:%M:%S')}: Reading in excel data from {path}")
    return pd.read_excel(path, sheet_name, dtype=dtype).to_dict(orient='records')
