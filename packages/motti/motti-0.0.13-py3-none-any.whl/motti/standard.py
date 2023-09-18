from io import BytesIO
import base64
from PIL import Image
from datetime import datetime
import os
from typing import Optional, Union
from pathlib import Path
import argparse
import yaml
from dataclasses import dataclass, asdict

def pil2str(x):
    buffer = BytesIO()
    x.save(buffer, format='PNG')
    b64 = base64.b64encode(buffer.getvalue())
    res = str(b64, 'utf-8')
    return res


def str2pil(s):
    b64 = base64.b64decode(s.encode('utf-8'))
    return Image.open(BytesIO(b64))


def get_datetime():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def init_project_dir_with(project_dir="."):
    def f(*args, **kwargs):
        return os.path.join(project_dir, *args, **kwargs)
    return f


def is_abs_path(path: Union[Path, str]):
    if isinstance(path, Path):
        return path.is_absolute()
    elif isinstance(path, str):
        return os.path.isabs(path)
    else:
        raise NotImplementedError 
        return False


def load_yaml(path):
    return yaml.safe_load(open(path, 'r'))


def load_namespace(path):
    D = load_yaml(path)
    return argparse.Namespace(**D)


def pt_to_pil(images):
    """
    Convert a torch image to a PIL image.
    """
    images = (images / 2 + 0.5).clamp(0, 1)
    images = images.cpu().permute(0, 2, 3, 1).float().numpy()
    images = numpy_to_pil(images)
    return images


def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    if images.shape[-1] == 1:
        # special case for grayscale (single channel) images
        pil_images = [Image.fromarray(image.squeeze(), mode="L") for image in images]
    else:
        pil_images = [Image.fromarray(image) for image in images]

    return pil_images


def is_video_file(file_name):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']  # 添加其他视频文件格式
    return any(file_name.lower().endswith(ext) for ext in video_extensions)


def is_image_file(file_name):
    photo_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']  # 添加其他照片文件格式
    # 将文件名后缀转换为小写，并检查是否在照片文件后缀列表中
    return any(file_name.lower().endswith(ext) for ext in photo_extensions)


def is_document_file(file_name):
    document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.odt']  # 添加其他文档文件格式

    # 将文件名后缀转换为小写，并检查是否在文档文件后缀列表中
    return any(file_name.lower().endswith(ext) for ext in document_extensions)
