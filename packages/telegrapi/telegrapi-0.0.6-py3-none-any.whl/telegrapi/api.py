# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 20:22:44 2023

@author: kunth
"""
from __future__ import annotations
import json
import requests

from telegrapi.method import Method

# Source: https://core.telegram.org/bots/api
# https://api.telegram.org/<<your_bot_api_token>>/sendMessage?chat_id=@<<channel_name>>&text=Hello



class TEngine:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{token}'

    def send(self, message: Chat) -> dict:
        global res
        url = f'{self.base_url}/{message.method}'
        res = requests.post(url, data=message.data, files=message.files)
        res = res.content.decode('utf-8')
        res = json.loads(res)
        return res


class Chat:
    chat_id: str
    _data: dict  = None
    _files: dict = None
    _method: Method = None
    _attatch_path:str = None
    
    def __init__(self, chat_id: str, bot: TEngine = None, parse_mode:str = 'HTML'):
        self.chat_id = chat_id
        self.parse_mode = parse_mode
        self.bot = bot
    
    def message(self, msg: str) -> Chat:
        self._method = Method.sendMessage
        self._data = {
                'chat_id': self.chat_id,
                'parse_mode': self.parse_mode,
                'text': msg,
            }
        return self
    
    def json(self, data:dict) -> Chat:
        message = json.dumps(data, ensure_ascii=False, indent=4)
        return self.message(message)
    
    def file(self, filepath: str, caption: str = None) -> Chat:
        self._method = Method.sendDocument
        self._attatch_path = filepath
        self._data = {
                'chat_id': self.chat_id,
                'parse_mode': self.parse_mode,
                'caption': caption,
            }
        return self
    
    def send(self, bot: TEngine = None) -> dict:
        bot = bot if bot else self.bot
        if self._attatch_path:
            with open(self._attatch_path, 'rb') as f:
                self._files = { 'document': f }
                return bot.send(self)
        return bot.send(self)
    
    @property
    def method(self) -> str:
        return self._method
    
    @property
    def data(self) -> dict:
        return self._data
    
    @property
    def files(self) -> dict:
        return self._files
