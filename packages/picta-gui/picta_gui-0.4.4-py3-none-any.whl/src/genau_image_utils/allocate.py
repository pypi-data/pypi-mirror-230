# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 2022

Allocates images into training, validation, testing

@author: Robert E. Reinke
@copyright 2022, IIT Corp.
"""
import os
import pathlib
import tensorflow as tf
import random
import shutil


def _copy_file_to_directory(origPathString, newDir):
    origPath = pathlib.Path(origPathString)
    imageFilename = origPath.parts[-1]
    shutil.copy(origPathString, os.path.join(newDir,imageFilename))


def allocate_images(root_dir, image_sub_dir, seg_sub_dir, train_pct, val_pct,
                         train_sub_dir, val_sub_dir, test_sub_dir):
    """ Allocates the images into training, validation and testing by copying
    the files to sub-directories using a uniform distribution with given
    pcercentages

    Inputs
    ----------
        root_dir (string) :  Directory with image subdirectories
        image_sub_dir (string) : Subdirectory of root_dir with training jpeg images
        seg_sub_dir (string) :  Subdirectory of root_dir with segmentation png images
        train_pct (real in [0,1]):  Percent of images allocated to training
        val_pct (real in [0, 1]):  Percent of images allocated to validation.
        train_sub_dir (string):  Subdirectory of root_dir for training images
        val_sub_dir (string) :  Subdirectory of root_dir for validation images
        test_sub_dir (string) :  Subdirectory of root for test images

    Returns
    -------
        True on success, false on failure

    """

    if not os.path.isdir(root_dir):
        print(root_dir, ' does not exist or is not a directory')
        return False

    image_dir = os.path.join(root_dir, image_sub_dir)
    if not os.path.isdir(image_dir):
        print(image_dir, ' does not exist or is not a directory')
        return False

    segmentation_dir = os.path.join(root_dir, seg_sub_dir)
    if not os.path.isdir(segmentation_dir):
        print(segmentation_dir, ' does not exist or is not a directory')
        return False

    training_dir = os.path.join(root_dir, train_sub_dir)
    if not os.path.isdir(training_dir):
        print(training_dir, ' does not exist or is not a directory')
        return False
    training_images_dir = os.path.join(training_dir, 'images')
    if not os.path.exists(training_images_dir):
        os.mkdir(training_images_dir)
    training_segmentation_dir = os.path.join(training_dir, 'segmentation')
    if not os.path.exists(training_segmentation_dir):
        os.mkdir(training_segmentation_dir)

    validation_dir = os.path.join(root_dir, val_sub_dir)
    if not os.path.isdir(validation_dir):
        print(validation_dir, ' does not exist or is not a directory')
        return False
    validation_images_dir = os.path.join(validation_dir ,'images')
    if not os.path.exists(validation_images_dir):
        os.mkdir(validation_images_dir)
    validation_segmentation_dir = os.path.join(validation_dir, 'segmentation')
    if not os.path.exists(validation_segmentation_dir):
        os.mkdir(validation_segmentation_dir)

    test_dir = os.path.join(root_dir, test_sub_dir)
    if not os.path.isdir(test_dir):
        print(test_dir, ' does not exist or is not a directory')
        return False
    test_image_dir = os.path.join(test_dir, 'images')
    if not os.path.exists(test_image_dir):
        os.mkdir(test_image_dir)
    test_segmentation_dir = os.path.join(test_dir, 'segmentation')
    if not os.path.exists(test_segmentation_dir):
        os.mkdir(test_segmentation_dir)

    if train_pct < 0 or train_pct > 1:
        print('trainpct must be between 0 and 1')
        return False

    if val_pct < 0 or val_pct > 1:
        print('valPct must be between 0 and 1')
        return False

    if train_pct + val_pct > 1:
        print('trainPct + valPct must be <= 1')
        return False

    testPct = 1.0 - (train_pct + val_pct)

    random.seed()
    image_dir = pathlib.Path(image_dir)
    pairs = []
    # build the lists of images and segementation images, confirming
    # that every image has a matching segmentation image
    for imagePath in image_dir.iterdir():
        imageFilename = imagePath.parts[-1]
        baseFileName, extension = os.path.splitext(imageFilename)
        if extension == '.jpg':
            segFilename = baseFileName + '.png'
            segPath = os.path.join(segmentation_dir, segFilename)
            if not os.path.exists(segPath):
                print('Missing segmentation file ', segPath)
                return False
            pairs.append([os.path.join(image_dir.resolve(), imageFilename),
                         segPath])

    distr = [train_pct, val_pct, testPct]
    print('Ready to write ' + str(len(pairs)) + ' pairs with distribution '
          + str(distr))

    for pair in pairs:
        selection = random.random()
        if (selection <= train_pct):
            _copy_file_to_directory(pair[0], training_images_dir)
            _copy_file_to_directory(pair[1], training_segmentation_dir)
        else:
            if (selection <= train_pct + val_pct):
                _copy_file_to_directory(pair[0], validation_images_dir)
                _copy_file_to_directory(pair[1], validation_segmentation_dir)
            else:
                _copy_file_to_directory(pair[0], test_image_dir)
                _copy_file_to_directory(pair[1], test_segmentation_dir)

    return True
