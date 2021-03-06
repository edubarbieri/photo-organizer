
import os
import time
import platform
import pathlib
import shutil
import logging
from PIL import Image, UnidentifiedImageError
from util import safe_name
from datetime import datetime
import argparse

logging.basicConfig(
    format='%(asctime)s :: %(levelname)s :: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    level=logging.INFO)

default_config = {
    'SOURCE_FOLDER': 'teste/source',
    'DESTINATION_FOLDER': 'teste/destination',
    'OPERATION': 'MOVE'
}

image_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.heic']
videos_formats = ['.mp4', '.wmv', '.avi']


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
    std_fmt = '%Y:%m:%d'
    # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
            (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
            (306, 37520), ]  # (DateTime, SubsecTime)
    with  Image.open(image_path) as img:
        if not hasattr(img, '_getexif'):
            return datetime.fromtimestamp(creation_date(image_path))
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
        full = dat.split(' ')[0]
        return datetime.strptime(full.replace('\x00', '').strip(), std_fmt)
        


def destination_path(path):
    take_date = img_date(path)
    if take_date is None:
        return None

    format_folder = take_date.strftime(F"%Y{os.sep}%m")
    base_name = os.path.basename(path)
    dest_path = os.path.join(get_config(
        'DESTINATION_FOLDER'), format_folder, base_name)
    return safe_name(dest_path)


def is_image(name):
    _, ext = os.path.splitext(name)
    return ext.lower() in image_formats

def is_video(name):
    _, ext = os.path.splitext(name)
    return ext.lower() in videos_formats

def process_image(image_path):
    logging.info(f'processing file {image_path}')
    if is_video(image_path):
        move_to_videos(image_path)
        return
    if not is_image(image_path):
        move_to_trash(image_path)
        return
    #process image moving
    try:
        new_path = destination_path(image_path)
    except UnidentifiedImageError as error:
        logging.error(f'Could not open image {image_path}')
        move_to_error(image_path)
    else:
        if not new_path:
            logging.error(f'Could not determine new path for image {image_path}')
            return
        operation = get_config('OPERATION')
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if operation == 'MOVE':
            logging.info(f'moving {image_path} to {new_path}...')
            shutil.move(image_path, new_path)
        elif operation == 'COPY':
            logging.info(f'copying {image_path} to {new_path}...')
            shutil.copy(image_path, new_path)
        else:
            logging.error('Please configure env OPERATION to perform operation...')

def move_to_error(image_path):
    base_name = os.path.basename(image_path)
    dest_path = safe_name(os.path.join(get_config('DESTINATION_FOLDER'), 'error', base_name))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    logging.info(f'moving {image_path} to ERROR {dest_path}...')
    shutil.move(image_path, dest_path)

def move_to_videos(image_path):
    base_name = os.path.basename(image_path)
    dest_path = safe_name(os.path.join(get_config('DESTINATION_FOLDER'), 'videos', base_name))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    logging.info(f'moving {image_path} to VIDEOS {dest_path}...')
    shutil.move(image_path, dest_path)

def move_to_trash(image_path):
    base_name = os.path.basename(image_path)
    dest_path = safe_name(os.path.join(get_config('DESTINATION_FOLDER'), 'trash', base_name))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    logging.info(f'moving {image_path} to TRASH {dest_path}...')
    shutil.move(image_path, dest_path)    

def arg_parsers():
    # Initiate the parser
    parser = argparse.ArgumentParser(description='Photo organizer - script to organizer photo by take date.')
    parser.add_argument("-V", "--version", help="show program version.", action="store_true")
    parser.add_argument("-s", "--source", help="source folder with unorganized photos. SOURCE_FOLDER env replace this parameter.", required=False)
    parser.add_argument("-d", "--destination", help="destination folder to move/copy photos by take date. DESTINATION_FOLDER env replace this parameter.", required=False)
    parser.add_argument("-o", "--operation", help="move or copy photos to destionarion. OPERATION env replace this parameter.", choices=['COPY', 'MOVE'], default='COPY', required=False)
    # Read arguments from the command line
    return parser.parse_args()

def update_config_with_args(args):
    global default_config
    if args.source:
        default_config['SOURCE_FOLDER'] = args.source
    if args.destination:
        default_config['DESTINATION_FOLDER'] = args.destination
    if args.operation == 'COPY':
        default_config['OPERATION'] = 'COPY'
    if args.operation == 'MOVE':
        default_config['OPERATION'] = 'MOVE'


def main():
    args = arg_parsers()
    if args.version:
        print('photo organizer version 1.0.3')
        return
    logging.info("Starting photo organizer V: 1.0.3")
    update_config_with_args(args)
    for root, _, files in os.walk(get_config('SOURCE_FOLDER')):
        for file in files:
            process_image(os.path.join(root, file))

if __name__ == '__main__':
    main()

