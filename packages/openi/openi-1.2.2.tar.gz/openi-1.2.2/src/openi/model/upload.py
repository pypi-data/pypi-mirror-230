from tqdm.auto import tqdm

from ..utils import logger, constants
from ..services import *

log = logger.setup_logger()


def upload_model(
    folder: str,
    repo_id: str,
    model_name: str,
):
    """
    upload a local dir (list of model files) to OpenI, not subfolder allowed

    :param folder: local folder name
    :param repo_id: repo id in form of `owner/repo_name`
    :param model_name: name of model shown on web page
    :return:

    e.g.
    >>> from openi.model import upload_model
    >>> upload_model("local_dir/chatglm2", "openi/official", "chatglm2b")

    Calculating file md5… (13/13) |███████████████████████████████████████████████████████████████████████████████| [00:00]
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
    Uploading(…-00001-of-00007.bin):   35%|██████████████████████                           | 0.34GB/0.98GB [00:03<?, ?B/s]
    Waiting(…-00002-of-00007.bin):   0%|                                                     | 0.00B/1.69GB [00:00<?, ?B/s]

    """

    log.info(f"{'-'*200}")
    log.info(f"params - {locals()}")

    # OpeniFileUpload
    local_dir, targe_files = get_upload_folder_files(folder)
    if targe_files == []:
        msg = f"❌ {local_dir} 未找到任何本地文件"
        log.error(msg)
        raise ValueError(msg)

    # OpeniRepo, check repo_id, access
    openi_repo = OpeniRepo(repo_id=repo_id)

    # OpeniModel
    openi_model = OpeniModel(
        model_name=model_name,
        repo_id=openi_repo.repo_id,
    )
    if openi_model.can_operate is False:
        msg = f"❌ `{openi_repo.current_user}` 无此模型上传权限，模型名称 `{openi_model.model_name}`, 仓库名称 `{openi_model.repo_id}`"
        log.error(msg)
        raise ValueError(msg)
    if openi_model.model_type == 0:
        msg = f"❌ `{openi_model.model_name}` 为线上模型，无法上传本地文件"
        log.error(msg)
        raise ValueError(msg)

    # openifiles
    tiltle_pbar = tqdm(
        total=len(targe_files),
        leave=True,
        bar_format="{desc}({n_fmt}/{total_fmt}) |{bar}| [{elapsed}]",
        desc=f"Calculating file md5… ",
        position=0,
    )
    openifiles = list()
    for file in targe_files:
        openi_file = OpeniFileUpload(
            local_file=file,
            repo_id=openi_repo.repo_id,
            upload_type=constants.FILE.DEFAULT_UPLOAD_TYPE,
            dataset_or_model_id=openi_model.model_id,
            dataset_or_model_name=openi_model.model_name,
            target_type="model",
        )
        tiltle_pbar.update(1)
        openifiles.append(openi_file)
    # tiltle_pbar.close()

    # # Display pbar
    display_progress_bar(openifiles)

    # # Upload
    for openi_file in openifiles:
        log.info(f"{'-'*200}")
        openi_file.upload_with_tqdm()

    log.info(f"{'-'*200}")
