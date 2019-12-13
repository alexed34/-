import requests
import os
import random
from dotenv import load_dotenv


def get_requests(url):
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    return response


def get_response_comic(num, get_requests):
    url = f'https://xkcd.com/{num}/info.0.json'
    response = get_requests(url)
    url_img = response.get('img')
    data = {'response_image': requests.get(url_img), 'name_image': f"{response.get('num')}.png",
            'comment': response.get('alt')}
    return data


def write_images(path, data):
    with open(os.path.join(path, data['name_image']), 'wb') as f:
        f.write(data['response_image'].content)


def upload_comic_server(name, url):
    with open(f'images/{name}', 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()


def save_comic_server(ACCESS_TOKEN, server, photo, hashh):
    url = 'https://api.vk.com/method/photos.saveWallPhoto?'
    params = {'group_id': '189760742', 'access_token': ACCESS_TOKEN, 'v': '5.103', 'server': server,
              'photo': photo, 'hashh': hashh}
    response = requests.post(url, params=params)
    response.raise_for_status()
    response = response.json().get('response')[0]
    data = {'owner_id': response['owner_id'], 'media_id': response['id']}
    return data


def publish_comic_server(ACCESS_TOKEN, data, message):
    url = 'https://api.vk.com/method/wall.post?'
    attachments = f"photo{str(data['owner_id'])}_{str(data['media_id'])}"
    params = {'access_token': ACCESS_TOKEN, 'v': '5.103', 'owner_id': '-189760742', 'from_group': '1',
              'message': message, 'attachments': attachments}
    response = requests.get(url, params=params)
    return response.json()


def main():
    load_dotenv()
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    path = 'images'
    group_id = '189760742'
    os.makedirs(path, exist_ok=True)
    num = str(random.randint(1, 2240))
    data_comic = get_response_comic(num, get_requests)
    write_images(path, data_comic)
    server_address_for_downloading_pictures = get_requests \
        (f'https://api.vk.com/method/photos.getWallUploadServer?group_id={group_id}&access_token={ACCESS_TOKEN}&v=5.103') \
        .get('response')
    upload_url = server_address_for_downloading_pictures['upload_url']
    json_comic_server = upload_comic_server(data_comic['name_image'], upload_url)
    server = json_comic_server['server']
    photo = json_comic_server['photo']
    hashh = json_comic_server['hashh']
    response_save_comic = save_comic_server(ACCESS_TOKEN, server, photo, hashh)
    publish_comic_server(ACCESS_TOKEN, response_save_comic, data_comic['comment'])
    os.remove(f"{path}/{data_comic['name_image']}")


if __name__ == '__main__':
    main()
