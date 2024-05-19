import requests
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm
from time import sleep
from datetime import datetime as dt
from pprint import pprint

load_dotenv()

yd_token = os.getenv('YD_TOKEN')
access_token = os.getenv('VK_TOKEN')
user_id = os.getenv('VK_ID')

class VKClient:
   api_base_url = 'https://api.vk.com/method'

   def __init__(self, access_token, user_id):

      self.token = access_token
      self.user_id = user_id

   def get_common_params(self):

      return {'access_token': self.token, 'v': '5.131'}
   
   def _build_url(self, api_method):

      return f'{self.api_base_url}/{api_method}'
   
   def users_info(self):

      params = self.get_common_params()
      params.update({'user_ids': self.user_id})
      response = requests.get(self._build_url('users.get'), params = params)
      return response.json()
   
   def get_profile_photos(self):

      params = self.get_common_params()
      params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1})
      response = requests.get(self._build_url('photos.get'), params = params)
      try:
         all_photo = response.json()['response']['items']
         photo_info_lst = []
         for photo in all_photo:
            file_time = dt.fromtimestamp(photo['date']).strftime('%Y_%m_%d')
            photo_info_dct = {}
            # не пойму, как здесь реализовать добавление даты к имени файла с повторяющимся количеством лайков
            photo_info_dct['date'] = file_time
            photo_info_dct['file_name'] = f"{photo['likes']['count']}.jpg" 
            photo_info_dct['url'] = photo['sizes'][-1]['url']
            photo_info_dct['size'] = photo['sizes'][-1]['type']
            photo_info_lst.append(photo_info_dct)

         return photo_info_lst
      except KeyError:
         return None

class YDClient:
   base_url_yd = 'https://cloud-api.yandex.net'

   def __init__(self, yd_token):
      
      self.token = f'OAuth {yd_token}'

   def create_folder_yd(self):

      params = {'path': 'image_vk'}
      headers = {'Authorization': self.token}
      response = requests.put(f'{self.base_url_yd}/v1/disk/resources', params=params, headers=headers)
      if 200 <= response.status_code < 300:
            print('Folder successfully created!')
            return response.json()['href']
      else:
         print('Folder creation failed!')
         print(response.json()['description'])
         return False
      
   
   
   def download_images(self):
      params = {'path': self.create_folder_yd()}
      # photo_info_lst = VKClient.get_profile_photos() каким образом здесь настроить взаимодействие, нет понимания совсем
      for photo_info in tqdm(photo_info_lst, desc='Downloading', unit='photo'):
         url = photo_info['url']
         response = requests.post(url, params=params)
      # и что дальше, тоже затык




vk = VKClient(access_token, user_id)
yd = YDClient(yd_token)
# pprint(vk.get_profile_photos())
print(yd.create_folder_yd())
# print(yd.download_images())
