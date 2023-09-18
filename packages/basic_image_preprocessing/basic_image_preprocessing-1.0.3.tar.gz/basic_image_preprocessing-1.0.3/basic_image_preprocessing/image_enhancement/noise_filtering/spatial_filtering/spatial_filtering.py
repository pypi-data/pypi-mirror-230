
import numpy as np
import cv2
from warnings import filterwarnings
from basic_image_preprocessing.exception.custom_exception import CustomException
from basic_image_preprocessing.utility.utlity import load_image, plot_graph, validate_param_type, \
    create_kernel_mask, validate_param_list_value
from typing import Union

filterwarnings('ignore')


class SpatialNoiseFiltering:
    def __init__(self, image_path: str, cmap: str):
        try:
            self.image_path = image_path
            self.is_color_image = False

            self.image, self.is_color_image = load_image(self.image_path, cmap)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.image_path}")

        except CustomException as ex:
            raise ex

    def noise_filtering(self, kernel_size: int, filter_type: str,
                        plot_output: bool = True) -> np.ndarray:
        """
        This definition will apply the noise removal method to identify the
        noises in the image with the specified parameter values.

        Input:
            kernel_size -> This is the kernel mask for performing the noise removal operation. This is the mandatory
            parameter

            filter_type -> This is the type of filtering method applying on the image.
            Accepted values - 'mean','median'

            plot_output -> This is a boolean value which will instruct the program whether to display the
            images post pre-processing or not. Will throw value error if value other than the accepted value
            passed.

            Accepted values - True , False

        Output:
            numpy.ndarray -> image post applying the canny edge detection on the given image
        """

        try:
            validate_param_list_value(filter_type, ['mean', 'median', 'gaussian'], 'Noise Filtering', 'filter_type')

            validate_param_type('kernel_size', kernel_size, type(kernel_size), int)

            kernel = create_kernel_mask(kernel_size, filter_type)

            if filter_type == 'median':
                image = self.image.astype(np.uint8)
                processed_image = cv2.medianBlur(image, kernel_size)

            elif filter_type == 'gaussian':
                image = self.image.astype(np.uint8)
                processed_image = cv2.filter2D(image, -1, kernel)

            else:
                processed_image = cv2.filter2D(self.image, -1, kernel)

            if plot_output:
                plot_graph(self.image, processed_image, self.is_color_image, f'{filter_type}')

            return processed_image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the {filter_type} mask on "
                            f"the given image - {ex}")

    def bilateral_filter(self, diameter: int = 5, sigma_color: Union[int, float] = 50,
                         sigma_space: Union[int, float] = 50, plot_output: bool = True) -> np.ndarray:
        """
        A bilateral filter is a non-linear, edge-preserving, and noise-reducing smoothing filter for images.
        It replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels.

        Input:
            diameter: Diameter of each pixel neighborhood.

            sigma_color: Value of sigma_color  in the color space.
            The greater the value, the colors farther to each other will start to get mixed.

            sigma_space:Value of sigma  in the coordinate space.
            The greater its value, when the pixels are further away it will mix together

            plot_output -> This is a boolean value which will instruct the program whether to display the
                images post pre-processing or not. Will throw value error if value other than the accepted value
                passed.

                Accepted values - True , False
        Output:
            numpy.ndarray -> image post applying the canny edge detection on the given image
        """
        try:
            validate_param_type('diameter', diameter, type(diameter), int)

            image = cv2.bilateralFilter(self.image, diameter, sigma_color, sigma_space)

            if plot_output:
                plot_graph(self.image, image, self.is_color_image, f'Bilateral')

            return image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the Bilateral mask on "
                            f"the given image - {ex}")

    def wiener_filter(self, kernel_size, noise_variance: float = 0.01,
                      plot_output: bool = True) -> np.ndarray:
        """
        In signal processing, the Wiener filter is a filter used to produce an estimate of a desired or target
        random process by linear time-invariant (LTI) filtering of an observed noisy process, assuming known
        stationary signal and noise spectra, and additive noise. The Wiener filter minimizes the mean square
        error between the estimated random process and the desired process.

        Input:
            Kernel_size : Size of the array of the filter Point Spread Function (PSF) of the degradation process

            noise_variance :  Variance of the noise.

            plot_output -> This is a boolean value which will instruct the program whether to display the
                images post pre-processing or not. Will throw value error if value other than the accepted value
                passed.

                Accepted values - True , False
        Output:
            numpy.ndarray -> image post applying the wiener transformation on the given image
        """

        try:
            validate_param_type('noise_variance', noise_variance, type(noise_variance), float)

            # 'mean' is the only filter type that can be used with
            # wiener filtering
            kernel = create_kernel_mask(kernel_size, 'mean')

            image = self.image.copy()

            if self.is_color_image:
                image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

            image_freq = np.fft.fft2(image)

            psf_freq = np.fft.fft2(kernel, s=image.shape)

            # Compute the Wiener filter
            wiener_filter = np.conj(psf_freq) / (np.abs(psf_freq) ** 2 + noise_variance)

            # Apply the Wiener filter to the frequency domain of the image
            filtered_freq = image_freq * wiener_filter

            # Compute the inverse Fourier Transform to obtain the filtered image
            filtered_image = np.fft.ifft2(filtered_freq).real

            if plot_output:
                plot_graph(self.image, filtered_image, self.is_color_image, f'Wiener', is_edge_detection=True)

            return filtered_image

        except ValueError as ex:
            raise ValueError(ex)

        except CustomException as ex:
            raise CustomException(ex)

        except Exception as ex:
            raise Exception(f"An error occurred while trying to apply the Bilateral mask on "
                            f"the given image - {ex}")
