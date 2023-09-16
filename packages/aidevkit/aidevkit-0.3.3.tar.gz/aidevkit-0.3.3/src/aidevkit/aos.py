# -*-coding:utf-8 -*-
"""
:创建时间: 2023/8/25 8:49
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

from abc import abstractmethod

if False:
    from typing import *
import os
import logging

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import torch


class Saver(object):
    def __init__(self, make_obj_callback, file_path, save_interval=256):
        self.obj = make_obj_callback()
        self.file_path = file_path
        self.save_interval = save_interval
        self.count = 0
        if os.path.isfile(self.local_path) or self.object_exists():
            logging.debug('load_object')
            self.load_object()

    @property
    def local_path(self):
        return os.path.join('./aos_work', self.file_path)

    def load_object(self):
        if not os.path.isfile(self.local_path):
            if not os.path.isdir('./aos_work'):
                os.mkdir('./aos_work')
            self.download_object()

        self.obj.load_state_dict(torch.load(self.local_path))

    def save_object(self):
        if not os.path.isdir('./aos_work'):
            os.mkdir('./aos_work')

        torch.save(self.obj.state_dict(), self.local_path)

        self.upload_object()

    def step(self):
        self.count += 1
        if self.count >= self.save_interval:
            self.save_object()
            self.count = 0
            logging.debug('auto_save')

    def must_save(self):
        self.save_object()
        logging.debug('must_save')

    @abstractmethod
    def object_exists(self):
        pass

    @abstractmethod
    def upload_object(self):
        pass

    @abstractmethod
    def download_object(self):
        pass


class CosSaver(Saver):
    @staticmethod
    def get_client():
        # 配置信息
        config = CosConfig(
            Region=os.environ['COS_Region'],
            SecretId=os.environ['COS_SecretId'],
            SecretKey=os.environ['COS_SecretKey'],
        )

        # 创建客户端
        client = CosS3Client(config)

        return client

    def object_exists(self):
        # 创建客户端
        client = self.get_client()

        response = client.object_exists(
            Bucket=os.environ['COS_Bucket'],
            Key=self.file_path,
        )

        return response

    def download_object(self):
        # 创建客户端
        client = self.get_client()

        client.download_file(
            Bucket=os.environ['COS_Bucket'],
            Key=self.file_path,
            DestFilePath=self.local_path,
        )

    def upload_object(self):
        # 创建客户端
        client = self.get_client()

        response = client.upload_file(
            Bucket=os.environ['COS_Bucket'],
            LocalFilePath=self.local_path,
            Key=self.file_path,
        )
        logging.debug('upload_file {}'.format(response))


class AutoDLSaver(Saver):
    root = '/root/autodl-fs'

    def object_exists(self):
        return os.path.isfile(os.path.join(self.root, self.file_path))

    def upload_object(self):
        os.system('cp {} {}'.format(self.local_path, os.path.join(self.root, self.file_path)))

    def download_object(self):
        os.system('cp {} {}'.format(os.path.join(self.root, self.file_path), self.local_path))


__all__ = ['Saver', 'CosSaver', 'AutoDLSaver']
