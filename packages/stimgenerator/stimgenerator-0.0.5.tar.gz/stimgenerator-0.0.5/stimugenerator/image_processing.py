import numpy as np
import cv2 as cv
from scipy.fftpack import fft2, fftshift

def get_rms_contrast(img):
    # std of the pixel intensity in an image
    return np.std(img)

def get_sobel_spatial_contrast(img):
    # Compute the gradient of the image using Sobel operators
    dx = cv.Sobel(img, cv.CV_64F, 1, 0)
    dy = cv.Sobel(img, cv.CV_64F, 0, 1)
    # Calculate the magnitude of the gradient
    mag = np.sqrt(dx**2 + dy**2)

    # Calculate the mean and standard deviation of the gradient magnitude
    mean_mag = np.mean(mag)
    std_mag = np.std(mag)

    # Calculate the spatial contrast as the standard deviation divided by the mean
    spatial_contrast = std_mag / mean_mag
    # print(spatial_contrast.shape)
    return spatial_contrast

def get_np_spatial_contrast(image):
    # Calculate the gradient of the image
    gradient = np.gradient(image)

    # Calculate the magnitude of the gradient
    magnitude = np.sqrt(gradient[0]**2 + gradient[1]**2)

    # Calculate the standard deviation of the magnitude
    std_dev = np.std(magnitude)

    # Calculate the mean of the image
    mean = np.mean(image)

    # Calculate the spatial contrast
    contrast = std_dev / mean

    return contrast

def get_laplacian_spatial_contrast(img):

    # Calculate the gradient of the image using the Laplacian filter
    laplacian = cv.Laplacian(img, cv.CV_64F)

    # Calculate the standard deviation of the gradient
    gradient_std = np.std(laplacian)

    # Calculate the mean of the image
    img_mean = np.mean(img)

    # Calculate the spatial contrast as the gradient standard deviation divided by the image mean
    spatial_contrast = gradient_std / img_mean

    return spatial_contrast

def get_spatial_frequency_spectrum(img):
    height = img.shape[0];width = img.shape[1]

    # code source: ChatGPT
    # Compute the 2D Fourier transform
    f = fftshift(fft2(img))

    # Calculate the spatial frequency spectrum
    freq_spectrum = np.abs(f)

    # Calculate the maximum spatial frequency
    max_freq = np.sqrt((height/2)**2 + (width/2)**2)

    # Convert the frequency spectrum to cycles per pixel
    freq_spectrum /= max_freq
    
    # print(freq_spectrum.shape)
    return freq_spectrum