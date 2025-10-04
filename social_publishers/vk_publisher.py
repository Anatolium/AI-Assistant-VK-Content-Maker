import requests

class VKPublisher:
    def __init__(self, vk_api_key, group_id, debug=False):
        self.vk_api_key = vk_api_key
        self.group_id = group_id
        self.debug = debug  # если True — печатаем все ответы VK API

    def _log(self, label, data):
        """Удобный метод для печати JSON-ответов VK API"""
        if self.debug:
            print(f"\n--- {label} ---")
            print(data)

    def upload_photo(self, image_url):
        # Получаем upload_url
        upload_url_response = requests.get(
            'https://api.vk.com/method/photos.getWallUploadServer',
            params={
                'access_token': self.vk_api_key,
                'v': '5.199',
                'group_id': self.group_id
            }
        ).json()
        self._log("upload_url_response", upload_url_response)

        if 'error' in upload_url_response:
            raise Exception(f"VK API error (getWallUploadServer): {upload_url_response['error']['error_msg']}")

        upload_url = upload_url_response['response']['upload_url']

        # Загружаем картинку
        image_data = requests.get(image_url).content
        upload_response = requests.post(upload_url, files={'photo': ('image.jpg', image_data)}).json()
        self._log("upload_response", upload_response)

        if 'photo' not in upload_response or 'server' not in upload_response or 'hash' not in upload_response:
            raise Exception(f"VK upload error: {upload_response}")

        # Сохраняем фото
        save_response = requests.get(
            'https://api.vk.com/method/photos.saveWallPhoto',
            params={
                'access_token': self.vk_api_key,
                'v': '5.199',
                'group_id': self.group_id,
                'photo': upload_response['photo'],
                'server': upload_response['server'],
                'hash': upload_response['hash']
            }
        ).json()
        self._log("save_response", save_response)

        if 'error' in save_response:
            raise Exception(f"VK API error (saveWallPhoto): {save_response['error']['error_msg']}")

        photo_id = save_response['response'][0]['id']
        owner_id = save_response['response'][0]['owner_id']

        return f'photo{owner_id}_{photo_id}'

    def publish_post(self, content, image_url=None, timestamp=None):
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.199',
            'owner_id': f'-{self.group_id}',
            'message': content
        }

        if image_url:
            attachment = self.upload_photo(image_url)
            params['attachments'] = attachment

        if timestamp:
            params['publish_date'] = timestamp

        response = requests.post('https://api.vk.com/method/wall.post', params=params).json()
        self._log("wall.post response", response)

        if 'error' in response:
            raise Exception(f"VK API error (wall.post): {response['error']['error_msg']}")

        return response['response']['post_id']
