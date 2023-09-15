from dataclasses import dataclass

from ..apis import OpeniAPI
from ..utils import logger

log = logger.setup_logger()


def get_login_user(token: str = None, endpoint: str = None):
    try:
        api = OpeniAPI(token=token, endpoint=endpoint)
        response = api.user_my_info().json()
        # username = response.json()["username"]
        return response, api.endpoint
    except:
        msg = f"❌ 无法获取当前用户信息"
        log.error(msg)
        raise ValueError(msg)


@dataclass
class OpeniRepo:
    repo_id: str

    # api = OpeniAPI()

    def __post_init__(self):
        self.api = OpeniAPI()
        user_info, _ = get_login_user()
        self.current_user = user_info["username"]
        self.is_admin = user_info["is_admin"]
        self.get_repo_by_name()
        self.get_repo_access()
        self.check_repo_collaborator()
        self.is_onwer = self.owner == self.current_user
        log.info(f"OpeniRepo Object init: {self.__dict__}")

    def check_repo_collaborator(self):
        try:
            response = self.api.repo_is_colloborator(self.repo_id, self.current_user)
            self.is_collaborator = response == 204
        except:
            msg = (
                f"❌ `{self.repo_id}` 无法获取仓库协作者信息，"
                "请检查仓库是否存在或者repo_id是否正确，"
                "repo_id为仓库链接中的 `拥有者(组织)/仓库名`"
            )
            log.error(msg)
            raise ValueError(msg)

    def get_repo_by_name(self):
        try:
            response = self.api.repo_info(self.repo_id).json()
            self.repo_id = response["full_name"]
            self.repo_uuid = response["id"]
            self.full_display_name = response["full_display_name"]
            self.owner = response["owner"]["username"]
        except:
            msg = (
                f"❌ `{self.repo_id}` 无法获取仓库信息，"
                "请检查仓库是否存在或者repo_id是否正确，"
                "repo_id为仓库链接中的 `拥有者(组织)/仓库名`"
            )
            log.error(msg)
            raise ValueError(msg)

    def get_repo_access(self):
        try:
            response = self.api.repo_access(self.repo_id).json()["right"]
            self.access = response
        except:
            msg = (
                f"❌ `{self.repo_id}` 无法获取仓库权限，"
                "请检查仓库是否存在或者repo_id是否正确，"
                "repo_id为仓库链接中的 `拥有者(组织)/仓库名`"
            )
            log.error(msg)
            raise ValueError(msg)
