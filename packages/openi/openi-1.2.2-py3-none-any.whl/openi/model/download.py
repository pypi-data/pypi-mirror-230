import os

from ..utils import logger, constants
from ..utils.logger import *
from ..services import *

log = logger.setup_logger()


def download_model(
    repo_id: str,
    model_name: str,
    save_path: str = constants.PATH.MODEL_SAVE_PATH,
):
    """
    download a list of model files from OpenI

    :param repo_id: repo id in form of `owner/repo_name`
    :param model_name: name of model shown on web page
    :param save_path: local save path, default is `./model`
    :return:

    e.g.
    >>> from openi.model import download_model
    >>> download_model("openi/official", "chatglm2b", save_path="mydata")

    Complete(…kenizer_config.json): 100%|█████████████████████████████████████████████████| 244B/244B [00:00<00:00, 795B/s]
    Complete(         config.json): 100%|███████████████████████████████████████████| 1.19kB/1.19kB [00:00<00:00, 1.71kB/s]
    Complete(      .gitattributes): 100%|███████████████████████████████████████████| 1.48kB/1.48kB [00:00<00:00, 1.15kB/s]
    Complete(…guration_chatglm.py): 100%|█████████████████████████████████████████████| 2.19kB/2.19kB [00:01<00:00, 859B/s]
    Complete(       MODEL_LICENSE): 100%|█████████████████████████████████████████████| 4.04kB/4.04kB [00:01<00:00, 686B/s]
    Complete(           README.md): 100%|█████████████████████████████████████████████| 7.89kB/7.89kB [00:01<00:00, 575B/s]
    Complete(…nization_chatglm.py): 100%|█████████████████████████████████████████████| 9.83kB/9.83kB [00:02<00:00, 491B/s]
    Complete(     quantization.py): 100%|█████████████████████████████████████████████| 14.3kB/14.3kB [00:02<00:00, 432B/s]
    Complete(…odel.bin.index.json): 100%|█████████████████████████████████████████████| 20.0kB/20.0kB [00:02<00:00, 384B/s]
    Complete( modeling_chatglm.py): 100%|█████████████████████████████████████████████| 49.5kB/49.5kB [00:02<00:00, 344B/s]
    Complete(     tokenizer.model): 100%|███████████████████████████████████████████████| 995kB/995kB [00:03<00:00, 311B/s]
    Downloading(…-00001-of-00007.bin):   35%|██████████████████████                         | 0.34GB/0.98GB [00:03<?, ?B/s]
    Waiting(…-00002-of-00007.bin):   0%|                                                     | 0.00B/1.69GB [00:00<?, ?B/s]

    """

    log.info(f"{'-'*200}")
    log.info(f"params - {locals()}")
    openi_repo = OpeniRepo(repo_id=repo_id)
    if openi_repo.access not in ["read", "write"]:
        msg = f"`{repo_id}` 无权限操作此仓库"
        log.error(msg)
        raise ValueError(msg)

    openi_model = OpeniModel(
        model_name=model_name,
        repo_id=openi_repo.repo_id,
    )
    if openi_model.model_files == []:
        msg = f"❌ `{model_name}` 未找到文件"
        log.error(msg)
        raise ValueError(msg)
    if openi_model.can_download is False:
        msg = f"❌ 本机登录用户无此模型下载权限，模型名称 `{openi_model.model_name}`, 仓库名称 `{openi_model.repo_id}`"
        log.error(msg)
        raise ValueError(msg)

    save_path = os.path.expanduser(save_path)
    local_dir = os.path.join(save_path, f"{model_name}")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir, exist_ok=True)

    openifiles = list()
    for targe_file in openi_model.model_files:
        openi_file = OpeniFileDownload(
            filename=targe_file["fileName"],
            size=targe_file["size"],
            local_dir=local_dir,
            repo_id=openi_repo.repo_id,
            dataset_or_model_id=openi_model.model_id,
            dataset_or_model_name=openi_model.model_name,
            target_type="model",
        )
        openifiles.append(openi_file)

    display_progress_bar(openifiles)
    for openi_file in openifiles:
        log.info(f"{'-'*100}")
        openi_file.download_with_tqdm()

    log.info(f"{'-'*200}")
