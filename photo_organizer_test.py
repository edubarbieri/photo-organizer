import os
import pytest
import datetime
from photo_organizer import get_config, default_config, img_date, destination_path
import platform

@pytest.fixture(scope="module", autouse=True)
def configure():
    default_config['SOURCE_FOLDER'] = './test_assets/source'
    default_config['DESTINATION_FOLDER'] = './test_assets/destination'
    default_config['OPERATION'] = 'COPY'

@pytest.fixture
def configs():
    return default_config

def test_get_config_default_value(configs):
    """Teste if return default configs values"""
    assert get_config('SOURCE_FOLDER') == configs['SOURCE_FOLDER']


def test_get_config_replace_by_os_env():
    """Teste if return default configs values"""
    value = 'MIMIMIMIMIMIMI'
    os.environ["SOURCE_FOLDER"] = value
    assert get_config('SOURCE_FOLDER') == value

def test_image_date_with_take_date():
    dt_expect = datetime.datetime(2020, 5, 10, 23, 5, 40, 420000)
    dt = img_date('./test_assets/source/take_date.jpg')
    assert dt == dt_expect

def test_image_date_without_take_date():
    dt_expect = datetime.datetime(2020, 5, 10, 23, 9, 15, 171856)
    dt = img_date('./test_assets/source/no_date.png')
    assert dt == dt_expect

def test_destination_path_with_take_date(configs):
    expected_path = os.path.join(configs['DESTINATION_FOLDER'], '2020', '05', '10', 'take_date.jpg')
    new_path = destination_path('./test_assets/source/take_date.jpg')
    assert new_path == expected_path

def test_destination_path_without_take_date(configs):
    expected_path = os.path.join(configs['DESTINATION_FOLDER'], '2020', '05', '10', 'no_date.png')
    new_path = destination_path('./test_assets/source/no_date.png')
    assert new_path == expected_path