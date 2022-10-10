import os
from random import randint
from time import sleep
import sys
import logging
from logging.handlers import RotatingFileHandler

import requests
import requests.exceptions
from dotenv import load_dotenv

logger = logging.getLogger(__file__)
API_VERSION = 5.131
SENDER = 0
INTERVAL = 86400
FILEPATH = './comics.png'


def download_image(url):
    logger.info('download_image() was called')
    response = requests.get(url)
    response.raise_for_status()
    with open(FILEPATH, 'wb') as file:
        file.write(response.content)


def receive_comic(comics_number=''):
    logger.info('receive_comic() was called')
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    unpacked_response = response.json()
    if not comics_number:
        return unpacked_response.get('num')
    img_link = unpacked_response.get('img')
    comics_comment = unpacked_response.get('alt')
    download_image(img_link)
    return comics_comment


def get_server_address_for_uploading_photo(access_token, group_id):
    logger.info('get_server_address_for_uploading_photo() was called')
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {'access_token': access_token, 'v': API_VERSION,
              'group_id': group_id
              }
    response = requests.get(url, params=params)
    response.raise_for_status()
    unpacked_response = response.json()
    return unpacked_response.get('response').get('upload_url')


def upload_img_to_server(url):
    logger.info('upload_img_to_server() was called')
    with open(FILEPATH, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


def save_img_to_group_album(access_token, group_id, server_response):
    logger.info('save_img_to_group_album() was called')
    params = {'access_token': access_token, 'v': API_VERSION,
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


def post_comic_on_group_wall(access_token, group_id, comics_comment,
                             photo_owner_id, photo_id):
    logger.info('post_comic_on_group_wall() was called')
    url = 'https://api.vk.com/method/wall.post'
    params = {'access_token': access_token, 'v': API_VERSION,
              'owner_id': f'-{group_id}', 'from_group': SENDER,
              'attachments': f'photo{photo_owner_id}_{photo_id}',
              'message': comics_comment,
              }
    response = requests.post(url, params=params)
    response.raise_for_status()
    os.remove(FILEPATH)


def main():
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                        format='%(name)s - %(levelname)s '
                               '- %(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=2)
    logger.addHandler(handler)
    load_dotenv()
    access_token = os.getenv('COMICS_ACCESS_TOKEN')
    group_id = os.getenv('COMICS_GROUP_ID')
    while True:
        try:
            comics_amount = receive_comic()
            random_number = randint(1, comics_amount)
            comics_comment = receive_comic(random_number)
            server_address = get_server_address_for_uploading_photo(
                                              access_token, group_id)
            server_response = upload_img_to_server(server_address)
            photo_owner_id, photo_id = save_img_to_group_album(access_token,
                                                               group_id,
                                                               server_response)
            post_comic_on_group_wall(access_token, group_id, comics_comment,
                                     photo_owner_id, photo_id)
            sleep(INTERVAL)
        except requests.exceptions.HTTPError as http_er:
            logger.warning(f'\n{http_er}\n')
            sys.stderr.write(f'\n{http_er}\n')
            sleep(30)
            continue
        except requests.exceptions.ConnectionError as connect_er:
            logger.warning(f'\n{connect_er}\n')
            sys.stderr.write(f'\n{connect_er}\n')
            sleep(30)
            continue


if __name__ == '__main__':
    main()
