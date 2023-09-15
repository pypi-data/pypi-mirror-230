import logging

import boto3
import botocore.exceptions
from botocore.config import Config

from taichu_storage import StorageInterface
import os


class StorageBoto3(StorageInterface):
    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}
        bucket = cfgs.get('bucket')
        ak = cfgs.get('ak')
        sk = cfgs.get('sk')
        region_name = cfgs.get('region_name', 'default')
        endpoint_url = cfgs.get('endpoint_url')
        prefix = cfgs.get('prefix')
        if prefix and not prefix.endswith('/'):
            prefix = prefix + '/'
        self._prefix = prefix
        self._bucket = bucket
        self._client = boto3.client(
            's3',
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            use_ssl=True,
            region_name=region_name,
            endpoint_url=endpoint_url,
            config=Config(s3={"addressing_style": "path", "signature_version": 's3v4'}))

    def write_bytes(self, content_bytes, key):
        key = f'{self._prefix}{key}'
        try:
            self._client.put_object(Body=content_bytes, Bucket=self._bucket, Key=key)
        except Exception as e:
            logging.error("write_bytes error", e)

    def write_string(self, content_string, key):
        key = f'{self._prefix}{key}'
        try:
            data = content_string.encode('utf-8')
            self._client.put_object(Body=data, Bucket=self._bucket, Key=key)
        except Exception as e:
            logging.error("write_string error", e)

    def upload_file(self, file_path, key):
        key = f'{self._prefix}{key}'
        try:
            self._client.upload_file(file_path, self._bucket, key)
        except Exception as e:
            logging.error("upload_file error", e)

    def download_file(self, file_path, key):
        key = f'{self._prefix}{key}'
        try:
            self._client.download_file(self._bucket, key, file_path)
        except Exception as e:
            logging.error("download_file error", e)

    def download_dir(self, key, local_target_directory):
        key = f'{self._prefix}{key}'
        response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        m = {}
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('/'):
                continue
            s3_key = obj['Key']
            local_file_path = f'{local_target_directory}{s3_key.replace(key, "")}'
            dirname = os.path.dirname(local_file_path)
            try:
                if not m.get(dirname, False):
                    os.makedirs(dirname, exist_ok=True)
                    m[dirname] = True
                self._client.download_file(self._bucket, s3_key, local_file_path)
            except Exception as e:
                logging.error(e)

    def generate_signed_url(self, key, expiration=600, host_url=None):
        key = f'{self._prefix}{key}'
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except botocore.exceptions.ClientError as e:
            logging.error("generate_signed_url error:", e)
            return None

    def generate_upload_credentials(self, key, expiration=3600):
        key = f'{self._prefix}{key}'
        try:
            response = self._client.generate_presigned_post(self._bucket, key, ExpiresIn=expiration)
        except botocore.exceptions.ClientError as e:
            logging.error("generate_upload_credentials error:", e)
            return None

        return response

    def list_objects(self, key, delimiter=''):
        key = f'{self._prefix}{key}'
        result = []
        try:
            response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key, Delimiter=delimiter)
            if 'CommonPrefixes' in response:
                folders = []
                for item in response['CommonPrefixes']:
                    folders.append(item['Prefix'].replace(self._prefix, '', 1))
                result.extend(folders)
            if 'Contents' in response:
                objects = []
                for item in response['Contents']:
                    if item['Key'].endswith('/'):
                        continue
                    objects.append(item['Key'].replace(self._prefix, '', 1))
                result.extend(objects)
            return result
        except Exception as e:
            logging.error("list_objects error:", e)
            return []

    def copy_object(self, source_key, target_key):
        source_key = f'{self._prefix}{source_key}'
        target_key = f'{self._prefix}{target_key}'
        try:
            self._client.copy_object(Bucket=self._bucket, Key=target_key,
                                     CopySource={'Bucket': self._bucket, 'Key': source_key})
        except Exception as e:
            logging.error("copy_object error:", e)
            return None

    def copy_dir(self, source_folder, dest_folder):
        source_folder = f'{self._prefix}{source_folder}'
        dest_folder = f'{self._prefix}{dest_folder}'
        objects = self._client.list_objects_v2(Bucket=self._bucket, Prefix=source_folder)

        if 'Contents' not in objects:
            logging.info("No files found in the source folder.")
            return
        m = {}
        for obj in objects['Contents']:
            if obj['Key'].endswith('/'):
                continue
            copy_source = {'Bucket': self._bucket, 'Key': obj['Key']}
            dest_key = obj['Key'].replace(source_folder, dest_folder, 1)
            dirname = os.path.dirname(dest_key)
            if not m.get(dirname):
                self._client.put_object(Bucket=self._bucket, Key=dirname+'/')
                m[dirname] = True
            self._client.copy_object(CopySource=copy_source, Bucket=self._bucket, Key=dest_key)

    def create_dir(self,  key):
        key = f'{self._prefix}{key}'
        if not key.endswith('/'):
            key = key + '/'
        try:
            self._client.put_object(Bucket=self._bucket, Key=key)
        except Exception as e:
            logging.error("create_dir error:", e)
            return None



if __name__ == '__main__':
    c = StorageBoto3({

    })
    # print(c.write_string("你好hello", 'admin/dir1/test.txt'))

    # print(c.list_objects('admin/', delimiter='/'))

    # print(c.generate_signed_url('admin/COCO_train2014_000000285059.jpg'))

    # response = c.generate_upload_credentials('admin/test.jpg')
    # print(response)
    # object_name = '/Users/shenli/Downloads/resource/dataset_coco/COCO_train2014_000000285323.jpg'
    # with open(object_name, 'rb') as f:
    #     files = {'file': (object_name, f)}
    #     http_response = requests.post(response['url'], data=response['fields'], files=files)
    #     print(http_response.status_code, '---http_response.status_code')

    # print(c.write_string("你好hello", 'admin/test.txt'))
    #
    # data = 'Hello, 你好!'.encode('utf-8')  # 这将返回一个bytes对象
    # print(c.write_bytes(data, 'admin/bytes.txt'))
    #
    # c.upload_file('/Users/shenli/Downloads/resource/dataset_coco/COCO_train2014_000000285323.jpg', 'admin/upload.jpg')
    #
    # c.download_file('/Users/shenli/Downloads/resource/dataset_coco/download.jpg', 'admin/upload.jpg')
    #
    # c.download_dir('shenli/', '/Users/shenli/Downloads/resource/test_download/')

    # c.copy_object('admin/upload.jpg', 'admin/copy1.jpg')

    # c.create_dir('admin/dir1/')
    #
    print(c.list_objects('shenli/', delimiter='/'))

    # c.copy_dir('admin/', 'shenli/')
