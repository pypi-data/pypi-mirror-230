from tqdm.auto import tqdm

from ..utils import logger, constants

log = logger.setup_logger()


def display_progress_bar(file_list: list):
    """
    display progress bar for files
    :param
        file_list: a list of OpeniFile objects contains "filename" and "size"
    """
    widths = [len(openi_file.filename) for openi_file in file_list]
    max_width = min(int(sum(widths) / len(widths)), 25)

    for index, openi_file in enumerate(file_list):
        filename, size = openi_file.filename, openi_file.size

        if len(filename) > max_width:
            title = "…" + filename[-1 * max_width :]
        else:
            title = filename.rjust(max_width + 1)

        desc = f"Waiting({title}): "
        if openi_file.target_type == "dataset":
            cluster = constants.FILE.UPLOAD_TYPE[openi_file.upload_type]
            desc = f"Waiting({title})({cluster}): "

        bar_format = (
            "{desc}{percentage:3.0f}%|{bar}| "
            "{n_fmt}{unit}/{total_fmt}{unit} "
            "[{elapsed}<{remaining}, "
            "{rate_fmt}{postfix}]"
        )
        pbar = tqdm(
            total=size,
            leave=True,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            bar_format=bar_format,
            desc=desc,
            position=index + 1,
            # dynamic_ncols=True,
            # ascii=True,
        )
        openi_file.pbar = pbar
