import os
import cv2
import numpy as np
from basic_image_preprocessing.exception.custom_exception import CustomException
import matplotlib.pyplot as plt
from typing import List, Tuple
import re


def load_image(image_path: str, cmap: str) -> Tuple[np.ndarray, bool]:
    """
    load_image -> The definition will be used to load the image from the
    file path and return the loaded image to the calling definition.
    This is a generic definition which will be used across the project
    for loading the image from a file path

    :param image_path:
    :param cmap: Allowed value for cmap are 'gray' and 'rgb'
    :return numpy.ndarray:
    """
    is_color_image = False
    if os.path.exists(image_path):
        if cmap.lower() == 'gray':
            image = cv2.imread(f"{image_path}", 0)

        elif cmap.lower() == 'rgb':
            image = cv2.imread(f"{image_path}", cv2.IMREAD_UNCHANGED)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        else:
            raise CustomException("Invalid cmap value specified. cmap value can only be either gray or rgb")

        if image is None:
            raise CustomException("Unable to read the image. Please check the image path")

        if cmap.lower() == 'rgb':
            is_color_image = True

        return image, is_color_image
    else:
        raise FileNotFoundError(f"File not found: {image_path}")


def plot_graph(original_image, processed_image, is_color_image_flag, pre_processing_method,
               is_edge_detection: bool = False) -> None:
    """
    plot_graph -> A generic definition to plot the original image and the processed image side
    by side for comparison purposes

    :param original_image: Original image on which the transformation was performed
    :param processed_image: Image after the transformation is applied
    :param is_color_image_flag: Flag to identify if it's a color and black and white image
    :param pre_processing_method: String representing the Transformation type
    :param is_edge_detection: Flag to denote if is an edge detection algorithm
    :return None:
    """
    plt.figure(figsize=(20, 10))

    plt.subplot(1, 3, 1)
    plt.title("Original Image")
    if is_color_image_flag:
        plt.imshow(original_image)
    else:
        plt.imshow(original_image, cmap="gray")

    plt.subplot(1, 3, 2)
    plt.title(f"Image post applying the {pre_processing_method} transformation")
    if (is_color_image_flag and is_edge_detection) or (not is_color_image_flag):
        plt.imshow(processed_image, cmap="gray")
    else:
        plt.imshow(processed_image)


def validate_channel_param(channel: List[int]) -> bool:
    """
    Definition to validate if the given channel param satisfy all the required conditions
    :param channel:
    :return bool:
    """
    if any(type(x) != int for x in channel):
        raise CustomException(f"channel parameter can take only integer values")

    if len(channel) > 3:
        raise CustomException(f"channel parameter excepts 1 - 3 values; but received {len(channel)}")

    if any(x > 2 for x in channel):
        raise CustomException(f"channel parameter can have values as 0, 1, 2. No other values are allowed")

    return True


def validate_param_list_value(value: str, list_of_accepted_values: List[str],
                              function_name: str, param_name: str) -> bool:
    """
    Definition used to verify whether the given value is available in the list of accepted values for the
    particular parameter
    :param value:
    :param list_of_accepted_values:
    :param function_name:
    :param param_name:
    :return:
    """
    if value not in list_of_accepted_values:
        raise CustomException(f"In {function_name} transformation the '{param_name}' param can take only one of the "
                              f"string available in {list_of_accepted_values}")
    return True


def validate_cmap_value(value, function_name: str, param_name: str) -> bool:
    """
    Definition to validate if the cmap value given in the definitions are
    one among the below values:
    [ gray, rgb, hsv, lab ]
    :param value:
    :param function_name:
    :param param_name:
    :return:
    """
    list_of_accepted_values = ['gray', 'rgb', 'hsv', 'lab']

    if value is not None and value.lower() not in list_of_accepted_values:
        raise ValueError(f"In {function_name} transformation the '{param_name}' param can take only one of the string "
                         f"available in {list_of_accepted_values}")
    return True


def validate_param_type(param_name, param_value, param_type, expected_type) -> None:
    """
    Definition to validate if the param type is same as specified in the definition
    If not an error is raised
    :param param_name:
    :param param_value:
    :param param_type:
    :param expected_type:
    :return:
    """
    if param_value is not None:
        if param_type != expected_type:
            raise ValueError(f"{param_name} is expected to be in {expected_type} but received value is {param_type}")


def create_kernel_mask(kernel_size: int, kernel_type: str, custom_edge_kernel: np.ndarray = None) -> np.ndarray:
    """
    Create a kernel mask for image processing based on the kernel_type passed.

    Parameters:
        kernel_size (int): The size of the kernel mask (should be odd).
        kernel_type (str): The type of kernel to create.
                        Possible values: 'identity', 'box', 'gaussian', 'sharpen', 'edge_detection', 'mean', 'custom'
                        Default is 'identity'.
        custom_edge_kernel (np.ndarray): A custom edge detection kernel provided by the user.
                                         It should be a 2D square matrix ndArray element which has the
                                         rows and columns value equivalent to the size parameter.
                                         Mandatory when the kernel_type is 'custom'
                                         Default is None.
    Returns:
        np.ndarray: The returned kernel mask is a 2D numpy array.
    """
    kernel = None
    if kernel_size % 2 == 0 or kernel_size <= 0:
        raise ValueError("Size of the kernel mask should be a positive odd integer.")

    if custom_edge_kernel is not None:
        if custom_edge_kernel.shape[0] != kernel_size or custom_edge_kernel.shape[1] != kernel_size:
            raise ValueError("The rows and columns for the custom kernel array should be equal to the specified"
                             " kernel size")

    if kernel_type == 'identity':
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        center = kernel_size // 2
        kernel[center, center] = 1.0

    elif kernel_type == 'box':
        kernel = np.ones((kernel_size, kernel_size), dtype=np.float32)

    elif kernel_type == 'gaussian':
        sigma = kernel_size / 6  # You can adjust the sigma value for different levels of blur.
        x, y = np.meshgrid(np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size),
                           np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size))
        kernel = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
        kernel /= kernel.sum()

    elif kernel_type == 'sharpen':
        kernel = -np.ones((kernel_size, kernel_size), dtype=np.float32)
        center = kernel_size // 2
        kernel[center, center] = kernel_size * kernel_size

    elif kernel_type == 'mean':
        kernel = np.ones((kernel_size, kernel_size), dtype=np.float32)
        kernel = kernel / (kernel_size * kernel_size)

    elif kernel_type == 'edge_detection':
        # Default edge detection kernel (laplacian operator)
        kernel = -np.ones((kernel_size, kernel_size), dtype=np.float32)
        center = kernel_size // 2
        kernel[center, center] = kernel_size * kernel_size - 1

    elif kernel_type == 'custom':
        if custom_edge_kernel is None:
            raise ValueError("Custom edge detection kernel is required for 'custom' kernel_type.")
        kernel = custom_edge_kernel

    return kernel


def validate_wavelet_type(wavelet_name) -> None:
    """
    Definition used to validate if the given wavelet name
    is amoung the given list of accepted wavelet family names
    :param wavelet_name:
    :return:
    """
    wavelet_types = ['db', 'sym', 'coif', 'bior', 'haar']
    pattern = r'(?<=\D)(?=\d)'

    # Split the strings based on the regex pattern
    result = re.split(pattern, wavelet_name.lower(), maxsplit=1)

    if result[0] is not None:
        if result[0] not in wavelet_types:
            raise ValueError(f"In Wavelet transformation the 'wavelet_name' param can take only a starting string "
                             f"in {wavelet_types} list")
