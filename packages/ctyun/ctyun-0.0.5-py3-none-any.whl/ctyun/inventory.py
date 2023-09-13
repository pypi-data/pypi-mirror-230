#!/usr/bin/env python3

import hashlib
import hmac
import base64
import requests
import datetime
import yaml
import os
import configparser

class Request(object):
    configFile = None
    accessKey = None
    secretKey = None
    regionId = None
    api = None
    url = None
    extra_headers = None
    request_method = None
    servicePath = None
    headers = None
    content = None
    content_list = None
    request_headers = None
    json = None
    def __init__(self, region_id=None, api=None, **kwargs):
            user_home = os.environ.get('HOME')
            if not self.configFile:
                self.configFile = user_home + '/.ctyun/credential'
            _configs = configparser.ConfigParser()
            _configs.read(self.configFile)
            self.accessKey = _configs['default']['accessKey']
            self.secretKey = _configs['default']['secretKey']
            self.requestDate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S") + ' CST'
            request_headers = dict()
            extra_headers = dict()
            content_list = list()
            api_yml = '/home/dmc-inventory-user/.ctyun/api.yml'
            with open(api_yml, 'r') as f:
                _apis = yaml.safe_load(f)
            apis_dict = _apis['apis']
            if api in apis_dict:
                self.api = api
                self.request_method = apis_dict[api]['method']
                self.servicePath = apis_dict[api]['servicePath']
                self.headers = apis_dict[api]['headers']
                self.url = 'https://api.ctyun.cn' + self.servicePath
                """ Content"""
                if 'headers' in apis_dict[api]:
                    for _ in apis_dict[api]['headers']:
                        self.content = '\n'.join(content_list)
                        self.content_list = content_list
            else:
                self.api = 'no_api_defined_yet'
            extra_headers['regionId'] = region_id
            self.extra_headers = extra_headers
            ''' auth: contentMD5, url, headers '''
            contentmd5_bytes = hashlib.md5(self.content.encode()).digest()
            contentmd5 = base64.b64encode(contentmd5_bytes).decode()
            request_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S") + ' CST'
            """ hmac
            def gen_hmac(contentMD5, requestDate, servicePath):
                hmac_string = contentMD5 + '\n' + requestDate + '\n' + servicePath
                return base64.b64encode(
                    hmac.new(secretKey.encode(), hmac_string.encode(), digestmod=hashlib.sha1).digest()).decode()
            """
            hmac_string = contentmd5 + '\n' + request_date + '\n' + self.servicePath
            hmac_base64 = base64.b64encode(hmac.new(self.secretKey.encode(), hmac_string.encode(), digestmod=hashlib.sha1).digest()).decode()
            self.hmac_string = hmac_string
            self.hmac_base64 = hmac_base64
            """
            def gen_public_headers(accessKey, contentMD5, requestDate, hmac, platform):
                headers = {
                    'accessKey': accessKey,
                    'contentMD5': contentMD5,
                    'requestDate': requestDate,
                    'hmac': hmac,
                    'platform': platform,
                }
                return headers
            """
            request_headers = {
                'accessKey': self.accessKey,
                'contentMD5': contentmd5,
                'requestDate': request_date,
                'hmac': hmac_base64,
                'platform': '3',
            }
            request_headers.update(extra_headers)
            """ kargs """
            for key, value in kwargs.items():
                request_headers[key] = value
            self.request_headers = request_headers
            """ data/payload """
            payload = request_headers
            if self.request_method == 'POST':
                _r = requests.request(self.request_method, self.url, headers=request_headers, data=payload)
            else:
                _r = requests.request(self.request_method, self.url, headers=request_headers, params=request_headers)
            ''' Return everything back'''
            self.json = _r.json()
