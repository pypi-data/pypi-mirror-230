# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import requests

from ...extend.base import Utils
from ...extend.asyncio.future import Thread


DEFAULT_GROUP_NAME = r'DEFAULT_GROUP'
DEFAULT_PROTOCOL = r'http'
DEFAULT_REQUEST_TIMEOUT = 5
DEFAULT_PULLING_TIMEOUT = 30
DEFAULT_WEIGHT = 1

WORD_SEPARATOR = u'\x02'
LINE_SEPARATOR = u'\x01'


class NacosConfig:

    def __init__(
            self, listener, servers, data_id, *,
            protocol=None, endpoint=None, group=None, namespace=None,
            request_timeout=None, pulling_timeout=None
    ):

        self._task = Thread(target=self._do_task)

        self._listener = listener
        self._servers = Utils.split_str(servers, r',')

        self._protocol = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint = endpoint if endpoint is not None else r''
        self._namespace = namespace if namespace is not None else r''

        self._data_id = data_id
        self._group = group if group is not None else DEFAULT_GROUP_NAME

        self._content = r''
        self._content_hash = r''

        self._request_timeout = request_timeout if request_timeout is not None else DEFAULT_REQUEST_TIMEOUT
        self._pulling_timeout = pulling_timeout if pulling_timeout is not None else DEFAULT_PULLING_TIMEOUT

    def _do_task(self):

        while True:

            payload = {
                r'Listening-Configs': WORD_SEPARATOR.join(
                    [
                        self._data_id,
                        self._group,
                        self._content_hash,
                        self._namespace,
                    ]
                ) + LINE_SEPARATOR,
            }

            headers = {
                r'Long-Pulling-Timeout': str(self._pulling_timeout * 1000),
            }

            for server in self._servers:

                url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/cs/configs/listener'

                try:

                    resp = requests.post(
                        url, payload,
                        headers=headers, timeout=self._request_timeout + self._pulling_timeout
                    )

                    if resp.status_code == 200:
                        if resp.text:
                            Utils.log.info(f'nacos config pulling: {resp.text.strip()}')
                            self._listener(self.get_config())
                    else:
                        raise Exception(r'nacos config pulling error')

                except Exception as err:
                    Utils.log.error(str(err))
                    time.sleep(self._request_timeout)
                else:
                    break

            else:

                Utils.log.error(f'nacos config pulling failed: servers unusable')

    def open(self):

        self._listener(self.get_config())

        self._task.start()

    def close(self):

        self._task.stop()

    def get_config(self):

        params = {
            r'dataId': self._data_id,
            r'group': self._group,
        }

        if self._namespace:
            params[r'tenant'] = self._namespace

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/cs/configs'

            try:

                resp = requests.get(url, params, timeout=self._request_timeout)

                if resp.status_code == 200:
                    self._content = resp.text
                    self._content_hash = Utils.md5(self._content)
                else:
                    raise Exception(r'nacos get config error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos get config failed: servers unusable')

        return self._content


