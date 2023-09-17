__version__ = '0.1.0'

import evaics.sdk as sdk

from evaics.sdk import (pack, unpack, OID, LOCAL_STATE_TOPIC,
                        REMOTE_STATE_TOPIC, rpc_e2e)

from types import SimpleNamespace

import socket
import json
import threading
import busrt

UDP_BUF_SIZE = 8192

d = SimpleNamespace(sock=None,
                    target_host=None,
                    target_port=None,
                    service=None,
                    packer=None,
                    unpacker=None)


def pack_json(payload):
    return json.dumps(payload).encode()


def unpack_json(data):
    return json.loads(data)


def serve(sock):
    while True:
        try:
            data = d.unpacker(sock.recv(UDP_BUF_SIZE))
            method = data.get('method')
            if method is None:
                raise ValueError('method not specified')
            params = data.get('params')
            target = data.get('target', 'eva.core')
            d.service.logger.info(f'{target}::{method} {params}')
            try:
                result = d.service.rpc.call(
                    target,
                    busrt.rpc.Request(method,
                                      pack(params) if params else None))
            except busrt.rpc.RpcException as e:
                raise rpc_e2e(e)
        except Exception as e:
            d.service.logger.error(e)


def on_frame(frame):
    oid = None
    if frame.topic:
        if frame.topic.startswith(LOCAL_STATE_TOPIC):
            oid = str(OID(frame.topic[len(LOCAL_STATE_TOPIC):], from_path=True))
        elif frame.topic.startswith(REMOTE_STATE_TOPIC):
            oid = str(OID(frame.topic[len(REMOTE_STATE_TOPIC):],
                          from_path=True))
    if oid:
        data = unpack(frame.payload)
        data['oid'] = oid
        d.sock.sendto(d.packer(data), (d.target_host, d.target_port))


def run():
    info = sdk.ServiceInfo(author='Bohemia Automation',
                           description='UDP Bridge',
                           version=__version__)
    service = sdk.Service()
    d.service = service

    config = service.get_config()

    fmt = config.get('format', 'json')
    if fmt == 'json':
        d.packer = pack_json
        d.unpacker = unpack_json
    elif fmt == 'msgpack':
        d.packer = pack
        d.unpacker = unpack
    else:
        raise RuntimeError(f'unsupported payload format: {fmt}')

    d.target_host, d.target_port = config['target'].rsplit(':', maxsplit=1)
    d.target_port = int(d.target_port)
    d.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    service.init(info, on_frame=on_frame)
    service.subscribe_oids(config.get('oids', []), event_kind='any')
    service.logger.info(f'target: {d.target_host}:{d.target_port}')

    if 'listen' in config:
        listen_host, listen_port = config['listen'].rsplit(':', maxsplit=1)
        listen_port = int(listen_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((listen_host, listen_port))
        service.logger.info(f'listen: {listen_host}:{listen_port}')
        threading.Thread(target=serve, args=(sock,), daemon=True).start()

    service.block()
