import requests
import json
import os
import time
from pathlib import Path
from dataclasses import dataclass

from .utils import logger, constants

log = logger.setup_logger()


"""
APIS
"""


@dataclass  # (frozen=True)
class OpeniAPI:
    endpoint: str = None
    token: str = None

    def __post_init__(self):
        if self.endpoint is None and self.token is None:
            try:
                saved_token = json.loads(Path(constants.PATH.TOKEN_PATH).read_text())
                self.token = saved_token["token"]
                self.endpoint = saved_token["endpoint"]
            except:
                msg = "❌ 本机尚未登录OpenI，请参考 https://openi.pcl.ac.cn/docs/index.html#/api/cli/login."
                log.error(msg)
                raise FileNotFoundError(msg)

        self.base_url = self.endpoint + constants.API.VERSION

    """
    basics
    """

    def send_api(
        self,
        method,
        route,
        params=dict(),
        stream=False,
        allow_redirects=False,
        *args,
        **kwargs,
    ):
        """
        General API call template to OpenI
        """

        url = self.base_url + route

        # 若不需要带token，则调用此函数时明确传入params=None
        if params is not None:
            params["access_token"] = self.token

        log.info(f"api.send_api() starts...")
        ts = time.time()
        response = requests.request(
            method=method,
            url=url,
            params=params,
            stream=stream,
            allow_redirects=allow_redirects,
        )
        log.info(f"{time.time() -ts }s used for requests returns...")
        try:
            if not kwargs.get("is_collaborator"):
                response.raise_for_status()

            log.http(
                f"{method} {route} {response.status_code} {response.reason} {response.url}"
            )

            return response

        except requests.exceptions.HTTPError as e:
            msg = f"{method} {route} {e}"
            log.warn(msg)
            raise ConnectionError(msg)

    def file_put_upload(self, url, data, upload_type):
        """
        API call to upload a chunk of the file(bytes data) to OpenI
        """
        headers = {"Content-Type": "text/plain"} if upload_type == 0 else {}
        response = requests.request(
            method="PUT",
            url=url,
            data=data,
            headers=headers,
        )
        try:
            response.raise_for_status()
            log.http(
                f"file_put_upload PUT {response.status_code} {response.reason} {response.url}"
            )
        except requests.exceptions.HTTPError as e:
            log.warn(f"{e}")

        return response

    """
    repo and user apis
    """

    def user_my_info(self):
        method = "GET"
        route = f"/user"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def user_info(self, username):
        method = "GET"
        route = f"/users/{username}"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_my_list(self):
        method = "GET"
        route = f"/user/repos"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_list(self, username):
        method = "GET"
        route = f"/users/{username}/repos"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_info(self, repo_id):
        method = "GET"
        route = f"/repos/{repo_id}"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_access(self, repo_id):
        method = "GET"
        route = f"/repos/{repo_id}/right"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_get_collaborators(self, repo_id):
        method = "GET"
        route = f"/repos/{repo_id}/collaborators"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def repo_is_colloborator(self, repo_id, username):
        method = "GET"
        route = f"/repos/{repo_id}/collaborators/{username}"
        response = self.send_api(method, route, is_collaborator=True)
        log.response(f" {route} {response.status_code}")
        return response.status_code

    """
    dataset api
    """

    def dataset_query(self, repo_id):
        method = "GET"
        route = f"/datasets/{repo_id}"
        response = self.send_api(method, route)
        log.response(f" {route} {response.json()}")
        return response

    def dataset_query_with_attachment(
        self,
        repo_id: str,
        upload_type: int = 0,
    ):
        method = "GET"
        route = f"/datasets/{repo_id}/current_repo"
        params = {"type": upload_type}
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def dataset_file_get_chunks(
        self,
        dataset_id,
        md5,
        filename,
        upload_type,
    ):
        """
        Get information of a file chunk
        """
        method = "GET"
        route = "/attachments/get_chunks"
        params = {
            "dataset_id": dataset_id,
            "md5": md5,
            "file_name": filename,
            "type": upload_type,
        }
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def dataset_file_get_multipart_url(
        self,
        chunk_number,
        chunk_size,
        dataset_id,
        filename,
        upload_type,
        upload_id,
        uuid,
    ):
        method = "GET"
        route = "/attachments/get_multipart_url"
        params = {
            "dataset_id": dataset_id,
            "file_name": filename,
            "type": upload_type,
            "chunkNumber": chunk_number,
            "size": chunk_size,
            "uploadID": upload_id,
            "uuid": uuid,
        }
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def dataset_file_new_multipart(
        self,
        dataset_id,
        md5,
        filename,
        upload_type,
        size,
        total_chunks_count,
    ):
        method = "GET"
        route = "/attachments/new_multipart"
        params = {
            "dataset_id": dataset_id,
            "md5": md5,
            "file_name": filename,
            "type": upload_type,
            "totalChunkCounts": total_chunks_count,
            "size": size,
        }
        response = self.send_api(method, route, params=params)
        if response.json()["result_code"] == "0":
            return response
        else:
            msg = f"{method} {route} {response.json()['msg']}"
            log.warn(msg)
            raise ConnectionError(msg)

    def dataset_file_complete_multipart(
        self,
        dataset_id,
        filename,
        upload_type,
        size,
        upload_id,
        uuid,
    ):
        method = "POST"
        route = "/attachments/complete_multipart"
        params = {
            "dataset_id": dataset_id,
            "file_name": filename,
            "type": upload_type,
            "size": size,
            "uploadID": upload_id,
            "uuid": uuid,
        }
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def dataset_download_file(
        self,
        uuid: str,
        upload_type: int,
    ):
        method = "GET"
        route = f"/attachments/{uuid}"
        params = {"type": upload_type}
        response = self.send_api(
            method,
            route,
            params=params,
            allow_redirects=True,
            stream=True,
        )
        return response

    """
    model management api
    """

    def model_create(
        self,
        repo_id,
        model_name,
        upload_type=1,
        engine=0,
        is_private=True,
    ):
        method = "POST"
        route = f"/repos/{repo_id}/modelmanage/create_local_model"
        params = dict(
            name=model_name,
            type=upload_type,
            engine=engine,
            isPrivate=is_private,
        )
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_query_by_id(self, repo_id, model_id):
        method = "GET"
        route = f"/repos/{repo_id}/modelmanage/query_model_byId"
        params = dict(id=model_id)  # {"id": model_id}
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_query_by_name(self, repo_id, model_name):
        method = "GET"
        route = f"/repos/{repo_id}/modelmanage/query_model_byName"
        params = dict(name=model_name)  # {"name": model_name}
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_file_query_by_id(self, repo_id, model_id):
        method = "GET"
        route = f"/repos/{repo_id}/modelmanage/query_modelfile_for_predict"
        params = dict(id=model_id)  # {"id": model_id}
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_download_all(self, repo_id, model_id):
        method = "GET"
        route = f"/repos/{repo_id}/modelmanage/downloadall"
        params = dict(id=model_id)  # {"id": model_id}
        response = self.send_api(method, route, params=params, stream=True)
        return response

    def model_download_single(
        self,
        repo_id,
        model_id,
        filename,
    ):
        method = "GET"
        route = f"/repos/{repo_id}/modelmanage/downloadsingle/{model_id}"
        params = dict(fileName=filename)
        response = self.send_api(
            method, route, params=params, allow_redirects=True, stream=True
        )
        return response

    def model_file_get_chunks(
        self,
        modeluuid,
        md5,
        filename,
        upload_type,
    ):
        method = "GET"
        route = f"/attachments/model/get_chunks"
        params = dict(
            modeluuid=modeluuid,
            md5=md5,
            file_name=filename,
            type=upload_type,
        )
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_file_new_multipart(
        self,
        modeluuid,
        md5,
        filename,
        upload_type,
        total_chunks_count,
        size,
    ):
        method = "GET"
        route = f"/attachments/model/new_multipart"
        params = dict(
            modeluuid=modeluuid,
            md5=md5,
            file_name=filename,
            type=upload_type,
            totalChunkCounts=total_chunks_count,
            size=size,
        )
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    def model_file_get_multipart_url(
        self,
        upload_type,
        chunk_number,
        chunk_size,
        upload_id,
        uuid,
    ):
        method = "GET"
        route = f"/attachments/model/get_multipart_url"
        params = dict(
            type=upload_type,
            chunkNumber=chunk_number,
            size=chunk_size,
            uploadID=upload_id,
            uuid=uuid,
        )
        response = self.send_api(method, route, params=params)
        # log.response(f" {route} {response.json()}")
        return response

    def model_file_complete_multipart(
        self,
        modeluuid,
        upload_type,
        upload_id,
        uuid,
    ):
        method = "POST"
        route = f"/attachments/model/complete_multipart"
        params = dict(
            modeluuid=modeluuid,
            type=upload_type,
            uploadID=upload_id,
            uuid=uuid,
        )
        response = self.send_api(method, route, params=params)
        log.response(f" {route} {response.json()}")
        return response

    """
    AI tasks apis
    """

    def aitask_repo_list(
        self,
        repo_id,
        job_type: str = "DEBUG",
        compute_resource: str = "GPU",
        page: int = 1,
    ):
        """
        test
        """
        method = "GET"
        route = f"/{repo_id}/ai_task/list"
        params = dict(
            job_type=job_type,
            compute_resource=compute_resource,
            page=page,
        )
        response = self.send_api(method, route, params=params)
        return response
