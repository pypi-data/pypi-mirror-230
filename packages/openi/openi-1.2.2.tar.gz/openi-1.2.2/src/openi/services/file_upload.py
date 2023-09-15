import hashlib
import math
import os
from dataclasses import dataclass

from .file_progress_bar import *
from ..apis import OpeniAPI
from ..utils import logger, constants
from ..utils.logger import *

log = logger.setup_logger()


@dataclass
class OpeniFileUpload:
    """
    Upload file object
    """

    local_file: str
    repo_id: str
    upload_type: str
    dataset_or_model_id: str
    dataset_or_model_name: str
    target_type: str  # ['dataset','model']
    chunk_size: int = None
    total_chunks_count: int = None
    pbar: object = None
    md5_pbar: object = None

    uploaded: int = False  # 1 for True, 0 for False
    uploading_chunks_idx: list = None
    uuid: str = None
    upload_id: str = None
    filename_exists: str = None

    def __post_init__(self):
        self.api = OpeniAPI()

        self.filename = os.path.basename(self.local_file)
        self.filepath = os.path.abspath(self.local_file)

        self.size = os.path.getsize(self.filepath)
        if self.md5_pbar is not None:
            self.md5 = calculateMD5(self.filepath, self.md5_pbar)
        else:
            self.md5 = calculateMD5(self.filepath)
        self.set_chunk_size()
        self.set_total_chunks_count()

        log.info(f"OpeniFileUpload Object init: {self.__dict__}")

    def set_chunk_size(self):
        if self.target_type == "model":
            self.chunk_size = constants.FILE.LARGE_FILE_CHUNK_SIZE
        else:
            if self.size < constants.FILE.SMALL_FILE_LIMIT:
                self.chunk_size = constants.FILE.SMALL_FILE_CHUNK_SIZE
            else:
                self.chunk_size = constants.FILE.LARGE_FILE_CHUNK_SIZE

    def set_total_chunks_count(self):
        total_chunks_count = math.ceil(self.size / self.chunk_size)
        self.total_chunks_count = total_chunks_count

    def read_file_by_chunk(self, real_chunk_size: int, start_position: int = 0):
        with open(self.filepath, "rb") as file:
            file.seek(start_position)
            chunk = file.read(real_chunk_size)
            return chunk

    def get_chunks(self):
        if self.target_type == "dataset":
            get_chunks = self.api.dataset_file_get_chunks(
                dataset_id=self.dataset_or_model_id,
                md5=self.md5,
                filename=self.filename,
                upload_type=self.upload_type,
            ).json()
            if "repoName" in get_chunks and "repoOwner" in get_chunks:
                cluster = constants.FILE.UPLOAD_TYPE[self.upload_type]
                self.pbar.close()
                msg = (
                    f"Falied: ❌ `{get_chunks['fileName']}` ({cluster})"
                    " 你已上传过此数据集，无法重复上传，点击链接查看 "
                    f"{self.api.endpoint.split('/api')[0]}/{get_chunks['repoOwner']}/{get_chunks['repoName']}/datasets"
                )
                log.error(msg)
                raise ValueError(msg)
        if self.target_type == "model":
            get_chunks = self.api.model_file_get_chunks(
                modeluuid=self.dataset_or_model_id,
                md5=self.md5,
                filename=self.filename,
                upload_type=self.upload_type,
            ).json()

        # upload completed
        self.uploaded = get_chunks["uploaded"]

        # continue upload
        if get_chunks["uuid"] != "" and get_chunks["uploadID"] != "":
            self.uuid = get_chunks["uuid"]
            self.upload_id = get_chunks["uploadID"]
            uploaded_chunks = [i for i in get_chunks["chunks"].split(",") if i != ""]
            # init uuid and uploadID but no chunks
            init_idx = 1 if uploaded_chunks == [] else len(uploaded_chunks)
            self.uploading_chunks_idx = [
                i for i in range(init_idx, self.total_chunks_count + 1)
            ]

    def new_multipart(self):
        if self.target_type == "dataset":
            new_multipart = self.api.dataset_file_new_multipart(
                dataset_id=self.dataset_or_model_id,
                md5=self.md5,
                filename=self.filename,
                upload_type=self.upload_type,
                size=self.size,
                total_chunks_count=self.total_chunks_count,
            ).json()
        if self.target_type == "model":
            new_multipart = self.api.model_file_new_multipart(
                modeluuid=self.dataset_or_model_id,
                md5=self.md5,
                filename=self.filename,
                upload_type=self.upload_type,
                size=self.size,
                total_chunks_count=self.total_chunks_count,
            ).json()

        self.uuid = new_multipart["uuid"]
        self.upload_id = new_multipart["uploadID"]
        self.uploading_chunks_idx = [i for i in range(1, self.total_chunks_count + 1)]

    def get_multipart_url(self, chunk_number: int):
        if self.target_type == "dataset":
            url = self.api.dataset_file_get_multipart_url(
                chunk_number=chunk_number,
                chunk_size=self.chunk_size,
                dataset_id=self.dataset_or_model_id,
                filename=self.filename,
                upload_type=self.upload_type,
                upload_id=self.upload_id,
                uuid=self.uuid,
            ).json()["url"]
        if self.target_type == "model":
            url = self.api.model_file_get_multipart_url(
                chunk_number=chunk_number,
                chunk_size=self.chunk_size,
                upload_type=self.upload_type,
                upload_id=self.upload_id,
                uuid=self.uuid,
            ).json()["url"]

        return url

    def complete_multipart(self):
        if self.target_type == "dataset":
            self.api.dataset_file_complete_multipart(
                dataset_id=self.dataset_or_model_id,
                filename=self.filename,
                upload_type=self.upload_type,
                size=self.size,
                upload_id=self.upload_id,
                uuid=self.uuid,
            )
        if self.target_type == "model":
            self.api.model_file_complete_multipart(
                modeluuid=self.dataset_or_model_id,
                upload_type=self.upload_type,
                upload_id=self.upload_id,
                uuid=self.uuid,
            )

    def upload_with_tqdm(self):
        # get_chunks
        self.get_chunks()

        # if uploaded and complete: update bar, return
        if self.uploaded == "1":
            msg = f"Failed: ❌ 已存在, 无需重复上传"
            self.pbar.set_description_str(self.pbar.desc.replace("Waiting", msg))
            # self.pbar.close()
            log.error(self.pbar.desc)
            return

        if self.uploaded == "0":
            # if continue: get_multipart_url, update bar, upload_chunks, complete_multipart
            # if not complete: update bar, complete_multipart
            # if new: new_multipart, update bar, upload_chunks, complete_multipart
            if not self.uuid and not self.upload_id:
                self.new_multipart()

            # start uploading
            self.pbar.set_description_str(
                self.pbar.desc.replace("Waiting", "Uploading")
            )
            init_progress = self.chunk_size * (
                self.total_chunks_count - len(self.uploading_chunks_idx)
            )
            self.pbar.update(init_progress)

            # upload_chunks
            for n in self.uploading_chunks_idx:
                start_position = (n - 1) * self.chunk_size
                real_chunk_size = min(self.chunk_size, self.size - start_position)

                data = self.read_file_by_chunk(
                    real_chunk_size=real_chunk_size, start_position=start_position
                )
                self.pbar.update(real_chunk_size)

                url = self.get_multipart_url(chunk_number=n)
                response = self.api.file_put_upload(
                    url=url,
                    data=data,
                    upload_type=self.upload_type,
                )
                etag = response.headers.get("ETag")
                if etag is None:
                    msg = f"❌ file_put_upload failed: {self.filename} chunk {n} failed to upload."
                    log.error(msg)
                    raise RuntimeError(msg)

            # complete upload process
            self.complete_multipart()
            self.pbar.set_description_str(
                self.pbar.desc.replace("Uploading", "Complete")
            )
            # self.pbar.close()


"""
public methods
"""


def calculateMD5(filepath: str, md5_pbar: object = None) -> str:
    """
    Calculate MD5 of a file
    """
    m = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def get_upload_folder_files(folder: str):
    local_dir = os.path.expanduser(folder)
    files = list()
    for root, dirs, filenames in os.walk(local_dir):
        if dirs != []:
            msg = f"❌ {local_dir} 路径下不允许有子文件夹."
            log.error(msg)
            raise ValueError(msg)
        for file in filenames:
            filepath = os.path.join(root, file)
            filesize = os.path.getsize(filepath)
            upload_size_check(file, filesize)
            files.append([filepath, filesize])
    sorted_files = [i[0] for i in sorted(files, key=lambda x: x[1])]
    return local_dir, sorted_files


def upload_size_check(filename: str, size: int):
    # msg = None
    if size == 0:
        msg = f"❌ `{filename}` file size is 0"
        log.error(msg)
        raise ValueError(msg)
    if size > constants.FILE.MAX_FILE_SIZE:
        msg = f"❌ `{filename}` file size exceeds {constants.FILE.MAX_FILE_SIZE_GB}GB"
        log.error(msg)
        raise ValueError(msg)
