import glob
import logging
import os

from huggingface_hub import snapshot_download


def get_file_from_huggingface_hub(repo_id: str, cache_dir: str) -> None:
    """
    Downloads a file from the HuggingFace Hub.

    Args:
        repo_id (str): The repository ID of the file to download (i.e. MikeXydas/iris).
        cache_dir (str): The directory to download the file to.
    """
    folder_name = repo_id.split("/")[-1]
    cache_dir = cache_dir + '/' if cache_dir[-1] != '/' else cache_dir

    cached_datasets = list(map(os.path.basename, glob.glob(f"{cache_dir}*")))

    if folder_name not in cached_datasets:  # Check if file is already downloaded in cache
        os.mkdir(cache_dir + folder_name)
        snapshot_download(repo_id=repo_id, local_dir=cache_dir + folder_name,
                          repo_type="dataset", local_dir_use_symlinks=False,
                          ignore_patterns=["*.md", ".gitattributes"])
    else:
        logging.debug(f"Using cached version of {folder_name}")
