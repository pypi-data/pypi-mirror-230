import os
import json
from pathlib import Path

# import textwrap

"""
File PATHs
"""


class PATH(object):
    OPENI_FOLDER = os.path.join(
        os.path.expanduser("~"),
        ".openi",
    )  # os.path.expanduser('~'), os.getcwd()
    TOKEN_PATH = os.path.join(OPENI_FOLDER, "token.json")
    LOG_PATH = os.path.join(OPENI_FOLDER, "log")
    DATASET_SAVE_PATH = os.path.join(os.getcwd(), "dataset")
    MODEL_SAVE_PATH = os.path.join(os.getcwd(), "model")
    TOKEN_PATTERN = r"^[0-9a-fA-F]{40}$"


if not os.path.exists(PATH.OPENI_FOLDER):
    os.mkdir(PATH.OPENI_FOLDER)
if not os.path.exists(PATH.LOG_PATH):
    os.mkdir(PATH.LOG_PATH)

"""
API
"""


class API(object):
    DEFAULT_ENDPOINT = "https://openi.pcl.ac.cn"
    VERSION = "/api/v1"
    ENGINE_TYPE = [
        "pytorch",
        "tensorflow",
        "mindspore",
        "paddlepaddle",
        "oneflow",
        "mxnet",
        "other",
    ]


"""
FILE
"""


class FILE(object):
    # SOTRAGE_TYPE = {"GPU": 0, "NPU": 1, "gpu": 0, "npu": 0}
    MAX_FILE_SIZE_GB = 200
    MAX_CHUNKS = 10000
    SMALL_FILE_CHUNK_SIZE = 1024 * 1024 * 8
    LARGE_FILE_CHUNK_SIZE = 1024 * 1024 * 64
    MAX_FILE_SIZE = 1024 * 1024 * 1024 * MAX_FILE_SIZE_GB
    SMALL_FILE_LIMIT = 1024 * 1024 * 8 * MAX_CHUNKS

    DEFAULT_UPLOAD_TYPE = 1
    UPLOAD_TYPE = ["gpu", "npu"]


"""
CLI help 
"""


class CLI(object):
    # main help page
    banner = "OpenI command line tool 启智AI协作平台命令行工具"

    usage = "openi {login, whoami, dataset, ...} [<args>] [-h]"
    command_login = "使用令牌登录启智并保存到本机"
    command_logout = "登出当前用户并删除本地令牌文件"
    command_whoami = "查询当前登录用户"
    command_dataset = "{upload,download} 上传/下载启智AI协作平台的数据集 "
    command_model = "{upload,download} 上传/下载启智AI协作平台的模型 "

    # Login
    login_usage = "openi login [-t token] [-e endpoint] [-h]"
    param_token = (
        "选填: 替代命令行输入，启智账号令牌，https://openi.pcl.ac.cn/user/settings/applications"
    )
    param_endpoint = "选填: 仅内部使用"

    # Dataset
    dataset_choices = ["upload", "download"]
    dataset_usage = "openi dataset {upload,download} [<args>] [-h]"

    command_dataset_upload = "上传数据集文件，需指定文件名,仓库路径及存储类型"
    dataset_upload_help = "上传数据集文件, openi dataset upload -h 查看更多说明"
    dataset_upload_usage = (
        "openi dataset upload [-f file] [-r repo_id] [-c cluster] [-h]"
    )
    dataset_upload_param_file = "本地文件名称，包含文件路径"
    dataset_upload_param_repo_id = "所在仓库路径，格式为`拥有者/仓库名`，登录用户需要拥有此仓库权限"
    dataset_upload_param_cluster = "选填: 文件的存储集群，仅支持小写，默认为`npu`"
    # dataset_upload_epilog = textwrap.dedent(
    #     """
    #     用法说明：\n
    #     登录用户为user1，并且为user2/repo2仓库的协作者 \n
    #     用法一: openi dataset upload data1.zip user1/repo1 gpu
    #     上传本地文件`data1.zip`到repo1仓库数据集，存储类型为GPU \n
    #     用法二: openi d upload localDir/data2.zip user2/repo2
    #     上传本地文件`./localDir/data2.zip`到协作仓库user2/repo2，存储类型为NPU \n
    #     """)

    command_dataset_download = "下载数据集文件，需指定文件名,仓库路径及存储类型"
    dataset_download_help = "下载数据集文件, openi dataset download -h 查看更多说明"
    dataset_download_usage = (
        "openi dataset download "
        "[-f file] [-r repo_id] "
        "[-c cluster] [-p save_path] [-h]"
    )
    dataset_download_param_file = "网页端数据集文件名称，只能下载`.zip`或`.tar.gz`格式的文件"
    dataset_download_param_save_path = "选填: 本地的保存路径，默认为在当前路径下创建`dataset`目录"
    # dataset_download_epilog = textwrap.dedent(
    #     """
    #     用法说明： \n
    #     登录用户为user1，并且为user2/repo2仓库的协作者\n
    #     用法一: openi dataset download data1.zip user1/repo1 gpu -p /downloads
    #     从repo1仓库下载`data1.zip`(GPU)数据集文件，并存到本地`/downloads/data1.zip`\n
    #     用法二: openi d download data2.zip user2/repo2
    #     从协作仓库user2/repo2下载`data2.zip`(NPU)数据集文件，并存到本地`./dataset/data2.zip`\n
    #     """)

    # Model
    model_choices = ["upload", "download"]
    model_usage = "openi model {upload,download} [<args>] [-h]"

    command_model_upload = "上传模型文件夹，需指定本地路径,仓库路径及模型名称"
    model_upload_help = "上传模型文件夹, openi model upload -h 查看更多说明"
    model_upload_usage = (
        "openi model upload [-f folder] [-r repo_id] [-m model_name] [-h]"
    )
    model_upload_param_folder = "本地文件夹路径，路径下可包含多个模型文件，不能包含子目录"
    model_upload_param_repo_id = "所在仓库路径，格式为`拥有者/仓库名`，登录用户需要拥有此仓库权限"
    model_upload_param_model_name = "网页端模型名称"

    command_model_download = "下载模型文件夹，需指定仓库路径及模型名称"
    model_download_help = "下载模型文件夹, openi model download -h 查看更多说明"
    model_download_usage = (
        "openi model download [-r repo_id] [-m model_name]  [-p save_path] [-h]"
    )
    model_download_param_save_path = "选填: 本地的保存路径，默认为在当前路径下创建`model`目录"
