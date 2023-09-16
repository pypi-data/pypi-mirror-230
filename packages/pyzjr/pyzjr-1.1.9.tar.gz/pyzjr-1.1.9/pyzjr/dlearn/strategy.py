import numpy as np
from PIL import Image
import torch
import random
from thop import clever_format, profile
from torchsummary import summary

from pyzjr.video import Timer
from pyzjr.utils import gpu
from pyzjr.FM import getPhotopath


def cvtColor(image):
    """Convert to RGB format"""
    if len(np.shape(image)) == 3 and np.shape(image)[2] == 3:
        return image
    else:
        img = image.convert('RGB')
        return img

def show_config(**kwargs):
    """display configuration"""
    print('Configurations:')
    print('-' * 70)
    print('|%25s | %40s|' % ('keys', 'values'))
    print('-' * 70)
    for key, value in kwargs.items():
        print('|%25s | %40s|' % (str(key), str(value)))
    print('-' * 70)

def normalize_image(image, open=False):
    """
    将图像归一化到 [0, 1] 的范围
    :param image: 输入的图像
    :param open: 是否需要打开图像文件（默认为 False）
    :return: 归一化后的图像
    """
    if open:
        if isinstance(image, str):
            img_opened = Image.open(image)
            image = np.asarray(img_opened)
        else:
            raise ValueError("[pyzjr]:When `open` is True, `image` should be a file path string.")

    normalized_image = image / 255.0
    return normalized_image

def normalization1(image, mean, std):
    """ Normalization using mean and std
    Args :
        image : numpy array of image
        mean :
    Return :
        image : numpy array of image with values turned into standard scores
    """

    image = image / 255  # values will lie between 0 and 1.
    image = (image - mean) / std

    return image

def normalization2(image, max, min):
    """Normalization to range of [min, max]
    Args :
        image : numpy array of image
        mean :
    Return :
        image : numpy array of image with values turned into standard scores
    """
    image_new = (image - np.min(image))*(max - min)/(np.max(image)-np.min(image)) + min
    return image_new

def resizepad_image(image, size, frame=True):
    """
    将调整图像大小并进行灰度填充
    :param image: 输入图像, PIL Image 对象
    :param size: 目标尺寸，形如 (width, height)
    :param frame: 是否进行不失真的resize
    :return: 调整大小后的图像，PIL Image 对象
    """
    iw, ih = image.size
    w, h = size
    if frame:
        scale = min(w/iw, h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)

        image = image.resize((nw,nh), Image.BICUBIC)
        new_image = Image.new('RGB', size, (128,128,128))
        new_image.paste(image, ((w-nw)//2, (h-nh)//2))
        return new_image, nw, nh
    else:
        new_image = image.resize((w, h), Image.BICUBIC)
        return new_image

def seed_torch(seed=11):
    """
    :param seed:设置随机种子以确保实验的可重现性
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def summarys(input_shape, model):
    """
    打印模型的摘要信息，并计算模型的总浮点运算量和总参数数量
    :param input_shape:
    :param model:要进行计算的模型
    """
    device = gpu()
    models = model.to(device)
    summary(models, (3, input_shape[0], input_shape[1]))

    dummy_input = torch.randn(1, 3, input_shape[0], input_shape[1]).to(device)
    flops, params = profile(models.to(device), (dummy_input, ), verbose=False)
    flops = flops * 2
    flops, params = clever_format([flops, params], "%.3f")
    print('Total GFLOPS: %s' % (flops))
    print('Total params: %s' % (params))

def flip(image, option_value):
    """
    Args:
        image : numpy array of image
        option_value: random integer between 0 to 3
            vertical                          0
            horizontal                        1
            horizontally and vertically flip  2
    Return :
        image : numpy array of flipped image
    """
    if option_value == 0:
        image = np.flip(image, option_value)
    elif option_value == 1:
        image = np.flip(image, option_value)
    elif option_value == 2:
        image = np.flip(image, 0)
        image = np.flip(image, 1)
    else:
        image = image
        # no effect
    return image

def approximate_image(image):
    """
    Convert a single channel image into a binary image.
    Args:
        image : numpy array of image in datatype int16
    Return :
        image : numpy array of image in datatype uint8 only with 255 and 0
    """
    image[image > 127.5] = 255
    image[image < 127.5] = 0
    image = image.astype("uint8")
    return image

def ceilfloor_image(image):
    """
    The pixel value of the input image is limited between the maximum value of 255 and the minimum value of 0
    Args:
        image : numpy array of image in datatype int16
    Return :
        image : numpy array of image in datatype uint8 with ceilling(maximum 255) and flooring(minimum 0)
    """
    image[image > 255] = 255
    image[image < 0] = 0
    image = image.astype("uint8")
    return image

def find_mean(image_path):
    """
    Calculate the mean of all images under a given path
    Args:
        image_path : pathway of all images
    Return :
        mean : mean value of all the images
    """
    all_images,_ = getPhotopath(image_path,debug=False)
    num_images = len(all_images)
    mean_sum = 0

    for image in all_images:
        img_asarray = normalize_image(image, open=True)
        individual_mean = np.mean(img_asarray)
        mean_sum += individual_mean

    # Divide the sum of all values by the number of images present
    mean = mean_sum / num_images

    return mean

def find_stdev(image_path):
    """
    Args:
        image_path : pathway of all images
    Return :
        stdev : standard deviation of all pixels
    """
    # Initiation
    all_images,_ = getPhotopath(image_path, debug=False)
    num_images = len(all_images)

    std_sum = 0

    for image in all_images:
        img_asarray = normalize_image(image, open=True)
        individual_stdev = np.std(img_asarray)
        std_sum += individual_stdev

    std = std_sum / num_images

    return std


class Runcodes:
    """
    Comparison of runtime between different detection methods

    with Runcodes("inference time"):
        output = ...
    """
    def __init__(self, description='Done'):
        self.description = description

    def __enter__(self):
        self.timer = Timer()
        return self

    def __exit__(self, *args):
        print(f'{self.description}: {self.timer.stop():.5f} sec')