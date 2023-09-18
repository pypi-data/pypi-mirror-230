# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import cv2
import numpy as np
from pathlib import Path


def read(img_path: Path):
    """
    读图片-兼容图片路径包含中文
    :param img_path:
    :return: np.ndarray
    """
    img = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    return img


def write(image: np.ndarray, img_write_path: Path):
    """
    写图片-兼容图片路径包含中文
    :param image:
    :param img_write_path:
    :return:
    """
    cv2.imencode(img_write_path.suffix, image[:, :, ::-1])[1].tofile(str(img_write_path))
