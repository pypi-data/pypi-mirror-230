import numpy as np
import cv2
from warnings import filterwarnings
from basic_image_preprocessing.exception.custom_exception import CustomException
from basic_image_preprocessing.utility.utlity import load_image, plot_graph, validate_channel_param, \
    validate_param_list_value, validate_cmap_value
from typing import List, Union

filterwarnings('ignore')


class TraditionalImageEnhancement:
    """
    This class contains the linear transformation methods
    that can be applied on the image.

    Input for Constructor:
    image_path -> image file path to read the image from
    cmap -> to know whether the image is a gray scale image or a color image.
        Accepted Values -> gray and rgb

    List of Linear Transformation methods available:
    1. linear_equation(slope: Union[int, float], constant: Union[int, float], cmap: str = None,
                        channel: List[int] = None) -> np.ndarray
    """
    def __init__(self, image_path: str, cmap: str):
        try:
            self.image_path = image_path
            self.is_color_image = False

            self.image, self.is_color_image = load_image(self.image_path, cmap)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.image_path}")

        except CustomException as ex:
            raise ex

    def linear_equation(self, slope: Union[int, float], constant: Union[int, float], cmap: str = None,
                        plot_output: bool = True,
                        channel: List[int] = None) -> np.ndarray:
        """
        This definition will apply the linear equation formula on the given image
        with the slope and constant value given in the parameters

        Input:
            slope -> slope value to be used for the linear equation
            constant -> constant value to be used for the linear equation
            cmap -> This value will denote on which plane the transformation needs to be applied on provided the cmap
                during object creation was mentioned as rgb
                Accepted value:
                    'gray' -> will apply the transformation on the gray scale image
                    'rgb' -> will apply the transformation on the channels given in 'channels' list. By default, apply
                            transformation on all the three channels
                    'hsv' -> will apply the transformation only on the value channel. If the channel param is specified,
                            will throw an error
                    'lab' -> will apply the transformation only on the lightness channel. If the channel param is
                            specified will throw an error

                Default value -> None. Will default to the cmap value specified during the object creation

            plot_output -> This is a boolean value which will instruct the program whether to display the
                        images post pre-processing or not. Will throw value error if value other than the accepted value
                        passed
                Accepted values - True , False

            channel -> Specify the channel index on which the transformation to be applied. Only allowed when the
                cmap = 'rgb'. Throws error when the cmap is 'hsv' or 'lab'
                Default value -> None
                Accepted value -> [0, 1, 2]
        Output:
            numpy.ndarray -> image post applying the linear equation formula on the given image
        """
        try:
            validate_cmap_value(cmap, 'Linear Equation', 'cmap')

            is_hsv = True if cmap is not None and cmap.lower() == 'hsv' else False
            is_lab = True if cmap is not None and cmap.lower() == 'lab' else False

            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            if not self.is_color_image:
                image = self.image.astype('float')
                image = np.clip(slope * image + constant, 0, 255).astype(np.uint8)
            else:
                image = self.image.copy()

                # Convert the rgb image to the required cmap color scale
                if is_hsv:
                    if channel is not None:
                        raise CustomException("Linear equation can be applied only on the Value channel for a HSV "
                                              "type image. Remove the channel parameter")
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                elif is_lab:
                    if channel is not None:
                        raise CustomException("Linear equation can be applied only of the Lightness channel for a LAB "
                                              "type image. Remove the channel parameter")
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

                # Apply the transformation on the default planes when the channel value is None
                if channel is None:
                    if is_hsv:
                        image[:, :, 2] = np.clip(slope * image[:, :, 2] + constant, 0, 255)

                    elif is_lab:
                        image[:, :, 0] = np.clip(slope * image[:, :, 0] + constant, 0, 255)

                    else:
                        image = np.clip(slope * image + constant, 0, 255)
                else:
                    # If the channel validation passes, then apply the transformation on the specified planes
                    if validate_channel_param(channel=channel):
                        for x in channel:
                            image[:, :, x] = np.clip(slope * image[:, :, x] + constant, 0, 255)

                if is_hsv:
                    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
                if is_lab:
                    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

                image = image.astype(np.uint8)
            if plot_output:
                plot_graph(self.image, image, self.is_color_image, 'Linear Equation')

            return image

        except TypeError as ex:
            raise TypeError(f"Type Error encountered in the method - {ex}. Please validate if proper value given "
                            f"for slope and constant")

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the linear equation on the given image - {ex}")

    def non_linear_equation(self, method: str, power_value: Union[int, float] = None, cmap: str = None,
                            plot_output: bool = True,
                            channel: List[int] = None) -> np.ndarray:
        """
        This definition will apply the non-linear equation on the given image
        with the value and method given in the parameters

        Input:
            power_value -> This is the value that will be applied on the image for the power transformation. It is a
                mandatory param if the method = 'power' else it is non-mandatory and will take the default value of
                None

            method -> This value will instruct the definition on what type of non-linear transformation to be done on
                the image.
                Accepted values - 'power', 'exponential', 'log'
                Will throw an error if the string is different from the accepted values

            cmap -> This value will denote on which plane the transformation needs to be applied on provided the
                cmap during object creation was mentioned as rgb
                Accepted value:
                    'gray' -> will apply the transformation on the gray scale image
                    'rgb' -> will apply the transformation on the channels given in 'channels' list. By default,
                            apply transformation on all the three channels
                    'hsv' -> will apply the transformation only on the value channel. If the channel param is specified,
                            will throw an error
                    'lab' -> will apply the transformation only on the lightness channel. If the channel param is
                            specified will throw an error

                Default value -> None. Will default to the cmap value specified during the object creation

            plot_output -> This is a boolean value which will instruct the program whether to display the
                        images post pre-processing or not. Will throw value error if value other than the accepted value
                        passed
                Accepted values - True , False

            channel -> Specify the channel index on which the transformation to be applied. Only allowed when the
                cmap = 'rgb'. Throws error when the cmap is 'hsv' or 'lab'
                Default value -> None
                Accepted value -> [0, 1, 2]

        Output:
            numpy.ndarray -> image post applying the non-linear equation on the given image
        """

        try:
            power_value_custom_exception = f"power_value is a required param when applying the power transformation." \
                                           f" Please pass in the power_value parameter"

            log_method_custom_exception = f"Channel is a required param when applying log transformation on RGB image."

            validate_cmap_value(cmap, 'Non - Linear', 'cmap')
            validate_param_list_value(method, ['power', 'exponential', 'log'], 'Non - Linear', 'method')

            is_hsv = True if cmap is not None and cmap.lower() == 'hsv' else False
            is_lab = True if cmap is not None and cmap.lower() == 'lab' else False

            # Validating if power_value is available if the method is 'power'
            if method == 'power' and power_value is None:
                raise CustomException(power_value_custom_exception)

            elif method == 'log' and (not is_hsv and not is_lab) and (channel is None):
                raise CustomException(log_method_custom_exception)

            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            if not self.is_color_image:
                image = self.image.astype('float')

                if method == 'power':
                    image = np.clip(np.power(image, power_value), 0, 255).astype(np.uint8)

                elif method == 'exponential':
                    image = np.clip(np.exp(image), 0, 255).astype(np.uint8)

                elif method == 'log':

                    image = np.clip(np.log1p(image), 0, 255).astype(np.uint8)

            else:
                image = self.image.copy()

                if is_hsv:
                    if channel is not None:
                        raise CustomException("Non - Linear equation can be applied only on the Value channel for a HSV"
                                              " type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                elif is_lab:
                    if channel is not None:
                        raise CustomException("Non - Linear equation can be applied only of the Lightness channel for a"
                                              " LAB type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

                # Apply the transformation on the default planes when the channel value is None
                if channel is None:
                    if is_hsv:
                        if method == 'power':
                            image[:, :, 2] = np.clip(np.power(image[:, :, 2], power_value), 0, 255)

                        if method == 'exponential':
                            image[:, :, 2] = np.clip(np.exp(image[:, :, 2]), 0, 255)

                        if method == 'log':
                            image[:, :, 2] = np.clip(np.log1p(image[:, :, 2]), 0, 255)

                    elif is_lab:

                        if method == 'power':
                            image[:, :, 0] = np.clip(np.power(image[:, :, 0], power_value), 0, 255)

                        if method == 'exponential':
                            image[:, :, 0] = np.clip(np.exp(image[:, :, 0]), 0, 255)

                        if method == 'log':
                            image[:, :, 0] = np.clip(np.log1p(image[:, :, 0]), 0, 255)

                    else:
                        if method == 'power':
                            image = np.clip(np.power(image, power_value), 0, 255)

                        elif method == 'exponential':
                            image = np.clip(np.exp(image), 0, 255)

                else:
                    # If the channel validation passes, then apply the transformation on the specified planes
                    if validate_channel_param(channel=channel):
                        if method == 'power':
                            for x in channel:
                                image[:, :, x] = np.clip(np.power(image[:, :, x], power_value), 0, 255)
                        if method == 'log':
                            for x in channel:
                                image[:,:,x] = np.clip(np.log1p(image[:, :, x]), 0, 255)

                if is_hsv:
                    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
                if is_lab:
                    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

                image = image.astype(np.uint8)

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Non Linear method - {method}')

            return image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the non-linear equation "
                            f"on the given image - {ex}")

    def math_operation(self, method: str, value: Union[int, float], cmap: str = None, plot_output: bool = True
                       , channel: List[int] = None) -> np.ndarray:
        """
        This definition will apply the mathematical operation on the given image
        with the value and method given in the parameters

        Input:
            value -> This is the value that will be applied on the image for all the transformation. It is a
                mandatory param

            method -> This value will instruct the definition on what type of mathematical transformation to be
                done on the image.
                Accepted values - addition', 'subtraction', 'multiplication', 'division'
                Will throw an error if the string is different from the accepted values

            cmap -> This value will denote on which plane the transformation needs to be applied on provided the
                cmap during object creation was mentioned as rgb
                Accepted value:
                    'gray' -> will apply the transformation on the gray scale image
                    'rgb' -> will apply the transformation on the channels given in 'channels' list. By default,
                            apply transformation on all the three channels
                    'hsv' -> will apply the transformation only on the value channel. If the channel param is specified,
                            will throw an error
                    'lab' -> will apply the transformation only on the lightness channel. If the channel param is
                            specified will throw an error

                Default value -> None. Will default to the cmap value specified during the object creation

            plot_output -> This is a boolean value which will instruct the program whether to display the
                        images post pre-processing or not. Will throw value error if value other than the accepted value
                        passed
                Accepted values - True , False

            channel -> Specify the channel index on which the transformation to be applied. Only allowed when the
                cmap = 'rgb'. Throws error when the cmap is 'hsv' or 'lab'
                Default value -> None
                Accepted value -> [0, 1, 2]

        Output:
            numpy.ndarray -> image post applying the non-linear equation on the given image
        """

        try:
            custom_exception = f"value is a required param when applying the mathematical transformation." \
                                           f" Please pass in the value parameter"

            validate_cmap_value(cmap, 'Mathematical Operations', 'cmap')

            validate_param_list_value(method, ['addition', 'subtraction', 'multiplication', 'division'],
                                      'Mathematical operations', 'method')

            is_hsv = True if cmap is not None and cmap.lower() == 'hsv' else False
            is_lab = True if cmap is not None and cmap.lower() == 'lab' else False

            # Validating if value is available for the method
            if method and value is None:
                raise CustomException(custom_exception)

            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            if not self.is_color_image:
                image = self.image.astype(float)

                if method == 'addition':
                    image = np.clip(image+value, 0, 255).astype(np.uint8)

                elif method == 'subtraction':
                    image = np.clip(image - value, 0, 255).astype(np.uint8)

                elif method == 'multiplication':
                    image = np.clip(image * value, 0, 255).astype(np.uint8)

                else:
                    image = np.clip(image//value, 0, 255).astype(np.uint8)

            else:
                image = self.image.copy().astype(np.float32)

                if is_hsv:
                    if channel is not None:
                        raise CustomException("Mathematical operation can be applied only on the Value channel for a HSV"
                                              " type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                elif is_lab:
                    if channel is not None:
                        raise CustomException("Mathematical operation can be applied only of the Lightness channel for a"
                                              " LAB type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

                # Apply the transformation on the default planes when the channel value is None
                if channel is None:
                    if is_hsv:
                        if method == 'addition':
                            image[:, :, 2] = np.clip(image[:, :, 2] + value, 0, 255)

                        elif method == 'subtraction':
                            image[:, :, 2] = np.clip(image[:, :, 2] - value, 0, 255)

                        elif method == 'multiplication':
                            image[:, :, 2] = np.clip(image[:, :, 2] * value, 0, 255)

                        else:
                            image[:, :, 2] = np.clip(image[:, :, 2]//value, 0, 255)

                    elif is_lab:
                        if method == 'addition':
                            image[:, :, 0] = np.clip(image[:, :, 0] + value, 0, 255)

                        elif method == 'subtraction':
                            image[:, :, 0] = np.clip(image[:, :, 0] - value, 0, 255)

                        elif method == 'multiplication':
                            image[:, :, 0] = np.clip(image[:, :, 0] * value, 0, 255)

                        else:
                            image[:, :, 0] = np.clip(image[:, :, 0] // value, 0, 255)

                    else:
                        if method == 'addition':
                            image = np.clip(image + value, 0, 255)

                        elif method == 'subtraction':
                            image = np.clip(image - value, 0, 255)

                        elif method == 'multiplication':
                            image = np.clip(image * value, 0, 255)

                        else:
                            image = np.clip(image // value, 0, 255)
                else:
                    # If the channel validation passes, then apply the transformation on the specified planes
                    if validate_channel_param(channel=channel):
                        if method == 'addition':
                            for x in channel:
                                image[:, :, x] = np.clip(image[:, :, x] + value, 0, 255)
                        elif method == 'subtraction':
                            for x in channel:
                                image[:, :, x] = np.clip((image[:, :, x] - value), 0, 255)
                        elif method == 'multiplication':
                            for x in channel:
                                image[:, :, x] = np.clip((image[:, :, x] * value), 0, 255)
                        else:
                            for x in channel:
                                image[:, :, x] = np.clip((image[:, :, x] // value), 0, 255)

                if is_hsv:
                    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
                if is_lab:
                    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

                image = image.astype(np.uint8)

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Math Operation - {method}')

            return image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the Math operation on the given image - {ex}")

