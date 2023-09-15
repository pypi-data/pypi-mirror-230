import base64
import io
import os
import json
from abc import abstractmethod
from enum import Enum


class Protocol(Enum):
    BOTO = 1
    OBS = 2
    BOTO3 = 3
    MINIO = 4


class StorageInterface:
    _client = None
    _bucket = None

    def client(self):
        return self._client

    @abstractmethod
    def write_bytes(self, content_bytes, key):
        pass

    @abstractmethod
    def write_string(self, content_string, key):
        pass

    def write_json(self, content_json, key):
        self.write_string(json.dumps(content_json), key)

    def write_base64(self, content_base64, key):
        image_data = base64.b64decode(content_base64)
        image_stream = io.BytesIO(image_data)
        self.write_bytes(image_stream, key)

    @abstractmethod
    def upload_file(self, file_path, key):
        pass

    def upload_directory(self, directory, key):
        for root, dirs, files in os.walk(directory):
            for file in files:
                local_path = os.path.join(root, file)
                s3_key = os.path.join(key, os.path.relpath(local_path, directory))
                self.upload_file(local_path, s3_key)

    @abstractmethod
    def download_file(self, file_path, key):
        raise Exception("Not Implemented: download_file")

    @abstractmethod
    def download_dir(self, key, local_target_directory):
        raise Exception("Not Implemented: download_dir")

    @abstractmethod
    def generate_signed_url(self, key, expiration=600, host_url=None):
        raise Exception("Not Implemented: generate_signed_url")

    @abstractmethod
    def generate_upload_credentials(self, key, expiration=3600):
        raise Exception("Not Implemented: generate_upload_credentials")

    # @abstractmethod
    # def copy_key(self, from_key, to_key, filter_func=None):
    #     raise Exception("Not Implemented: copy_key")
    #
    # @abstractmethod
    # def copy_dir(self, from_dir, to_dir, filter_func=None):
    #     raise Exception("Not Implemented: copy_dir")
    #
    # @abstractmethod
    # def list(self, dir, delimiter="", marker=None, size=None):
    #     raise Exception("Not Implemented: list")
    # @abstractmethod
    # def list_objects(self, prefix):
    #     pass


def create_storage(protocol: Protocol, cfgs=None):
    if cfgs is None:
        cfgs = {}
    if protocol == Protocol.OBS:
        from taichu_storage.obs_client import StorageObs
        return StorageObs(cfgs)
    if protocol == Protocol.BOTO3:
        from taichu_storage.boto3_client import StorageBoto3
        return StorageBoto3(cfgs)
    elif protocol == Protocol.BOTO:
        from taichu_storage.boto_client import StorageBoto
        return StorageBoto(cfgs)
    elif protocol == Protocol.MINIO:
        from taichu_storage.minio_client import StorageMinio
        return StorageMinio(cfgs)
    return None

