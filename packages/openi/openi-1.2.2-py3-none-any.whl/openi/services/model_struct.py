from dataclasses import dataclass

from ..apis import OpeniAPI
from ..utils import logger, constants


log = logger.setup_logger()


def get_engine(engine: str):
    try:
        engine_type = constants.API.ENGINE_TYPE.index(engine.lower())
        return engine_type
    except:
        msg = f"❌ `engine` 参数为[pytorch, tensorflow, mindspore, paddlepaddle, oneflow, mxnet, other]其中之一，不区分大小写"
        log.error(msg)
        raise ValueError(msg)


@dataclass
class OpeniModel:
    model_name: str
    repo_id: str
    model_id: str = None
    storage_path: str = None
    model_files: list = None
    model_type: int = None
    model_creator: str = None

    # api = OpeniAPI()

    def __post_init__(self):
        self.api = OpeniAPI()
        self.get_model_id_by_name()
        self.get_model_file()
        log.info(f"OpeniModel Object init: {self.__dict__}")

    def get_model_id_by_name(self):  # repo_id, model_name):
        try:
            response = self.api.model_query_by_name(
                repo_id=self.repo_id,
                model_name=self.model_name,
            ).json()
            self.model_id = response[0]["id"]
            self.storage_path = response[0]["path"]
            self.model_type = response[0]["modelType"]
            self.model_creator = response[0]["userName"]
            self.can_operate = response[0]["isCanOper"]
            self.can_download = response[0]["isCanDownload"]
        except:
            msg = f"❌ `{self.repo_id}` 未找到名为 `{self.model_name}` 的模型"
            log.error(msg)
            raise ValueError(msg)

    def get_model_file(self):
        try:
            response = self.api.model_file_query_by_id(
                repo_id=self.repo_id,
                model_id=self.model_id,
            ).json()
            sorted_model_files = sorted(response, key=lambda x: x["size"])
            self.model_files = sorted_model_files
        except:
            msg = f"❌ `{self.repo_id}`-`{self.model_name}` 获取模型文件列表失败"
            log.error(msg)
            raise ValueError(msg)


def get_model_files_by_id(repo_id, model_id):
    try:
        api = OpeniAPI()
        model_files = api.model_file_query_by_id(
            repo_id=repo_id, model_id=model_id
        ).json()
        return model_files
    except:
        msg = f"❌ "
        log.error(msg)
        raise ValueError(msg)


def create_model(repo_id, model_name):
    api = OpeniAPI()
    response = api.model_create(repo_id, model_name)
    if response.json()["code"] == "0":
        model_id = response.json()["id"]
        return model_id
    else:
        msg = f"model create failed, {response.json()['msg']}"
        log.error(msg)
        raise ValueError(msg)
