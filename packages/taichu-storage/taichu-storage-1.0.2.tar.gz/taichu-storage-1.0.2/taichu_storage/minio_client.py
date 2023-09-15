import io
import logging

from taichu_storage import StorageInterface
from minio import Minio
from io import BytesIO


class StorageMinio(StorageInterface):
    _use_alluxio_path = True

    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}

        endpoint = cfgs.get('minio_endpoint')
        ak = cfgs.get('minio_ak')
        sk = cfgs.get('minio_sk')
        self._bucket = cfgs.get('bucket')
        self._use_alluxio_path = cfgs.get('use_alluxio_path', True)
        print(self._use_alluxio_path, self._bucket)

        self._client = Minio(
            endpoint,
            ak,
            sk,
            secure=False,
        )

    def generate_signed_url(self, key, expiration=600, host_url=None):
        key = self._prefix_key(key)
        return self._client.presigned_get_object(self._alluxio_bucket(), key, expiration)

    def _prefix_key(self, key):
        alluxio_path = 'data/%s/' % self._bucket
        print('alluxio_path: %s' % alluxio_path)
        if self._use_alluxio_path is False or key.startswith(alluxio_path):
            k = key
        else:
            k = alluxio_path + key.lstrip('/')
        print(k)
        return k

    def _alluxio_bucket(self):
        return 'alluxio' if self._use_alluxio_path else self._bucket

    def write_bytes(self, content_bytes, key):
        key = self._prefix_key(key)
        # o = StrReader(content_bytes)
        try:
            self._client.put_object(
                self._alluxio_bucket(),
                key,
                io.BytesIO(content_bytes),
                len(content_bytes)
            )
        except Exception as e:
            logging.error(e)

    def write_string(self, content_string, key):
        key = self._prefix_key(key)
        return self.write_bytes(content_string.encode('utf-8'), key)

    def upload_file(self, file_path, key):
        key = self._prefix_key(key)
        print(key)
        try:
            self._client.fput_object(
                self._alluxio_bucket(),
                key,
                file_path
            )
        except Exception as e:
            logging.error(e)


class StrReader:

    def __init__(self, strs):
        self.str = strs if isinstance(strs, bytes) else strs.encode('utf-8')

    def read(self, n=-1):
        return self.str

    def len(self):
        return len(self.str)


if __name__ == '__main__':
    c = StorageMinio({

    })
    c.write_string('abc', 'sys/test/abc.txt')
    # c.write_bytes(b"hello", 'sys/test/abc_bytes.txt')
    c.upload_file('test/b.txt', 'sys/test/b.txt')
    # print(c.generate_signed_url('sys/test/abc.txt'))
    # print(c.generate_upload_credentials('sys/test/abc.txt'))
