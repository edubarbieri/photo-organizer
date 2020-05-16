import os
import pytest
import datetime
from photo_organizer import get_config, default_config, img_date, destination_path, is_image, process_image
import platform
import shutil

@pytest.fixture(scope="module", autouse=True)
def configure():
    default_config['SOURCE_FOLDER'] = './test_assets/source'
    default_config['DESTINATION_FOLDER'] = './test_assets/destination'
    default_config['OPERATION'] = 'COPY'


@pytest.fixture
def configs():
    return default_config


@pytest.fixture
def take_date_source_path(configs):
    return os.path.join(configs['SOURCE_FOLDER'], 'take_date.jpg')


@pytest.fixture
def take_date_dest_path(configs):
    return os.path.join(configs['DESTINATION_FOLDER'], '2020', '05', 'take_date.jpg')


@pytest.fixture
def file_not_image_source_path(configs):
    return os.path.join(configs['SOURCE_FOLDER'], 'text_file.txt')


def test_get_config_default_value(configs):
    """Teste if return default configs values"""
    assert get_config('SOURCE_FOLDER') == configs['SOURCE_FOLDER']


def test_get_config_replace_by_os_env():
    """Teste if return default configs values"""
    value = 'MIMIMIMIMIMIMI'
    os.environ["SOURCE_FOLDER"] = value
    assert get_config('SOURCE_FOLDER') == value


def test_image_date_with_take_date():
    dt_expect = datetime.datetime(2020, 5, 10, 23, 5, 40)
    dt = img_date('./test_assets/source/take_date.jpg')
    assert dt == dt_expect


def test_image_date_without_take_date():
    dt_expect = datetime.datetime(2020, 5, 10, 23, 9, 15, 171856)
    dt = img_date('./test_assets/source/no_date.png')
    assert dt == dt_expect


def test_destination_path_with_take_date(configs, take_date_dest_path):
    new_path = destination_path('./test_assets/source/take_date.jpg')
    assert new_path == take_date_dest_path


def test_destination_path_without_take_date(configs):
    expected_path = os.path.join(
        configs['DESTINATION_FOLDER'], '2020', '05', 'no_date.png')
    new_path = destination_path('./test_assets/source/no_date.png')
    assert new_path == expected_path


def test_is_image_with_image_file(configs):
    assert is_image(os.path.join(
        configs['SOURCE_FOLDER'], 'take_date.jpg')) == True
    assert is_image(os.path.join(
        configs['SOURCE_FOLDER'], 'no_date.png')) == True


def test_is_image_without_image_file(file_not_image_source_path):
    assert is_image(file_not_image_source_path) == False


def test_process_image_with_invalid_image(configs, file_not_image_source_path):
    process_image(file_not_image_source_path)
    assert os.path.exists(os.path.join(configs['DESTINATION_FOLDER'], 'text_file.txt')) == False



def test_process_image_copy_image(configs, take_date_source_path, take_date_dest_path):
    default_config['OPERATION'] = 'COPY'
    process_image(take_date_source_path)
    assert os.path.exists(take_date_dest_path) == True
    shutil.rmtree(os.path.join(configs['DESTINATION_FOLDER'], '2020'))

def test_process_image_move_image(configs, take_date_source_path, take_date_dest_path):
    default_config['OPERATION'] = 'MOVE'
    process_image(take_date_source_path)
    assert os.path.exists(take_date_source_path) == False
    assert os.path.exists(take_date_dest_path) == True

    shutil.move(take_date_dest_path, take_date_source_path)
    shutil.rmtree(os.path.join(configs['DESTINATION_FOLDER'], '2020'))
