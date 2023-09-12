# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 14:50:29 2023

Utility routines for checking the absence or presence of image files

@author: Robert E. Reinke
@copyright 2023, IIT Corp.
"""

import os
import pathlib
import tensorflow as tf

def exists_and_is_dir(path):
    """ Determining if the given path exists and is a directory.

    Inputs:
        path (string): Full or relative path to a file/directory

    Returns:
        True if the path is an existing directory false otherwise
    """
    if not os.path.exists(path):
        return False
    else:
        return os.path.isdir(path)
    
def is_jpeg_filename(filename):
    """Determine if the filename has a jpg or jpeg extension

    Inputs:
        filename (string): full or partial or relative file name of the file
    Returns:
        (boolean) : True if the file extension is 'jpg' or 'jpeg' (case-insensitive), False otherwise
    """
    if len(filename) < 4:
        return False
    ext = filename[-4:].upper()
    return ext in ('.JPG', 'JPEG')


def is_png_filename(filename):
    """Determine if the filename has a png extension

    Inputs:
        filename (string): full or partial or relative file name of the file
    Returns:
        (boolean) : True if the file extension is 'png' (case-insensitive), False otherwise
    """
    if len(filename) < 4:
        return False
    ext = filename[-4:].upper()
    return (ext == '.PNG')

def check_image_segmentation_match(image_dir_name, seg_dir_name,
                                seg_is_gif=False):
    """ Determines if every image has a matching segmentation, and vice versa.
    Prints the names of missing image or segmentation files.

    Inputs:
        seg_dir_name (string): Path to directory containing segmentation images (gif or png)
        seg_is_gif (boolean) : If True, looks for GIF segmentation files, otherwise looks for PNG

    Returns:
        (int) : Number of missing files

    """
    if (not exists_and_is_dir(image_dir_name)):
        print(image_dir_name + ' is not an existing directory')
        return False

    if (not exists_and_is_dir(seg_dir_name)):
        print(seg_dir_name + ' is not an existing directorty')
        return False

    result = 0

    # build the lists of images and segementation images, confirming
    # that every image has a matching segmentation image
    imageDir = pathlib.Path(image_dir_name)
    for imagePath in imageDir.iterdir():
        imageFilename = imagePath.parts[-1]
        baseFileName, extension = os.path.splitext(imageFilename)
        if extension == '.JPG':
            if seg_is_gif:
                segFilename = baseFileName + '.GIF'
            else:
                segFilename = baseFileName + '.PNG'
            segPath = os.path.join(seg_dir_name, segFilename)
            if not os.path.exists(segPath):
                print('Missing segmentation file ', segPath)
                result = result + 1

    # now do the converse
    segmentationDir = pathlib.Path(seg_dir_name)
    for segPath in segmentationDir.iterdir():
        segFileName = segPath.parts[-1]
        baseFileName, extension = os.path.splitext(segFileName)
        if (extension == '.GIF' and seg_is_gif) or \
           (extension == '.png' and (not seg_is_gif)):
            imageFilename = baseFileName + '.JPG'
            imagePath = os.path.join(image_dir_name, imageFilename)
            if not os.path.exists(imagePath):
                print('Missing image file ', imagePath)
                result = result + 1
    return result

def rgb_to_int(red, green, blue):
    """Converts RGB values to a single integer

    Inputs:
        red (byte): from 0 to 255
        green (byte): from 0 to 255
        blue (byte): from 0 to 255

    Returns:
        The value as a single integer
    """
    return (red << 16) + (green << 8) + blue

def rgb_from_int(value):
    """Converts an integer RGB value to its components

    Inputs:
        value (int): a pixel value with RGB encoded in its rightmost 24 bits

    Returns:
        (3 bytes) : red, green, blue 
    """
    red = (value & 0xFF0000) >> 16
    green = (value & 0x00FF00) >> 8
    blue = value & 0x0000FF
    return red, green, blue

def manhattan_distance_rgb(value, target):
    """Manhattan distance between two RGB values.

    Inputs:
        value (3-tuple of integers): The RGB value from an image
        target (3-tuple of integers): The 'target' RGB value
    Returns:
        (int) : Manhattan distance
    """
    dist = abs(value[0] - target[0])
    dist += abs(value[1] - target[1])
    dist += abs(value[2] - target[2])
    return dist

def on_target_rgb(value, targets):
    """Determines if the RGB value matches one of the targets

    Inputs:
        value (3-tuple of integers): The  RGB value from an image
        targets (tuple of 3-tuple of integers): Target values
    Returns:
        (bool) : True if the value matches one of the targets, false otherwise
    """
    for target in targets:
        if (manhattan_distance_rgb(value, target) == 0):
            return True
    return False

def nearby_rgb(value, targets,nearby_distance=192):
    """Determines if the value RGB is near one of the target RGB values
        For our purposes, 'nearby' means 'Manhattan distance < nearby_distance'.  
        I chose 192 as the default because a) using 50 (my initial guess)
        produced too many 'not nearby' values and b) 192 = 64 x 3
    
    Inputs:
        value (3-tuple of integers): The RGB value from an image
        targets (tuple of 3-tuple of integers): Target values
    Returns:
        Nearby target RGB or None
    """
    for target in targets:
        if (manhattan_distance_rgb(value, target) < nearby_distance):
            return target
    return None

def repair_using_manhattan_close(rgbTuple, targets, locations, imageArray):
    """Replaces RBG values with target values that are 'close' to the given value by
    the Manhattan measure.  Can be used as a repair_func in repair_using_function

    Inputs:
        rgbTuple (3-tuple of ints): an RBG tuple that isn't one of the
            expected ones
        targets (tuple of 3-tuples): the expected RBG tuples
        locations (tuple of 2-tuples): x, y locations where rgbTuple is found
        imageArray (np array [512, 512, 3]) : image as a numpy array

    Returns:
        The total number of pixels replaced
    """
    result = 0
    replacement = nearby_rgb(rgbTuple, targets)
    if replacement is not None:
        for location in locations:
            x = location[0]
            y = location[1]
            imageArray[x, y, 0] = replacement[0]
            imageArray[x, y, 1] = replacement[1]
            imageArray[x, y, 2] = replacement[2]
        result += len(locations)
    return result

def estimated_target_rgb(imageArray, x, y, targets):
    """Estimates the target RGB we should use at x, y based on neighboring
    pixels.
    NOTE: We assume that repair_using_manhattan_close has already been run so
    that the likelihood of there being a 'correct' nearby pixel is high.
    Inputs:
        imageArray ([512, 512, 3] numpy array) : the image
        x (integer): first axis value
        y (integer): second axis value
        targets (tuple of 3-tuple of integers): Target values as rgb
    Returns:
        (3-tuple of integer) : The RGB target value that is most common among nearby pixels to x,y
    """
    targetDict = dict()
    for target in targets:
        targetDict[rgb_to_int(target[0], target[1], target[2])] = 0

    for dx in range(-8, 9):
        for dy in range(-8, 9):
            if ((dx != 0) or (dy != 0)) and (x + dx >= 0) and (x + dx <= 511) and (y + dy >= 0) and (y + dy <= 511):
                nx = x + dx
                ny = y + dy
                rgb = (imageArray[nx, ny, 0],
                       imageArray[nx, ny, 1], imageArray[nx, ny, 2])
                if rgb in targets:
                    val = rgb_to_int(rgb[0], rgb[1], rgb[2])
                    count = targetDict[val]
                    targetDict[val] = count + 1
    highestCount = 0
    highestTargetVal = None
    for key in targetDict.keys():
        if targetDict[key] > highestCount:
            highestCount = targetDict[key]
            highestTargetVal = key
    if highestTargetVal is None:
        return None
    else:
        red, green, blue = rgb_from_int(highestTargetVal)
        return (red, green, blue)
    

def generate_unexpected_values_dictionary(imageArray, targets, image_size):
    """Generates a dictionary of unexpected pixel values in the given image
    array to their locations

    Inputs:
        imageArray (numpy array of [512, 512, 3]): The image as a numpy array
        targets (tuple or list of integers): Expected pixel values as integers
        image_size (2-tuple of integer) : image size in pixels

    Returns:
        A dictionary of unexpected values where the value is a list of (x,y)
        locations
    """
    result = dict()
    for x in range(image_size[0]):
        for y in range(image_size[1]):
            red = imageArray[x, y, 0]
            green = imageArray[x, y, 1]
            blue = imageArray[x, y, 2]
            rgb = rgb_to_int(red, green, blue)
            if not (rgb in targets):
                value = result.get(rgb, None)
                # when viewed in GIMP, the first coordinate is actually the
                # vertical direction
                if value is None:
                    value = [(x, y), ]
                else:
                    value += [(x, y), ]
                result[rgb] = value
    return result

def repair_using_surrounding_pixels(rgbTuple, targets, locations, imageArray):
    """Replaces RBG values by finding the most common 'correct' value in
    nearby pixels.  Can be used as a repair_func in repair_using_function

    Args:
        rgbTuple (3-tuple of ints): an RBG tuple that isn't one of the
                expected ones
        targets (tuple of 3-tuples): the expected RBG tuples
        locations (tuple of 2-tuples): locations where rgbTuple is found
        imageArray (np array [*, *, 3]) : image as a numpy array

    Returns:
        The total number of pixels replaced
    """
    result = 0
    for location in locations:
        x = location[0]
        y = location[1]
        replacement = estimated_target_rgb(imageArray, x, y, targets)
        if (replacement is not None):
            imageArray[x, y, 0] = replacement[0]
            imageArray[x, y, 1] = replacement[1]
            imageArray[x, y, 2] = replacement[2]
            result += 1
        else:
            print('        Unable to find replacment for bad pixel at ' + str(x) + ',' + str(y))
    return result

def repair_using_function(seg_dir, expected_rgbs, image_size, repair_func):
    """Repairs R, G, B values in the segmentation files directory using a repair function
    
     Calls repair_func to repair non-matching pixels.

    Args:
        seg_dir (string): Directory containing png files to repair
        expected_rgbs (tuple of 3-tuples) : valid RGB values for segmentation
        image_size (2-tuple of int) : image size in pixels
        repair_func (function) : routine to call to repair bad values.  The function must take:
            a rgb 3-tuple of a bad value
            the expected RGBs list
            a list of (x,y) locations where the bad value occurs
            the image as a [512, 512, 3] numpy array
        and should return the number of pixel values replaced

    Returns:
        List of file paths that were overwritten, or None
    """
    if not exists_and_is_dir(seg_dir):
        print(seg_dir + ' does not exist or is not a directory')
        return None
    
    files = [fn for fn in os.listdir(seg_dir) if is_png_filename(fn)]
    if len(files) == 0:
        print('No PNG files found')
        return None

    expectedValues = []
    for rgb in expected_rgbs:
        expectedValues.append(rgb_to_int(rgb[0], rgb[1], rgb[2]))
    
    changedFiles = []
    for filename in files:
        filepath = os.path.join(seg_dir, filename)
        imageTensor = tf.image.decode_png(tf.io.read_file(filepath))

        # make sure the image is what we expect
        shapeArr = tf.shape(imageTensor).numpy()
        skip = False
        if (shapeArr.shape != (3, )):
            print('file ' + filepath + ' is not the correct shape, skipping')
            skip = True
        if (not skip) and ((shapeArr[0] != image_size[0]) or (shapeArr[1] != image_size[1]) or (shapeArr[2] != 3)):
            print('file ' + filepath + ' is not the correct shape, skipping')
            skip = True

        if not skip:
            imageArray = imageTensor.numpy()
            print('Analyzing ' + filepath)
            pixelDict = generate_unexpected_values_dictionary(imageArray, expectedValues, image_size)
            bad = len(pixelDict.keys())
            if bad > 0:
                print('    ' + str(bad) + ' pixel values')
                replaceCount = 0
                for key in pixelDict.keys():
                    red, green, blue = rgb_from_int(key)
                    print('         considering ' + str(len(pixelDict[key])) + ' instances of (' + str(
                        red) + ', ' + str(green) + ', ' + str(blue) + ')')
                    replaceCount += repair_func((red, green, blue),expected_rgbs, pixelDict[key],imageArray)
                print('    ' + str(replaceCount) + ' pixels replaced')
                if replaceCount > 0:
                    imageTensor = tf.convert_to_tensor(imageArray)
                    tf.io.write_file(
                        filepath, tf.image.encode_png(imageTensor))
                    changedFiles += [filepath, ]
                    print('    file updated')
            else:
                print('     OK!')

    return changedFiles

def qc_segmentation_file(filename, target_rgbs, image_size):
    """ Does quality check on the file to determine if there are bad pixels for segmentation and prints errors to standard output

    Inputs:
        filename (string) : Path to the file to be analyzed
        target_rgbs (tuple of 3-tuples) : target RGB valuse for segmentation
        image_size (2-tuple of integer) : image size in pixels
    Returns:
        True if there are no issues, false otherwise.

    """
    imageTensor = tf.image.decode_png(tf.io.read_file(filename))
    expectedValues = []
    for rgb in target_rgbs:
        expectedValues.append(rgb_to_int(rgb[0], rgb[1], rgb[2]))
    
    # make sure the image is what we expect
    shapeArr = tf.shape(imageTensor).numpy()
    if (shapeArr.shape != (3, )):
        print('file ' + filename + ' does not have 3 dimensions')
        return False
    if ((shapeArr[0] != image_size[0]) or (shapeArr[1] != image_size[1]) or (shapeArr[2] != 3)):
        print('file ' + filename + ' has shape ' + str(shapeArr) +
              ' not (' + image_size + ',3)')
        return False

    imageArray = imageTensor.numpy()
    pixelDict = generate_unexpected_values_dictionary(imageArray, expectedValues, image_size)
    bad = len(pixelDict.keys())
    if bad > 0:
        print('file ' + filename + ' has ' + str(bad) + ' bad pixel values')
        for key in pixelDict.keys():
            red, green, blue = rgb_from_int(key)
            print('         ' + str(len(pixelDict[key])) + ' instances of ('
                  + str(red) + ', ' + str(green) + ', ' + str(blue) + ')')
            print('               Locations:' + str(pixelDict[key]))
        return False
    else:
        print('file ' + filename + ' OK!')
        return True
    
def qc_segmentation_directory(seg_dir_name, target_rgbs, image_size = (512, 512)):
    """ Runs qc_segmentation_file on each PNG file in seg_dir_name 
    
    Inputs:
        seg_dir_name (string) : directory path to be analyzed
        target_rgbs (tuple of 3-tuples) : valid segmentation RGB values
        image_size (2-tuple of integer) : image size in pixels
    Returns:
        (bool)  True if there are no issues, false otherwise.    
    """
    if not exists_and_is_dir(seg_dir_name):
        print(seg_dir_name + ' does not exist or is not a directory')
        return False
    inputPath = pathlib.Path(seg_dir_name)
    result = True
    for imagePath in inputPath.iterdir():
        imageFilename = imagePath.parts[-1]
        if is_png_filename(imageFilename):
            if not qc_segmentation_file(os.path.join(seg_dir_name, imageFilename),target_rgbs, image_size):
                result = False
    return result