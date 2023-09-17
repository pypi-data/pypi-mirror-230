"""Tests if the engine is able to complete the rpa challenge - https://rpachallenge.com/"""
import os
from webbrowser import get
import pytest
import cv2

from filecmp import cmp
from PIL.PngImagePlugin import PngImageFile

import setup_tests
from setup_tests import config_dict

if not config_dict['local-dev']:
    from setup_tests import disp


from src.aai_engine_package.engine import read_excel
from src.aai_engine_package.engine_util import locate
from src.aai_engine_package.engine import get_box_location


COLUMN_NAMES = ['First Name', 'Last Name', 'Company Name',
                'Role in Company', 'Address', 'Email', 'Phone Number'
               ]

FILE_NAMES = ['first_name_linux.png','last_name_linux.png','email_linux.png',
              'phone_number_linux.png', 'role_in_company_linux.png',
              'submit_linux.png','address_linux.png','company_name_linux.png'
             ]
LOCAL_DEV = config_dict['local-dev']
CWD = os.getcwd()


class TestRpaChallenge:
    """Checks if the engine can complete the RPA challenge: https://rpachallenge.com/
    """
    def test_rpa_challenge(self):
        """Abstract version of the RPA challenge
        """
        # Load people data
        people = read_excel("tests/files/challenge.xlsx")
        assert len(people) == 10
        assert COLUMN_NAMES == list(people[0].keys())
        data = {}
        data["people"] = people

        # Check if bounding boxes get drawn correctly
        situation_index = 1
        for person in data['people']:
            """Do not delete the comments with cv2, they are needed to generate a visual check
               of the bounding boxes of the rpa challenge in case a test fails
            """
            # Load haystack image
            haystack_image_path = "tests/images/situations/" + str(situation_index) + '.png'
            haystack_image = PngImageFile(haystack_image_path)
            if config_dict['local-dev']:
                haystack_checker = cv2.imread(haystack_image_path)

            assert haystack_image

            for img_path in FILE_NAMES:
                box_location = get_box_location("tests/images/steps/" + img_path,haystack=haystack_image, cache_confidence=False)

                assert box_location

                # Write generated box to a file
                with open('tests/files/bounding_boxes.txt','a',encoding="utf-8") as file:
                    file.write(f"{person['First Name']}-{img_path}-{box_location} + \n")
                # print(f"{person['First Name']} ---- {img_path} ------ {box_location}")
                if config_dict['local-dev']:
                    cv2.rectangle(haystack_checker, (box_location.left, box_location.top), (box_location.left + box_location.width,box_location.top + box_location.height), (0, 0, 255))
            if config_dict['local-dev']:
                cv2.imwrite(f"tests/images/check_{str.lower(person['First Name'])}.png",haystack_checker)
            situation_index += 1

        # Compare the bounding boxes from the check file to the ones drawn in the test
        assert cmp('tests/files/bounding_boxes.txt','tests/files/check_bounding_box.txt',shallow=False)


    def load_needle_image(self,url):
        """Auxilary Function that loads in the needle image as PngImageFile
        """
        full_file_path = '/'.join([CWD, url])
        needle_img = PngImageFile(full_file_path)
        return needle_img

    @pytest.fixture(scope='session', autouse=True)
    def setup_cleanup(self):
        """Performs the setup before the test session and cleans up after the session
        """
        if not LOCAL_DEV:
            #===============Will be executed before the first test===============#
            yield disp
            #================Will be executed after the last test================#
            disp.stop()
            try:
                os.remove('tests/files/bounding_boxes.txt')
            except OSError:
                pass
        else:
            #===============Will be executed before the first test===============#
            yield None
            #================Will be executed after the last test================#
            try:
                os.remove('tests/files/bounding_boxes.txt')
            except OSError:
                pass

if __name__ == "__main__":
    rpa = TestRpaChallenge()
    rpa.test_rpa_challenge()
