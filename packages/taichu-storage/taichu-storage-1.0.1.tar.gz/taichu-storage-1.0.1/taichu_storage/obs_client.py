import logging

from taichu_storage import StorageInterface
from obs import ObsClient, PutObjectHeader


class StorageObs(StorageInterface):

    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}

        self._bucket = cfgs.get('bucket')
        obs_ak = cfgs.get('ak')
        obs_sk = cfgs.get('sk')
        obs_server = cfgs.get('endpoint_url')

        self._client = ObsClient(
            access_key_id=obs_ak,
            secret_access_key=obs_sk,
            server=obs_server
        )

    def list_objects(self, key, delimiter=''):
        max_num = 1000
        mark = None
        result = []
        while True:
            resp = self._client.listObjects(bucketName=self._bucket, prefix=key, marker=mark,
                                            max_keys=max_num, delimiter=delimiter)
            if resp.status < 300:
                folders = []
                for folder in resp.body.commonPrefixs:
                    folders.append(folder.Prefix)
                result.extend(folders)
                objects = []
                for content in resp.body.contents:
                    objects.append(content.Key)
                result.extend(objects)
                if resp.body.is_truncated is True:
                    mark = resp.body.next_marker
                else:
                    break
            else:
                logging.error(f'list_objects error,error_code:{resp.errorCode}, message:{resp.errorMessage}')

        return result

    def download_file(self, file_path, key):
        pass

    def download_dir(self, key, local_target_directory):
        pass

    def generate_signed_url(self, key, expiration=600, host_url=None):
        try:
            rps = self._client.createSignedUrl("GET", self._bucket, key, expires=6000)
            return rps.signedUrl
        except Exception as e:
            logging.error(e)
            return None

    def generate_upload_credentials(self, key, expiration=3600):
        try:
            rps = self._client.createSignedUrl("PUT", self._bucket, key,
                                               expires=expiration, headers={'Content-Type': 'text/plain'})
            return rps.signedUrl
        except Exception as e:
            logging.error(e)
            return None

    def write_bytes(self, content_bytes, key):
        self.write_string(content_bytes, key)

    def write_string(self, content_string, key):
        try:
            self._client.putContent(self._bucket, key, content=content_string)
        except Exception as e:
            logging.error("write_string error:", e)

    def upload_file(self, file_path, key):
        headers = PutObjectHeader()
        headers.contentType = 'text/plain'
        self._client.putFile(self._bucket, key, file_path, metadata={}, headers=headers)

    def copy_object(self, source_key, dest_key):
        resp = self._client.copyObject(self._bucket, source_key, self._bucket, dest_key)
        if not resp.status < 300:
            logging.error(f'copy_object error,error_code:{resp.errorCode}, message:{resp.errorMessage}')

    def copy_dir(self, source_path, dest_path):
        objects = self.list_objects(source_path)
        for source_key in objects:
            dest_key = source_key.replace(source_path, dest_path)
            self.copy_object(source_key, dest_key)

    def create_dir(self,  key):
        if not key.endswith('/'):
            key = key + '/'
        self.write_string(None, key)


if __name__ == '__main__':
    c = StorageObs({

    })

    # print(c.list_objects('shenli_test/', delimiter=''))
    #
    # print(c.generate_signed_url('shenli_test/COCO_train2014_000000285059.jpg'))
    #
    # print(c.generate_upload_credentials('shenli_test/upload.jpg'))

    # print(c.write_string("你好hello", 'shenli_test/test/hello.txt'))
    #
    # data = 'Hello, 你好!'.encode('utf-8')  # 这将返回一个bytes对象
    # print(c.write_bytes(data, 'shenli_test/test/bytes.txt'))
    #
    # c.upload_file('/Users/shenli/Downloads/resource/dataset_coco/COCO_train2014_000000285323.jpg', 'admin/upload.jpg')
    #
    # c.download_file('/Users/shenli/Downloads/resource/dataset_coco/download.jpg', 'admin/upload.jpg')
    #
    # c.download_dir('shenli/', '/Users/shenli/Downloads/resource/test_download/')

    # c.copy_object('shenli_test/COCO_train2014_000000285059.jpg', 'shenli_test/copy.jpg')
    #
    # c.create_dir('shenli_test3/')

    # print(c.list_objects('shenli/', delimiter='/'))

    # c.copy_dir('shenli_test/', 'shenli_test2/')
