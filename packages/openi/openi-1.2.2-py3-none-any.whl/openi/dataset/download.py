import os
import re

from ..utils import logger, constants
from ..services import *

log = logger.setup_logger()


def download_file(
    file: str,
    repo_id: str,
    cluster: str = "npu",
    save_path: str = constants.PATH.DATASET_SAVE_PATH,
):
    """
    download a zip or tar.gz dataset file from OpenI

    :param file: dataset file name
    :param repo_id: repo id in form of `owner/repo_name`
    :param cluster: cluster type in [gpu,npu], default is `npu`
    :param save_path: local save path, default is `./dataset`
    :return:

    e.g.
    >>> from openi.dataset import download_file
    >>> download_file("cifar10.zip", "openi/official", cluster="gpu", save_path="mydata")

    Complete( cifar10.zip)(gpu): 100%|████████████████████████| 163MB/163MB [00:00<00:00, 54.0MB/s]

    """

    log.info(f"{'-'*200}")
    log.info(f"params - {locals()}")

    upload_type = get_upload_type(cluster)

    # Define a regex pattern to match the desired formats
    pattern = r"^.+\.(zip|tar\.gz)$"
    if not re.match(pattern, file):
        msg = f"❌ `{file}` 非压缩文件（`zip`或`tar.gz`）无法通过sdk下载"
        log.error(msg)
        raise ValueError(msg)

    openi_repo = OpeniRepo(repo_id=repo_id)
    if openi_repo.access not in ["read", "write"]:
        msg = f"`{repo_id}` 无权限操作此仓库"
        log.error(msg)
        raise ValueError(msg)

    openi_dataset = OpeniDataset(repo_id=openi_repo.repo_id)
    openi_dataset.get_dataset_file(upload_type=upload_type)
    targe_file = None
    log.info(f"openi_dataset.dataset_files,{openi_dataset.dataset_files}")
    if openi_dataset.dataset_files is not None:
        for f in openi_dataset.dataset_files:
            if f["name"] == file:
                targe_file = f
    log.info(f"targe_file,{targe_file}")
    if openi_dataset.dataset_files is None or targe_file is None:
        msg = (
            f"❌ `{openi_repo.repo_id}`-`{openi_dataset.dataset_name}` "
            f"数据集内未找到名为{file}({cluster})的文件"
        )
        log.error(msg)
        raise ValueError(msg)

    local_dir = os.path.expanduser(save_path)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir, exist_ok=True)

    openi_file = OpeniFileDownload(
        filename=targe_file["name"],
        size=targe_file["size"],
        local_dir=local_dir,
        repo_id=openi_repo.repo_id,
        dataset_or_model_id=openi_dataset.dataset_id,
        dataset_or_model_name=openi_dataset.dataset_name,
        target_type="dataset",
        upload_type=upload_type,
        uuid=targe_file["uuid"],
    )

    display_progress_bar([openi_file])
    openi_file.download_with_tqdm()

    log.info(f"{'-'*200}")
