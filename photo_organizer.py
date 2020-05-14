import os
from datetime import datetime
import time
import platform
from PIL import Image
import shutil
from util import safe_name
import pathlib

default_config = {
    'SOURCE_FOLDER': 'teste/source',
    'DESTINATION_FOLDER': 'teste/destination',
    'OPERATION': 'MOVE'
}

image_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.heic']


def get_config(key: str) -> str:
    return os.environ.get(key, default_config[key])


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def img_date(image_path):
    """returns the image date from image (if available)\nfrom Orthallelous"""
    std_fmt = '%Y:%m:%d %H:%M:%S.%f'
    # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
            (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
            (306, 37520), ]  # (DateTime, SubsecTime)
    exif = Image.open(image_path)._getexif()
    if not exif:
        return datetime.fromtimestamp(creation_date(image_path))

    for tag in tags:
        dat = exif.get(tag[0])
        sub = exif.get(tag[1], 0)

        # PIL.PILLOW_VERSION >= 3.0 returns a tuple
        dat = dat[0] if type(dat) == tuple else dat
        sub = sub[0] if type(sub) == tuple else sub
        if dat != None:
            break

    if dat == None:
        return datetime.fromtimestamp(creation_date(image_path))
    full = '{}.{}'.format(dat, sub)
    return datetime.strptime(full, std_fmt)


def destination_path(path):
    take_date = img_date(path)
    if take_date is None:
        return None

    format_folder = take_date.strftime(F"%Y{os.sep}%m{os.sep}%d")
    base_name = os.path.basename(path)
    dest_path = os.path.join(get_config(
        'DESTINATION_FOLDER'), format_folder, base_name)
    return safe_name(dest_path)


def is_image(name):
    _, ext = os.path.splitext(name)
    return ext in image_formats

def process_image(image_path):
    if not is_image(image_path):
        return
    new_path = destination_path(image_path)
    if not new_path:
        print(f'Could not determine new path for image {image_path}')
        return
    operation = get_config('OPERATION')
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    if operation == 'MOVE':
        print(f'moving {image_path} to {new_path}...')
        shutil.move(image_path, new_path)
    elif operation == 'COPY':
        print(f'copying {image_path} to {new_path}...')
        shutil.copy(image_path, new_path)
    else:
        print(f'Please configure env OPERATION to perform operation...')


if __name__ == '__main__':
    for root, _, files in os.walk(get_config('SOURCE_FOLDER')):
        for file in files:
            process_image(os.path.join(root, file))
