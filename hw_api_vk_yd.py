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
            photo_info_dct['file_name'] = f"{photo['likes']['count']}_{file_time}.jpg" 
            photo_info_dct['url'] = photo['sizes'][-1]['url']
            photo_info_dct['size'] = photo['sizes'][-1]['type']
            photo_info_lst.append(photo_info_dct)

         return photo_info_lst
      except KeyError:
         return None

class YDClient:
   base_url_yd = 'https://cloud-api.yandex.net/v1/disk/'

   def __init__(self, yd_token):
      
      self.token = f'OAuth {yd_token}'

   def create_folder_yd(self, folder_name):

      headers = {'Authorization': self.token}
      response = requests.put(f'{self.base_url_yd}resources?path={folder_name}', headers=headers)
      if 200 <= response.status_code < 300:
            print('Folder successfully created!')
            return response.json()
      else:
         print('Folder creation failed!')
         print(response.json()['description'])
         return False
      
   
   def download_images(self, file_url, file_name, folder_name):
      headers = {'Authorization': self.token}
      params = {'url': file_url, 'path': f'{folder_name}/{file_name}', 'fields': file_name, 'overwrite': 'true'}
      response = requests.post(f'{self.base_url_yd}resources/upload', headers=headers, params=params)
      return response.json()




vk = VKClient(access_token, user_id)
yd = YDClient(yd_token)

photos = vk.get_profile_photos()
folder_name = 'vk_photos'
yd.create_folder_yd(folder_name)

for photo in tqdm(photos, desc='Uploading photos'):
   file_url = photo['url']
   file_name = photo['file_name']
   yd.download_images(file_url, file_name, folder_name)