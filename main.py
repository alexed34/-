# для проверяющего
# у меня сомнения что я все сделал правильно с исключениями, постарался выжать из себя все. 
# если неправильно то буду благодарен за пример правильного кода что бы понять как это делается на практике.

import requests
import os
import random
from dotenv import load_dotenv


def get_request(url):
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


def write_image(path, data):
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


def save_comic_server(access_token, server, photo, hashh):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {'group_id': '189760742', 'access_token': access_token, 'v': '5.103', 'server': server,
              'photo': photo, 'hash': hashh}
    response = requests.post(url, params=params)
    response.raise_for_status()
    response = response.json().get('response')[0]
    data = {'owner_id': response['owner_id'], 'media_id': response['id']}
    return data


def publish_comic_server(access_token, data, message):
    url = 'https://api.vk.com/method/wall.post'
    attachments = f"photo{str(data['owner_id'])}_{str(data['media_id'])}"
    params = {'access_token': access_token, 'v': '5.103', 'owner_id': '-189760742', 'from_group': '1',
              'message': message, 'attachments': attachments}
    response = requests.get(url, params=params)
    return response.json()


def raise_for_error_vk(response):
    if 'error' in response:
        print('error in request in VK')
        print(response.get('error'))
        raise ValueError


def main():
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    path = 'images'
    group_id = '189760742'
    os.makedirs(path, exist_ok=True)
    current_comic = get_request('https://xkcd.com/info.0.json')['num']
    num = str(random.randint(1, current_comic))
    data_comic = get_response_comic(num, get_request)
    write_image(path, data_comic)
    try:
        url = 'https://api.vk.com/method/photos.getWallUploadServer'
        params = {'group_id': group_id, 'access_token': access_token, 'v': '5.103'}
        server_address_for_downloading_pictures = get_request(requests.get(url, params=params).url)
        raise_for_error_vk(server_address_for_downloading_pictures)
        upload_url = server_address_for_downloading_pictures['response']['upload_url']
        data_comic_server = upload_comic_server(data_comic['name_image'], upload_url)
        server = data_comic_server['server']
        photo = data_comic_server['photo']
        str_hash = data_comic_server['hash']
        response_save_comic = save_comic_server(access_token, server, photo, str_hash, )
        publish_comic_server(access_token, response_save_comic, data_comic['comment'])
    except ValueError:
        print('ValueError')
    except KeyError:
        print('KeyError - ошибка')

    finally:
        os.remove(f"{path}/{data_comic['name_image']}")


if __name__ == '__main__':
    main()
