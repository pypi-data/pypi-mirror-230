import io, os
from pathlib import Path
import pickletools
import requests
from rich import print
import torch
from typing import IO, Optional, Union


# https://github.com/pytorch/pytorch/blob/664058fa83f1d8eede5d66418abff6e20bd76ca8/torch/serialization.py#L28
MAGIC_NUMBER = 0x1950a86a20f9469cfc6c

MAGIC_NUMBER_ZIP = b'PK\x03\x04'


def select_device(device: Optional[str] = None) -> str:
    if device is None or device not in ['cuda', 'cpu']:
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    return device


# copied from pytorch code
# https://github.com/pytorch/pytorch/blob/664058fa83f1d8eede5d66418abff6e20bd76ca8/torch/serialization.py#L272
def is_compressed_file(f: IO[bytes]) -> bool:
    compress_modules = ["gzip"]
    try:
        return f.__module__ in compress_modules
    except AttributeError:
        return False


# copied from pytorch code
# https://github.com/pytorch/pytorch/blob/664058fa83f1d8eede5d66418abff6e20bd76ca8/torch/serialization.py#L280
def should_read_directly(f: IO[bytes]) -> bool:
    """
    Checks if f is a file that should be read directly. It should be read
    directly if it is backed by a real file (has a fileno) and is not a
    a compressed file (e.g. gzip)
    """
    if is_compressed_file(f):
        return False
    try:
        return f.fileno() >= 0
    except io.UnsupportedOperation:
        return False
    except AttributeError:
        return False


# Check if the file is zip.
def is_zipfile(file_path: Optional[str] = None, data: Optional[IO[bytes]] = None) -> bool:
    # Reference: https://github.com/protectai/modelscan/blob/main/modelscan/tools/utils.py#L55

    if data is None:
        # Read bytes from the file path
        if file_path == "" and Path(file_path).is_file():
            with open(file_path, 'rb') as f:
                magic_bytes = f.read(4)
            if magic_bytes.startswith(MAGIC_NUMBER_ZIP):
                return True
    else:
        # Read bytes from data directly
        read_bytes = []
        start = data.tell()

        byte = data.read(1)
        while byte != b"":
            read_bytes.append(byte)
            if len(read_bytes) == 4:
                break
            byte = data.read(1)
        data.seek(start)
        return b"".join(read_bytes) == MAGIC_NUMBER_ZIP

    return False


def get_magic_number(data: IO[bytes]) -> Optional[int]:
    try:
        for opcode, args, _pos in pickletools.genops(data):
            if "INT" in opcode.name or "LONG" in opcode.name:
                data.seek(0)
                return int(args)
    except:
        return None
    
    return None
            

# Fetch URL and get contents.
def fetch_url(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(url, allow_redirects=False, timeout=10)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e.response.status_code}")
        return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"Invalid JSON")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error")
        return None
    except Exception as e:
        print(f"{e}")
        return None
    

def read_hf_file(repo_id: str, filename: str) -> Optional[bytes]:
    """
    Read a file from Hugging Face repository
    """
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    return fetch_url(url)


def get_download_path(dir_path: Optional[Union[str, Path]] = None, file_path: Optional[Union[str, Path]] = None) -> Union[str, Path]:
    if dir_path is None:
        return Path(file_path)
    else:
        return os.path.join(dir_path, file_path)
