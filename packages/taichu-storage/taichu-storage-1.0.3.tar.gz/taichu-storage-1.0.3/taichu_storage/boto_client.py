import logging

from taichu_storage import StorageInterface
import boto.s3.connection
import boto.exception
import os


class StorageBoto(StorageInterface):
    _boto_host = ''
    _boto_port = ''

    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}

        boto_ak = cfgs.get('boto_ak')
        boto_sk = cfgs.get('boto_sk')
        self._boto_host = cfgs.get('boto_host')
        self._boto_port = cfgs.get('boto_port')
        boto_path = cfgs.get('boto_path')
        boto_bucket = cfgs.get('boto_bucket')

        self._client = boto.connect_s3(
            aws_access_key_id=boto_ak,
            aws_secret_access_key=boto_sk,
            host=self._boto_host,
            port=self._boto_port,
            path=boto_path,
            is_secure=False,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        self._bucket = self._client.get_bucket(boto_bucket)

    def write_bytes(self, content_bytes, key):
        try:
            s3_key = self._bucket.new_key(key)
            s3_key.set_contents_from_file(content_bytes)
        except boto.exception.BotoClientError:
            pass
        except Exception as e:
            logging.info("key: " + key)
            logging.error("TaichuStorageError", e)

    def write_string(self, content_string, key):
        try:
            s3_key = self._bucket.new_key(key)
            s3_key.set_contents_from_string(content_string)
        except boto.exception.BotoClientError:
            pass
        except Exception as e:
            logging.info("key: " + key)
            logging.error("TaichuStorageError", e)

    def upload_file(self, file_path, key):
        s3_key = self._bucket.new_key(key)
        with open(file_path, "rb") as f:
            try:
                s3_key.set_contents_from_file(f)
            except:
                return

    def download_dir(self, src, dest):
        rps = self._bucket.list(prefix=src)
        for r in rps:
            os.makedirs(dest, exist_ok=True)
            local_file = f'{dest}{r.name.replace(src, "")}'
            try:
                key = self._bucket.get_key(r.name)
                with open(local_file, 'wb') as f:
                    key.get_contents_to_file(f)
            except Exception as e:
                if 'SAXParseException' in str(type(e)):
                    pass
                else:
                    logging.error(e)

    def generate_signed_url(self, key, expiration=600, host_url=None):
        try:
            k = self._bucket.get_key(key)
            if k is None:
                logging.info(key, "：不存在")
                return key + "：不存在"
            url = k.generate_url(expiration)
            print("URL_ORIGIN: ", url)
            if not host_url:
                return url
            h = self._boto_host
            if self._boto_port != 80:
                h = self._boto_host + ':' + str(self._boto_port)
            url = url.replace(h, host_url)
            print("URL_RETURN: ", url)
            return url
        except Exception as e:
            logging.error(e)
            return None


if __name__ == '__main__':
    c = StorageBoto({
        'boto_bucket': 'publish-data',
        'boto_ak': 'minio',
        'boto_sk': 'minio2022',
        'boto_host': 'juicefs-s3-gateway.infra',
        'boto_port': 29501,
        'boto_path': 'alluxio',
    })
    # c.write_string('abc', 'sys/test/abc.txt')
    print(c.generate_signed_url('admin/test.txt'))
    # print(c.generate_upload_credentials('sys/test/abc.txt'))
    # c.write_json({'abc': "123"}, 'sys/test/json.json')
    # c.upload_file('test/b.txt', 'sys/test/b.txt')
    # c.upload_directory('test', 'sys/test/directory')
    # c.download_directory('sys/test/directory', 'test/download')