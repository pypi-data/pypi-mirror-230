# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import json
import yaml

from ...extend.config import ConfigureBase

from .client import NacosConfig


class Configure(ConfigureBase):
    """配置类
    """

    __slots__ = [r'_format', r'_client']

    def __init__(
            self, servers, data_id, *,
            protocol=None, endpoint=None, group=None, namespace=None
    ):

        super().__init__()

        self._format = None

        self._client = NacosConfig(
            self._reload_config, servers, data_id,
            protocol=protocol, endpoint=endpoint, group=group, namespace=namespace
        )

    def _reload_config(self, content):

        self._parser.clear()

        if self._format == r'text':
            self._parser.read_string(content)
        elif self._format == r'json':
            self._parser.read_dict(json.loads(content))
        elif self._format == r'yaml':
            self._parser.read_dict(yaml.load(content, yaml.Loader))

        self._load_options()

    def release(self):

        self._client.close()
        self._parser.clear()

    def read(self):

        self._format = r'text'
        self._client.open()

    def read_json(self):

        self._format = r'json'
        self._client.open()

    def read_yaml(self):

        self._format = r'yaml'
        self._client.open()
