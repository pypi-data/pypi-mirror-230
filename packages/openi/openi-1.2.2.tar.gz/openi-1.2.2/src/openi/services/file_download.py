import os
import time
from dataclasses import dataclass

from ..apis import OpeniAPI
from ..utils import logger

log = logger.setup_logger()


@dataclass
class OpeniFileDownload:
    """
    Download file object
    """

    filename: str
    size: int
    local_dir: str
    repo_id: str
    dataset_or_model_id: str
    dataset_or_model_name: str
    target_type: str  # ['dataset','model']
    upload_type: int = 1
    uuid: str = None
    filepath: str = None
    pbar: object = None
    downloaded: bool = False

    def __post_init__(self):
        self.api = OpeniAPI()
        self.filepath = os.path.join(self.local_dir, self.filename)
        self.is_download_complete()
        log.info(f"OpeniFileDownload Object init: {self.__dict__}")

    def is_download_complete(self):
        if os.path.exists(self.filepath):
            if self.size == os.path.getsize(self.filepath):
                self.downloaded = True
                return
        self.downloaded = False

    def download_with_tqdm(self):
        ts_total = time.time()
        log.info(
            f"download_with_tqdm() {self.filename} starts, size {self.size} bytes..."
        )

        if self.downloaded:
            if self.target_type == "dataset":
                self.filepath = rename_existing_file(self.filepath)
                log.info(
                    f"{self.filename} rename_existing_file({self.filepath}) completes..."
                )
            else:
                self.pbar.update(self.size)
                self.pbar.set_description_str(
                    self.pbar.desc.replace("Waiting", "Complete")
                )
                log.info(f"{self.filename} downloaded, download_with_tqdm() ends...")
                return

        if self.target_type == "model" and os.path.exists(self.filepath):
            os.remove(self.filepath)
            log.info(f"{self.filename} os.remove({self.filepath}) completes...")

        self.pbar.set_description_str(self.pbar.desc.replace("Waiting", "Downloading"))

        if self.target_type == "dataset":
            file_stream = self.api.dataset_download_file(
                uuid=self.uuid,
                upload_type=self.upload_type,
            )

        if self.target_type == "model":
            file_stream = self.api.model_download_single(
                repo_id=self.repo_id,
                model_id=self.dataset_or_model_id,
                filename=self.filename,
            )
        log.info(f"{self.filename} file_stream() received...")

        ts = time.time()
        block_size = 1024
        with open(self.filepath, "wb") as f:
            log.info(f"{self.filename} file opened...")
            for data in file_stream.iter_content(block_size):
                self.pbar.update(len(data))
                f.write(data)
        log.info(f"{self.filename} file closed...")

        self.pbar.set_description_str(self.pbar.desc.replace("Downloading", "Complete"))
        log.info(
            f"download_with_tqdm() {self.filename} ends, {time.time() - ts_total}s total time used..."
        )


def rename_existing_file(filepath: str):
    if "tar.gz" in filepath:
        path = filepath.replace(".tar.gz", "")
        suffix = ".tar.gz"
    else:
        path, suffix = os.path.splitext(filepath)

    counter = 1
    while os.path.exists(filepath):
        filepath = "{}({}){}".format(path, counter, suffix)
        counter += 1
    return filepath