class NacosInstanceRegister:

    def __init__(
            self, servers, service_name, service_ip, service_port, heartbeat_interval, *,
            protocol=None, endpoint=None, group=None, namespace=None, cluster=None, weight=None,
            request_timeout=None
    ):

        self._task = Thread(target=self._do_task)

        self._servers = Utils.split_str(servers, r',')

        self._service_name = service_name
        self._service_ip = service_ip
        self._service_port = service_port

        self._protocol = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint = endpoint if endpoint is not None else r''
        self._namespace = namespace if namespace is not None else r''

        self._group = group if group is not None else DEFAULT_GROUP_NAME
        self._cluster = cluster
        self._weight = weight if weight is not None else DEFAULT_WEIGHT

        self._request_timeout = request_timeout if request_timeout is not None else DEFAULT_REQUEST_TIMEOUT
        self._heartbeat_interval = heartbeat_interval

    def _do_task(self):

        while True:

            payload = {
                r'serviceName': self._service_name,
                r'namespaceId': self._namespace,
                r'groupName': self._group,
                r'beat': Utils.json_encode(
                    {
                        r'serviceName': self._service_name,
                        r'ip': self._service_ip,
                        r'port': str(self._service_port),
                        r'weight': self._weight,
                        r'ephemeral': True,
                    }
                ),
            }

            for server in self._servers:

                url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance/beat'

                try:

                    resp = requests.put(url, payload, timeout=self._request_timeout)

                    if resp.status_code != 200:
                        raise Exception(r'nacos instance beat error')

                except Exception as err:
                    Utils.log.error(str(err))
                else:
                    break

            else:

                Utils.log.error(f'nacos instance beat failed: servers unusable')

            time.sleep(self._heartbeat_interval)

    def open(self):

        payload = {
            r'serviceName': self._service_name,
            r'ip': self._service_ip,
            r'port': self._service_port,
            r'namespaceId': self._namespace,
            r'weight': self._weight,
            r'enabled': True,
            r'healthy': True,
            r'groupName': self._group,
            r'ephemeral': True,
        }

        if self._cluster:
            payload[r'clusterName'] = self._cluster

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance'

            try:

                resp = requests.post(url, payload, timeout=self._request_timeout)

                if resp.status_code == 200:
                    self._task.start()
                    Utils.log.info(f'nacos instance register: {payload}')
                else:
                    raise Exception(r'nacos instance register error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos instance register failed: servers unusable')

    def close(self):

        self._task.stop()


class NacosInstanceQuery:

    def __init__(
            self, listener, servers, service_name, listener_interval, *,
            protocol=None, endpoint=None, group=None, namespace=None, cluster=None,
            request_timeout=None
    ):

        self._task = Thread(target=self._do_task)

        self._listener = listener
        self._servers = Utils.split_str(servers, r',')

        self._service_name = service_name

        self._protocol = protocol if protocol is not None else DEFAULT_PROTOCOL
        self._endpoint = endpoint if endpoint is not None else r''
        self._namespace = namespace if namespace is not None else r''

        self._group = group if group is not None else DEFAULT_GROUP_NAME
        self._cluster = cluster

        self._content = None
        self._content_hash = r''

        self._request_timeout = request_timeout if request_timeout is not None else DEFAULT_REQUEST_TIMEOUT
        self._listener_interval = listener_interval

    def _do_task(self):

        content_hash = self._content_hash

        while True:

            self._send_query()

            if content_hash != self._content_hash:
                Utils.log.info(f'nacos instance query: {self._content}')
                content_hash = self._content_hash
                self._listener(self._content)

            time.sleep(self._listener_interval)

    def _send_query(self):

        params = {
            r'serviceName': self._service_name,
            r'namespaceId': self._namespace,
            r'groupName': self._group,
            r'healthyOnly': True,
        }

        if self._cluster:
            params[r'clusterName'] = self._cluster

        for server in self._servers:

            url = f'{self._protocol}://{server}{self._endpoint}/nacos/v1/ns/instance/list'

            try:

                resp = requests.get(url, params, timeout=self._request_timeout)

                if resp.status_code == 200:
                    self._content = resp.json()[r'hosts']
                    self._content_hash = Utils.md5(Utils.json_encode(self._content))
                else:
                    raise Exception(r'nacos instance query error')

            except Exception as err:
                Utils.log.error(str(err))
            else:
                break

        else:

            Utils.log.error(f'nacos instance query failed: servers unusable')

        return self._content

    def open(self):

        self._listener(self._send_query())

        self._task.start()

    def close(self):

        self._task.stop()

    def get_host(self):

        if not self._content:
            return None

        return Utils.randhit(self._content, lambda x: int(x[r'weight'] * 100))

    def get_hosts(self):

        return Utils.deepcopy(self._content)
