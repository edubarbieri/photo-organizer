import os
from util import safe_name
import pytest

def test_safe_name_with_not_found_file():
    expected_path = os.path.join(
        'test_assets', 'destination', 'dest_not_foud.jpg')
    assert safe_name(expected_path) == expected_path


def test_safe_name_with_exist_file():
    path = os.path.join(
        'test_assets', 'destination', 'dest_img.jpg')
    expected_path = os.path.join(
        'test_assets', 'destination', 'dest_img - 1.jpg')
    assert safe_name(path) == expected_path
