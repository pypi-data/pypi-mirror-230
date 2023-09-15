from dataclasses import dataclass

from ..apis import OpeniAPI
from ..utils import logger, constants
from ..utils.logger import *

log = logger.setup_logger()


def get_upload_type(cluster: str):
    try:
        cluster = cluster.lower()
        upload_type = constants.FILE.UPLOAD_TYPE.index(cluster)
        return upload_type
    except:
        msg = f"`cluster` 参数为 [gpu,npu] 其中之一，不区分大小写"
        log.error(msg)
        raise ValueError(msg)


def get_cluster(upload_type: str):
    try:
        cluster = constants.FILE.UPLOAD_TYPE[upload_type]
        return cluster
    except:
        msg = f"`upload_type` 参数为 [0,1] 其中之一"
        log.error(msg)
        raise ValueError(msg)


@dataclass
class OpeniDataset:
    repo_id: str
    dataset_id: str = None
    dataset_name: str = None
    dataset_files: list = None

    def __post_init__(self):
        self.api = OpeniAPI()
        if self.dataset_name is None:
            self.get_dataset_current_repo()
        log.info(f"OpeniDataset Object init: {self.__dict__}")

    def get_dataset_current_repo(self):
        try:
            response = self.api.dataset_query(repo_id=self.repo_id).json()
            self.dataset_id = response["data"][0]["id"]
            self.dataset_name = response["data"][0]["title"]
        except:
            msg = f"❌ 获取数据集失败，`{self.repo_id}` 仓库尚未创建数据集，请先在网页端创建"
            log.error(msg)
            raise ValueError(msg)

    def get_dataset_file(self, upload_type: int):
        try:
            response = self.api.dataset_query_with_attachment(
                repo_id=self.repo_id,
                upload_type=upload_type,
            ).json()
            d = next(d for d in response["data"] if d["title"] == self.dataset_name)
            self.dataset_files = d["attachments"]
            log.info(f"OpeniDataset get_dataset_file: {response}")
        except:
            msg = f"❌ `{self.repo_id}`-`{self.dataset_name}` 获取数据集文件列表失败，请检查数据集是否存在文件或者集群[gpu,npu]是否填写正确"
            log.error(msg)
            raise ValueError(msg)
