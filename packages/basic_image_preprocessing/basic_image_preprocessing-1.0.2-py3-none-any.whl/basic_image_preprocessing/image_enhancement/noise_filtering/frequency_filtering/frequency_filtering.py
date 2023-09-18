import numpy as np
from warnings import filterwarnings
import image_frequency_analysis as ifa
from basic_image_preprocessing.exception.custom_exception import CustomException
from basic_image_preprocessing.utility.utlity import validate_param_type, validate_wavelet_type

filterwarnings('ignore')


class FrequencyNoiseFiltering:
    def __init__(self, image_path: str):
        try:
            self.image_path = image_path

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.image_path}")

        except CustomException as ex:
            raise ex

    def fourier_transform(self, filter_radius: int, high_pass_filter: bool = False,
                          low_pass_filter: bool = False) -> np.ndarray:
        """
        Definition to perform the Fourier Transform algorithm on the image.
        In this method even though a color image path is mentioned, it will
        be read as a gray scale image, as the fourier transform can be done
        only on a gray scale image
        :param filter_radius: This defines the amount of the filtering to be done
        :param high_pass_filter: Boolean flag to enable the high frequency to be allowed
        :param low_pass_filter: Boolean flag to enable the low frequency to be allowed
        :return: numpy.ndarray -> image post applying the required fourier transform on the given image
        """
        try:
            validate_param_type('filter_radius', filter_radius, type(filter_radius), int)
            validate_param_type('high_pass_filter', high_pass_filter, type(high_pass_filter), bool)
            validate_param_type('low_pass_filter', low_pass_filter, type(low_pass_filter), bool)

            obj = ifa.FrequencyAnalysis(self.image_path, filter_radius, high_pass_filter,
                                        low_pass_filter)
            processed_image = obj.perform_image_frequency_analysis()

            return processed_image
        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the Fourier Transformation on "
                            f"the given image - {ex}")
