# -*- coding: utf-8 -*-
"""
Created on Mon May 08 2023

Routines for displaying image files

@author: Robert E. Reinke
@copyright 2023, IIT Corp.
"""

import tensorflow as tf
import random
import os
import matplotlib.pyplot as plt
import pathlib
from . import filechecks
from . import imagetransforms

def random_jpg_from_dir(dirPath):
    """ Randomly picks, reads and returns a jpg file from the given directory
    
    Inputs:
        dirPath (string): directory containing jpg files
    Returns:
        An image as produced by tf.decode_jpeg
    """
    subset = [fn for fn in os.listdir(dirPath) if filechecks.is_jpeg_filename(fn)]
    if len(subset) == 0:
        print('No JPG files found')
        return None
    else:
        filename = random.choice(subset)
        return tf.image.decode_jpeg(tf.io.read_file(os.path.join(dirPath,filename)))
    
def image_compare(orig, adjusted, figure_size=(15, 15)):
    """Displays two images side-by-side

    Inputs:
        orig (image): the original image
        adjusted (image): the adjusted image
        figure_size (2-tuple): image size (width, height) for display
    """
    plt.figure(figsize=figure_size)
    plt.subplot(1, 2, 1)
    plt.title('Original')
    plt.imshow(orig)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.title('Adjusted')
    plt.imshow(adjusted)
    plt.axis('off')
    plt.show()
    
def display_hue_transform(image_dir_name, max_delta):
    """Applies random hue to a random image and shows the image next to the adjusted image

    Inputs:
        image_dir_name (string) : path to a directory with jpg images
        max_delta (real): hue delta will be randomly selected in [-max_delta, max_delta]
    """
    image = random_jpg_from_dir(image_dir_name)
    augment = imagetransforms.apply_random_hue(image, max_delta)
    image_compare(image, augment)

def display_saturation_transform(image_dir_name, lower, upper):
    """Applies random saturation to a random image and shows the image next to the adjusted image

    Inputs:
        image_dir_name (string) : path to a directory with jpg images
        lower (real) : lower bound for the random saturation factor
        upper (real) : upper bound for the random saturation factor    
    """
    image = random_jpg_from_dir(image_dir_name)
    augment = imagetransforms.apply_random_saturation(image, lower, upper)
    image_compare(image, augment)
    
def display_brightness_transform(image_dir_name, max_delta):
    """Applies random brightness to a random image and shows the image next to the adjusted image

    Inputs:
        image_dir_name (string) : path to a directory with jpg images
        max_delta (real): brightness delta will be randomly selected in [-max_delta, max_delta]
    """
    image = random_jpg_from_dir(image_dir_name)
    augment = imagetransforms.apply_random_brightness(image, max_delta)
    image_compare(image, augment)
    
def display_contrast_transform(image_dir_name, lower, upper):
    """Applies random constrast to a random image and shows the image next to the adjusted image

    Inputs:
        image_dir_name (string) : path to a directory with jpg images
        lower (real) : lower bound for the random contrast factor
        upper (real) : upper bound for the random constrast factor    
    """
    image = random_jpg_from_dir(image_dir_name)
    augment = imagetransforms.apply_random_contrast(image, lower, upper)
    image_compare(image, augment)
    
def display_triple(display_list, figure_size=(15, 15)):
    """ Displays a triple of image, true mask, predicted mask

    Inputs:
        display_list (3-tuple): tensorflow image tensors to show
        figure_sizes (2-tuple of integer) : figure dimensions
    """
    plt.figure(figsize=figure_size)
    title = ['Input Image', 'True Mask', 'Predicted Mask']

    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i+1)
        plt.title(title[i])
        plt.imshow(tf.keras.utils.array_to_img(display_list[i]))
        plt.axis('off')
    plt.show()
    
def write_model_prediction_as_png(model, input_image_filename, output_filename):
    """_summary_

    Writes the model's prediction as a grayscale png
    Args:
        model (keras model): The trained model
        input_image_filename (string): The path to the input JPG image
        outpath_filename (string): path to write the output to
    """
    image = tf.image.decode_jpeg(tf.io.read_file(input_image_filename))
    image = tf.cast(image, tf.float32)/255.0
    modeled = tf.math.argmax(model.predict(image[tf.newaxis, ...]),axis=-1)
    modeled = modeled[...,tf.newaxis]
    modeled = modeled[0]
    modeled = modeled * 255
    tf.io.write_file(output_filename, tf.image.encode_png(tf.cast(modeled, tf.uint8)))
    print("Wrote " + output_filename)
    
       
def display_model_results(model, image_dir_name, segments_dir_name,
                        image_size=[128, 128]):
    """
    Displays image, correct mask, predicted mask from a model from a directory until all files are displayed or the user enters 'q'

    Inputs:
        model (Keras model) : trained model.
        image_dir_name (string) : the path to the directory containing images to show.
        segments_dir_name (string) : the path to the directory containing segmented/labelled images.
        image_size (2-tuple of int) : width, height of image

    Returns:
        (bool) : True on success, False on failure.

    """

    if not filechecks.exists_and_is_dir(image_dir_name):
        print(image_dir_name, ' does not exist or is not a directory')
        return False
    if not filechecks.exists_and_is_dir(segments_dir_name):
        print(segments_dir_name, ' does not exist or is not a directory')
        return False
    image_dir_path = pathlib.Path(image_dir_name)
    pairs = []
    # build the lists of images and segementation images, confirming
    # that every image has a matching segmentation image
    for imagePath in image_dir_path.iterdir():
        imageFilename = imagePath.parts[-1]
        baseFileName, extension = os.path.splitext(imageFilename)
        if extension == '.jpg':
            segFilename = baseFileName + '.png'
            segPath = os.path.join(segments_dir_name, segFilename)
            if not os.path.exists(segPath):
                print('Missing segmentation file ', segPath)
                return False
            pairs.append([os.path.join(image_dir_path.resolve(), imageFilename),
                         segPath])

    for pair in pairs:
        image = tf.image.decode_jpeg(tf.io.read_file(pair[0]))
        image = tf.reshape(image, [image_size[0], image_size[1], 3])
        image = tf.cast(image, tf.float32)/255.0
        seg = tf.image.decode_png(tf.io.read_file(pair[1]))
        seg = tf.reshape(seg[:, :, 0], [image_size[0], image_size[1], 1])
        seg = tf.cast(seg, tf.float32)/255.0
        modeled = tf.math.argmax(model.predict(image[tf.newaxis, ...]),axis=-1)
        modeled = modeled[...,tf.newaxis]
        modeled = modeled[0]
        display_triple((image, seg, modeled))
        print("File " + pair[0] + "\n")
        val = input('Type q<cr> to quit, <cr> to continue')
        if (val == 'q'):
            return True

    return True