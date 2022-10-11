import os
from random import randint
import sys
import logging
from logging.handlers import RotatingFileHandler

import requests
import requests.exceptions
from dotenv import load_dotenv

logger = logging.getLogger(__file__)


def download_image(url, filepath):
    logger.info('download_image() was called')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        file.write(response.content)


def receive_comic(filepath, comics_number=''):
    logger.info('receive_comic() was called')
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    unpacked_response = response.json()
    if not comics_number:
        return unpacked_response.get('num')
    img_link = unpacked_response.get('img')
    comics_comment = unpacked_response.get('alt')
    download_image(img_link, filepath)
    return comics_comment


def get_server_address_for_uploading_photo(
        access_token, api_version, group_id):
    logger.info('get_server_address_for_uploading_photo() was called')
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    unpacked_response = response.json()
    return unpacked_response.get('response').get('upload_url')


def upload_img_to_server(filepath, url):
    logger.info('upload_img_to_server() was called')
    with open(filepath, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


def save_img_to_group_album(
        access_token, api_version,
        group_id, server_response):
    logger.info('save_img_to_group_album() was called')
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id,
    }
    params.update(server_response)
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, params=params)
    response.raise_for_status()
    unpacked_response = response.json()
    photo_id = unpacked_response.get('response')[0].get('id')
    photo_owner_id = unpacked_response.get('response')[0].get('owner_id')
    return photo_owner_id, photo_id


def post_comic_on_group_wall(
        access_token, api_version,
        group_id, comics_comment, sender,
        photo_owner_id, photo_id):
    logger.info('post_comic_on_group_wall() was called')
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': f'-{group_id}',
        'from_group': sender,
        'attachments': f'photo{photo_owner_id}_{photo_id}',
        'message': comics_comment,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


def main():
    logging.basicConfig(
        filename='app.log',
        filemode='w',
        level=logging.INFO,
        format='%(name)s - %(levelname)s - %(asctime)s - %(message)s',
    )
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        filename='app.log',
        maxBytes=10000,
        backupCount=2
    )
    logger.addHandler(handler)
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN_TO_COMICS_VK')
    group_id = os.getenv('GROUP_ID_COMICS_VK')
    filepath = './comics.png'
    api_version = 5.131
    sender = 0
    try:
        comics_amount = receive_comic(filepath=filepath)
        random_number = randint(1, comics_amount)
        comics_comment = receive_comic(
            filepath=filepath,
            comics_number=random_number,
        )
        server_address = get_server_address_for_uploading_photo(
            access_token=access_token,
            api_version=api_version,
            group_id=group_id,
        )
        server_response = upload_img_to_server(
            filepath=filepath,
            server_address=server_address,
        )
        photo_owner_id, photo_id = save_img_to_group_album(
            access_token=access_token,
            api_version=api_version,
            group_id=group_id,
            server_response=server_response,
        )
        post_comic_on_group_wall(
            access_token=access_token,
            api_version=api_version,
            group_id=group_id,
            comics_comment=comics_comment,
            sender=sender,
            photo_owner_id=photo_owner_id,
            photo_id=photo_id,
        )
    except requests.exceptions.HTTPError as http_er:
        logger.warning(f'\n{http_er}\n')
        sys.stderr.write(f'\n{http_er}\n')
    except requests.exceptions.ConnectionError as connect_er:
        logger.warning(f'\n{connect_er}\n')
        sys.stderr.write(f'\n{connect_er}\n')
    finally:
        os.remove(filepath)


if __name__ == '__main__':
    main()
