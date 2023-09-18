import numpy as np
import cv2
from warnings import filterwarnings
from basic_image_preprocessing.exception.custom_exception import CustomException
from basic_image_preprocessing.utility.utlity import load_image, plot_graph, validate_channel_param, \
    validate_cmap_value, validate_param_type
from typing import List, Union

filterwarnings('ignore')


class ConventionalImageEnhancement:
    def __init__(self, image_path: str, cmap: str):
        try:
            self.image_path = image_path
            self.is_color_image = False

            self.image, self.is_color_image = load_image(self.image_path, cmap)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.image_path}")

        except CustomException as ex:
            raise ex

    def equalization_histogram(self, cmap: str = None,
                               plot_output: bool = True,
                               channel: List[int] = None) -> np.ndarray:
        """
        This definition will apply the histogram equalization transformation on the given image
        with the value and method given in the parameters

        Input:
            cmap -> This value will denote on which plane the transformation needs to be applied on, provided the
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
            numpy.ndarray -> image post applying the equalization equation on the given image
        """
        try:
            validate_cmap_value(cmap, 'Histogram Equalization', 'cmap')

            is_hsv = True if cmap is not None and cmap.lower() == 'hsv' else False
            is_lab = True if cmap is not None and cmap.lower() == 'lab' else False

            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            if not self.is_color_image:
                image = self.image
                image = cv2.equalizeHist(image)
            else:
                image = self.image.copy()
                if is_hsv:
                    if channel is not None:
                        raise CustomException("Equalization Histogram can be applied only on the Value channel for a"
                                              " HSV type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                elif is_lab:
                    if channel is not None:
                        raise CustomException("Equalization Histogram can be applied only of the Lightness channel for "
                                              "a LAB type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

                if channel is None:
                    if is_hsv:
                        image[:, :, 2] = np.clip(cv2.equalizeHist(image[:, :, 2]), 0, 255)
                    elif is_lab:
                        image[:, :, 0] = np.clip(cv2.equalizeHist(image[:, :, 0]), 0, 255)
                    else:
                        image[:, :, 0] = np.clip(cv2.equalizeHist(image[:, :, 0]), 0, 255)
                        image[:, :, 1] = np.clip(cv2.equalizeHist(image[:, :, 1]), 0, 255)
                        image[:, :, 2] = np.clip(cv2.equalizeHist(image[:, :, 2]), 0, 255)
                else:
                    # If the channel validation passes, then apply the transformation on the specified planes
                    if validate_channel_param(channel=channel):
                        for x in channel:
                            image[:, :, x] = np.clip(cv2.equalizeHist(image[:, :, x]), 0, 255)

                if is_hsv:
                    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
                if is_lab:
                    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

                image = image.astype(np.uint8)

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Equalization Histogram')

            return image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(
                f"An error occurred while trying to apply the Equalization Histogram on the given image - {ex}")

    def clahe(self, clip_value: Union[int, float] = 2.0, tile_grid_size: int = 8,
              cmap: str = None, plot_output: bool = True,
              channel: List[int] = None):

        """
        This definition will apply the CLAHE transformation on the given image
        with the defined parameter values

        Input:
            clip_value -> This parameter sets the threshold for contrast limiting. It is the contrast limit for
            localized changes in contrast.
                Accepted value -> Int or Float
                Default value -> 2.0

            tile_grid_size -> This sets the number of tiles in the row and column.
                It is used while the image is divided into tiles for applying CLAHE.

                Accepted value -> Int
                Default value -> 8

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
            numpy.ndarray -> image post applying the CLAHE transformation on the given image
        """

        try:
            validate_cmap_value(cmap, 'CLAHE', 'cmap')

            validate_param_type('tile grid size', tile_grid_size, type(tile_grid_size), int)

            is_hsv = True if cmap is not None and cmap.lower() == 'hsv' else False
            is_lab = True if cmap is not None and cmap.lower() == 'lab' else False

            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            if not self.is_color_image:
                image = self.image
                clahe = cv2.createCLAHE(clipLimit=clip_value, tileGridSize=(tile_grid_size, tile_grid_size))
                image = clahe.apply(image)
            else:
                image = self.image.copy()

                if is_hsv:
                    if channel is not None:
                        raise CustomException("CLAHE transformation can be applied only on the Value channel for a HSV"
                                              " type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

                elif is_lab:
                    if channel is not None:
                        raise CustomException("CLAHE transformation can be applied only of the Lightness channel for a"
                                              " LAB type image. Remove the channel parameter")

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

                if channel is None:
                    if is_hsv:
                        clahe = cv2.createCLAHE(clipLimit=clip_value, tileGridSize=(tile_grid_size, tile_grid_size))
                        image[:, :, 2] = np.clip(clahe.apply(image[:, :, 2]), 0, 255)

                    elif is_lab:
                        clahe = cv2.createCLAHE(clipLimit=clip_value, tileGridSize=(tile_grid_size, tile_grid_size))
                        image[:, :, 0] = np.clip(clahe.apply(image[:, :, 0]), 0, 255)

                    else:
                        clahe = cv2.createCLAHE(clipLimit=clip_value, tileGridSize=(tile_grid_size, tile_grid_size))
                        image[:, :, 0] = clahe.apply(image[:, :, 0])
                        image[:, :, 1] = clahe.apply(image[:, :, 1])
                        image[:, :, 2] = clahe.apply(image[:, :, 2])
                        image = image

                else:
                    # If the channel validation passes, then apply the transformation on the specified planes
                    if validate_channel_param(channel=channel):
                        for x in channel:
                            clahe = cv2.createCLAHE(clipLimit=clip_value,
                                                    tileGridSize=(tile_grid_size, tile_grid_size))
                            image[:, :, x] = np.clip(clahe.apply(image[:, :, x]), 0, 255)

                if is_hsv:
                    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
                if is_lab:
                    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

                image = image.astype(np.uint8)

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Clahe Histogram')

            return image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the CLAHE transformation on "
                            f"the given image - {ex}")
