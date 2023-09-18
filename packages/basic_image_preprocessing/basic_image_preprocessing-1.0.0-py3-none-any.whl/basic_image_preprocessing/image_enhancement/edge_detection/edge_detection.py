import numpy
import numpy as np
import cv2
from warnings import filterwarnings
from basic_image_preprocessing.exception.custom_exception import CustomException
from basic_image_preprocessing.utility.utlity import load_image, plot_graph, validate_param_type, \
    create_kernel_mask, validate_param_list_value

filterwarnings('ignore')


class ImageEdgeDetection:
    def __init__(self, image_path: str, cmap: str):
        try:
            self.image_path = image_path
            self.is_color_image = False

            self.image, self.is_color_image = load_image(self.image_path, cmap)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.image_path}")

        except CustomException as ex:
            raise ex

    def laplacian(self, kernel: int = 3, smoothness: bool = True, plot_output: bool = True):
        """
        This definition will apply the laplacian edge detection  on the given image
        with the value and method given in the parameters

        Input:

            kernel: Mask shape for smoothening the image
                        Accepted value -> must be an odd number
            smoothness: bool value whether the image has to be removed by noise before edge detection or not
                        Accepted value -> True or False
                        Default value -> True
            plot_output: This is a boolean value which will instruct the program whether to display the
                            images post pre-processing or not. Will throw value error if value other than the accepted
                            value passed

                            Accepted values - True , False

        Output:
                numpy.ndarray -> image post applying the laplacian edge detection on the given image
        """
        try:
            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            validate_param_type('kernel', kernel, type(kernel), int)

            validate_param_type('smoothness', smoothness, type(smoothness), bool)

            image = self.image
            if self.is_color_image:
                image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

            if smoothness:
                smooth = cv2.GaussianBlur(image, (kernel, kernel), 0, borderType=cv2.BORDER_REFLECT)
                laplacian = cv2.Laplacian(smooth, cv2.CV_64F)
                image = np.uint16(np.absolute(laplacian))
            else:
                laplacian = cv2.Laplacian(image, cv2.CV_64F)
                image = np.uint16(np.absolute(laplacian))

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Laplacian Edge detection', is_edge_detection=True)

            return image
        except TypeError as ex:
            raise TypeError(ex)

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the laplacian Edge detection on the given image "
                            f"- {ex}")

    def canny_edge_detection(self, lower_threshold: int, upper_threshold: int, aperture_size: int = None,
                             l2gradient: bool = None, plot_output: bool = True):
        """
        This definition will apply the Canny edge detection method to identify the
        edges in the image with the specified parameter values.

        Input:
            lower_threshold -> Lower threshold value in Hysteresis Thresholding. Required parameter

            upper_threshold -> Upper threshold value in Hysteresis Thresholding. Required parameter

            aperture_size -> Aperture size of the Sobel filter. The value should be an odd integer between 3 and 7.
                If the value is out of range, an error is raised for the cv2 package.

            l2gradient -> Boolean parameter used for more precision in calculating Edge Gradient.
                Accepted values - True , False

            plot_output -> This is a boolean value which will instruct the program whether to display the
                        images post pre-processing or not. Will throw value error if value other than the accepted value
                        passed
                Accepted values - True , False

        Output:
            numpy.ndarray -> image post applying the canny edge detection on the given image
        """
        try:
            if type(plot_output) is not bool:
                raise ValueError(
                    f"plot_output parameter takes only True or False boolean value. No other values allowed")

            validate_param_type('aperture_size', aperture_size, type(aperture_size), int)

            validate_param_type('L2gradient', l2gradient, type(l2gradient), bool)

            if l2gradient is not None and aperture_size is not None:
                edge_detail = cv2.Canny(self.image, lower_threshold, upper_threshold, apertureSize=aperture_size,
                                        L2gradient=l2gradient)

            elif aperture_size is not None:
                edge_detail = cv2.Canny(self.image, lower_threshold, upper_threshold, apertureSize=aperture_size)

            elif l2gradient is not None:
                edge_detail = cv2.Canny(self.image, lower_threshold, upper_threshold, L2gradient=l2gradient)

            else:
                edge_detail = cv2.Canny(self.image, lower_threshold, upper_threshold)

            if plot_output:
                plot_graph(self.image, edge_detail, self.is_color_image, f'Canny Edge Detection',
                           is_edge_detection=True)

            return edge_detail

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the Canny Edge detection Algorithm on "
                            f"the given image - {ex}")

    def edge_filtering(self, kernel_size: int, filter_type: str, custom_filter_array: numpy.ndarray = None,
                       plot_output: bool = True):
        """
        This definition will apply either the sharpening filter or the edge detection filter when the
        custom_kernel_array is not passed

        :param kernel_size: Size of the filter array to be created. Should be an odd positive integer

        :param filter_type: The filter_type used to define what type of filtering mask to be applied on the image
                            Accepted Value -> 'sharpen', 'edge_detection'
                            Uses the 'custom' value when the custom_filter_array is passed.

        :param custom_filter_array: A custom numpy square matrix array, whose row and column values should be equal to
                                    the kernel size passed

        :param plot_output: This is a boolean value which will instruct the program whether to display the
                            images post pre-processing or not. Will throw value error if value other than the accepted
                            value passed.
                                Accepted values - True , False
        :return: numpy.ndarray -> image post applying the required filtering on the given image
        """
        try:
            validate_param_list_value(filter_type, ['sharpen', 'edge_detection'], 'Edge Filtering', 'filter_type')

            if custom_filter_array is not None:
                kernel = create_kernel_mask(kernel_size, 'custom', custom_filter_array)

            else:
                kernel = create_kernel_mask(kernel_size, filter_type)

            image = self.image

            if filter_type == 'edge_detection':
                image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

            processed_image = cv2.filter2D(image, -1, kernel)

            if plot_output:
                plot_graph(self.image, processed_image, self.is_color_image, f'{filter_type}', is_edge_detection=True)

            return processed_image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the sharpening filter mask on "
                            f"the given image - {ex}")
