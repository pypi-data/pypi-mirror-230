# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 2023

Routines for transforming image files

@author: Robert E. Reinke
@copyright 2023, IIT Corp.
"""

import os
import pathlib
import cv2
import tensorflow as tf
import numpy as np
import filechecks
from PIL import Image, ImageFilter
from psd_tools import PSDImage
from collections import deque

def write_image_with_suffix(orig_path_name, image, suffix, is_jpeg):
    """ Utility routine that writes a a jpg or png image to a file with suffix appended to the name

    Inputs:
        orig_path_name (string) : The original image path
        image (tf image) :  The image to write (usually a rotated image)
        suffix (string):  Suffix to append to the original file name for the rotated file name.
        is_jpeg : boolean.  If True, writes a jpeg.  Otherwise writes a png

    Returns:
        True on success, false on failure
    """
    orig_path = pathlib.Path(orig_path_name)
    image_filename = orig_path.parts[-1]
    base_filename, extension = os.path.splitext(image_filename)
    rot_filename = base_filename + '-' + suffix + extension
    new_file_path = os.path.join(os.path.dirname(orig_path_name), rot_filename)
    if os.path.exists(new_file_path):
        print("File " + new_file_path + " already exists; not written")
        return False

    if (is_jpeg):
        encoded_image = tf.image.encode_jpeg(image)
    else:
        encoded_image = tf.image.encode_png(image)
    tf.io.write_file(new_file_path, encoded_image)
    return True

def downsample_images(input_dir_name, reduced_size, output_dir_name, output_suffix):
    """ Reads all the jpg and png images in input_dir_name, downsamples to reduced_size and writes the result to output_dir_name,
    For jpeg images, uses bilinear interpolation with anti-aliasing. For png images, uses nearest neighbor interpolation

    Inputs:
        input_dir_name (string): Path to the directory containing input files
        reduced_size (2-list): [width, height] of output images
        output_dir_name (string): Path to the directory to write the output files  
        output_suffix (string): Added to the end of the file name of the downsampled output file

    Returns:
        True on success, False on failure
    """
    if not filechecks.exists_and_is_dir(input_dir_name):
        print(input_dir_name + ' does not exist or is not a directory')
        return False
    if not os.path.exists(output_dir_name):
        os.mkdir(output_dir_name)
    inputPath = pathlib.Path(input_dir_name)
    for imagePath in inputPath.iterdir():
        imageFilename = imagePath.parts[-1]
        baseFileName, extension = os.path.splitext(imageFilename)
        image = None
        is_jpeg = True
        if extension == '.jpg':
            image = tf.image.decode_jpeg(tf.io.read_file(
                os.path.join(input_dir_name, imageFilename)))
        else:
            if extension == '.png':
                image = tf.image.decode_png(tf.io.read_file(
                    os.path.join(input_dir_name, imageFilename)))
                is_jpeg = False
            else:
                print('Ignoring file ' + imageFilename +
                      ' because not jpg or png')
        if not image == None:
            outPath = os.path.join(
                output_dir_name, baseFileName + output_suffix + extension)
            if os.path.exists(outPath):
                print('Skipping ' + outPath + ' which already exists')
            else:
                if is_jpeg:
                    image = tf.image.resize(image, reduced_size, method=tf.image.ResizeMethod.BILINEAR, antialias=True,preserve_aspect_ratio=True)
                else:
                    image = tf.image.resize(image, reduced_size, method=tf.image.ResizeMethod.NEAREST_NEIGHBOR, preserve_aspect_ratio=True)
                image = tf.cast(image, tf.uint8)
                if extension == '.jpg':
                    tf.io.write_file(outPath, tf.image.encode_jpeg(image))
                else:
                    tf.io.write_file(outPath, tf.image.encode_png(image))
                print('Wrote ' + outPath)

    return True

def add_rotated_images(image_dir_name, seg_dir_name, rot90=True, rot180=True,
                     rot270=True):
    """ Rotates all the jpeg images in the image directory and png images
    in the segmentation directory by the specified amount and
    writes corresponding image files.

    Inpugs:
        image_dir_name (string) :  directory with jpeg images
        seg_dir_name (string) : directory with png images
        rot90 : boolean.  Write an image rotated 90 degrees counter-clockwise?
        rot180 : boolean.  Write an image rotated 180 degrees counter-clockwise?
        rot270 : boolean.  Write an image rotated 270 degrees counter-clockwise?

    Returns:
        True on success, false on failure

    """
    if (not rot90) and (not rot180) and (not rot270):
        print("No rotation specified")
        return False

    if not filechecks.exists_and_is_dir(image_dir_name):
        print(image_dir_name, ' does not exist or is not a directory')
        return False

    image_path = pathlib.Path(image_dir_name)
    paths = []
    # build the lists of images and segementation images, confirming
    # that every image has a matching segmentation image
    for image_file in image_path.iterdir():
        image_file_name = image_file.parts[-1]
        base_file_name, extension = os.path.splitext(image_file_name)
        if (extension == '.jpg') or (extension == '.JPG'):
            seg_file_name = base_file_name + '.png'
            seg_file = os.path.join(seg_dir_name, seg_file_name)
            if not os.path.exists(seg_file):
                print('Missing segmentation file ', seg_file)
                return False
            paths.append(os.path.join(image_dir_name, image_file_name))
            paths.append(seg_file)

    for path in paths:
        print('Rotating file: ' + path)
        is_jpeg = filechecks.is_jpeg_filename(path)
        if is_jpeg:
            image = tf.image.decode_jpeg(tf.io.read_file(path))
        else:
            image = tf.image.decode_png(tf.io.read_file(path))
        # since we may need any subset of the rots, we just generate them all (and tf.image only has rot90)
        image90 = tf.image.rot90(image)
        image180 = tf.image.rot90(image90)
        image270 = tf.image.rot90(image180)

        if rot90:
            write_image_with_suffix(path, image90, 'rot90', is_jpeg)

        if rot180:
            write_image_with_suffix(path, image180, 'rot180', is_jpeg)

        if rot270:
            write_image_with_suffix(path, image270, 'rot270', is_jpeg)

    return True

_SEED_1 = 42 # first seed used/changed in the various apply_random methods
_SEED_2 = 59 # second seeed used/changed in the various apply_random methods

def _next_seed():
    global _SEED_1
    global _SEED_2
    _SEED_1 = _SEED_1 + 1
    _SEED_2 = _SEED_2 - 1
    return (_SEED_1, _SEED_2)

def apply_random_hue(image, max_delta):
    """ Applies tf.image.stateless_random_hue to the given image using arbitrary seeds that are then changed.
    
        NOTE: This is intended for experimenting with the effects of the max_delta parameter on candidate images; it should NOT be used in actual image pipelines
    
    Inputs:
        image (tf.image) : the image to which to apply the hue transform
        max_delta (real) : hue delta will be randomly selected in [-max_delta, max_delta]
    
    Returns:   
        Resulting image
    """
    return tf.image.stateless_random_hue(image, max_delta, _next_seed())

def apply_random_saturation(image, lower, upper):
    """Applies tf.image.stateless_random_saturation to the given image using arbitrary seeds that are then changed.
    
        NOTE: This is intended for experimenting with the effects of the lower and upper parameters to on candidate images; it should NOT be used in actual image pipelines
        
    Inputs:
        image (tf.image) : the image to which to apply the saturation transform
        lower (real) : lower bound for the random saturation factor
        upper (real) : upper bound for the random saturation factor
    """
    return tf.image.stateless_random_saturation(image, lower, upper, _next_seed())

def apply_random_brightness(image, max_delta):
    """ Applies tf.image.stateless_random_brightness to the given image using arbitrary seeds that are then changed.
    
        NOTE: This is intended for experimenting with the effects of the max_delta parameter on candidate images; it should NOT be used in actual image pipelines
    
    Inputs:
        image (tf.image) : the image to which to apply the brightness transform
        max_delta (real) : brightness delta will be randomly selected in [-max_delta, max_delta]
    
    Returns:   
        Resulting image
    """
    return tf.image.stateless_random_brightness(image, max_delta, _next_seed())

def apply_random_contrast(image, lower, upper):
    """Applies tf.image.stateless_random_constrast to the given image using arbitrary seeds that are then changed.
    
        NOTE: This is intended for experimenting with the effects of the lower and upper parameters to on candidate images; it should NOT be used in actual image pipelines
        
    Inputs:
        image (tf.image) : the image to which to apply the saturation transform
        lower (real) : lower bound for the random contrast factor
        upper (real) : upper bound for the random contrast factor
    """
    return tf.image.stateless_random_contrast(image, lower, upper, _next_seed())  

def extract_from_psd(dir_name, target_dir):
    """Produces 2 outputs from a psd file, a JPEG of the base image and a PNG of the corresponding segmentation. Loads files with .psd extension from a directory,
    iterates over the layers inside the .psd file, then saves the last layer as a PNG and the second layer as a JPEG. For purposes of Picta, 
    assumes the first layer is the 'Base' original photo, and the last layer is the 'Segmentation' of the original photo.
    
    Inputs:
        dir_name (string) : the directory path to the location of the psd files
        target_dir (string) : the path to write the generated files to
    """
    files = os.listdir(dir_name)
    for file in files:
        if file.endswith('.psd'):
            fname = file.replace('.psd', '')
            try:
                print('Processing ' + fname)
                psd = PSDImage.open(os.path.join(dir_name,file))
                first = True
                last_layer = None
                for layer in psd.descendants():
                    image = layer.composite()
                    image = image.convert('RGB')
                    if first:
                        image.save(os.path.join(target_dir, fname + ".jpg"),'JPEG')
                        first = False
                    else: 
                        last_layer = layer
                if last_layer != None:
                    image = layer.composite(layer_filter=__layer_filter_true)
                    image = image.convert('RGB')
                    image.save(os.path.join(target_dir,fname + ".png"),'PNG')
                else:
                    print('No last layer found for ' + fname)
            except ValueError:
                print('Failed processing ' + fname)
            
def __layer_filter_true(layer):
    return True

def convert_image_into_tensor_and_apply_model(image, model):
    """Converts an image into a tensor and applies the trained model. 
    
    Inputs:
        image (PIL.Image) : the image to convert into a tensor
        model (Keras model) : the model to apply 
    Returns:
        A tf tensor
    """
    image = tf.convert_to_tensor(image)
    image = tf.cast(image, tf.float32)/255.0
    modeled = tf.math.argmax(model.predict(image[tf.newaxis, ...]),axis=-1)
    modeled = modeled[...,tf.newaxis]
    modeled = modeled[0]
    modeled = modeled * 255
    return modeled

def __crop_and_paste_into_sections(model_dimension, original_image, is_horizontal):
    """Routine to copy original image into two images spanning the entrie original image. Scales down the original image to size model_dimension x z, or 
    z x model_dimension where z = model_dimension * aspect_ratio (horizontal_orientation) or z = model_dimension / aspect ratio (vertical orientation). 
    Creates two images of size model_dimension x model_dimension, and copies their respective portion of the original image using the PIL.Image.paste() function.
    
    Inputs:
        model_dimension (int) : size of the two sections to be created, model_dimension x model_dimension
        og_image (PIL.Image) : the image to copy from
        is_horizontal(boolean) : indicates whether the image has a horizontal (true) or vertical (false) orientation
    Returns:
        left_half_or_top (PIL.Image) : first half of the copied portion of the scaled image. Will always copy the first model_dimension x model_dimension square
        right_half_or_bottom (PIL.Image) : second half of the copied image. Always starts copying at 
        scaled_image.width (int) : width dimension of scaled og_image
        scaled_image.height (int) : height dimension of scaled og_image
        offset (int) : the x or y position where the second image began copying the original image
    """
    aspect_ratio = original_image.width / original_image.height
    left_half_or_top = Image.new("RGB", (model_dimension, model_dimension))
    right_half_or_bottom = Image.new("RGB", (model_dimension, model_dimension))
    if is_horizontal:
        scaled_image = original_image.resize((int(model_dimension * aspect_ratio), model_dimension), resample=Image.BICUBIC)
        offset = scaled_image.width - model_dimension
        right_half_or_bottom.paste(scaled_image.crop((offset, 0, scaled_image.width, scaled_image.height)))
    else:
        scaled_image = original_image.resize((model_dimension, int(model_dimension / aspect_ratio)), resample=Image.BICUBIC)
        offset = scaled_image.height - model_dimension
        right_half_or_bottom.paste(scaled_image.crop((0, offset, scaled_image.width, scaled_image.height)))
    left_half_or_top.paste(scaled_image.crop((0, 0, model_dimension, model_dimension)))
    print("Image size: " + str(original_image.width) + "x" + str(original_image.height) + "\nRescaled to: " + str(scaled_image.width) + "x" + str(scaled_image.height))
    return left_half_or_top, right_half_or_bottom, scaled_image.width, scaled_image.height, offset

def __stitching_loops(x_range, y_range, x_range2, y_range2, preferred_segment, other_segment, x_offset, y_offset, canvas, prefer_segment_left_or_top):
    """Takes two segmentation images and copies portions of both images onto a 'canvas' image of size (x_ range + x_offset) x (y_range + y_offset) representng the 
    size of the scaled original image size. Uses PIL.Image.getpixel() to find white pixels in a range on each segmentation, then uses PIL.Image.putpixel() to 
    place a white pixel on canvas at the appropriate position using the offsets to match its placement on the original image.
    
    Inputs:
        x_range (int) : x range of where to copy from preferred_segement
        y range (int) : y range of where to copy from preferred_segement
        x_range2 (int) : x range of where to copy from other_segment
        y_range2 (int) : y range of where to copy from other_segment
        preferred_segment (PIL.Image) : the mask that will be favored for stitching
        other_segment (PIL.Image) : the secondary mask that will be less favored for stitching, range determined by offset
        x_offset (int) : used to determine where to put pixels from other_segment on x-axis
        y_offset (int) : used to determine where to put pixels from other_segment on y-axis
        canvas (PIL.Image) : stitched image where white pixels will be placed
        prefer_segment_left_or_top (boolean) : used to determine if the preferred_segment is segment_left_or_top (True) or segment_right_or_bottom (False)
    Returns:
        A PIL.Image containing the stitched pixels
    """
    if prefer_segment_left_or_top:
        for x in range(x_range):
            for y in range(y_range):
                if preferred_segment.getpixel((x, y)) == 255:
                    canvas.putpixel((x, y), (255,255,255))
        for x_range2 in range(128):
            for y_range2 in range(128):
                if other_segment.getpixel((x_range2, y_range2)) == 255:
                    canvas.putpixel((x_range2 + x_offset, y_range2 + y_offset), (255,255,255))
    else:
        for x in range(x_range):
            for y in range(y_range):
                if preferred_segment.getpixel((x, y)) == 255:
                    canvas.putpixel((x, y), (255,255,255))
        for x in range(x_range2):
            for y in range(y_range2):
                if other_segment.getpixel((x, y)) == 255:
                    canvas.putpixel((x + x_offset,  + y_offset), (255,255,255))
    return canvas

def __perform_union_stitching(model_dimension, offset, canvas, segment_left_or_top, segment_right_or_bottom, prefer_segment_left_or_top, is_horizontal):
    """Passes the two segmentation images into the stitching loops in the appropriate order
    
    Inputs:
        model_dimension (int) : the size of the segmentation images
        offset (int) : how far down the x or y-axis the copy of segment_right_or_bottom started copying from the orginial image.
        canvas (PIL.Image) : the Image object where the copied pixels will be placed
        segment_left_or_top (PIL.Image) : the first segmentation image to copy from
        segment_right_or_bottom (PIL.Image) : the second segmentation image to copy from
        prefer_segment_left_or_top (boolean) : indicates whether a majority of segment_left_or_top will be copied (True) or segment_right_or_bottom (False)
        is_horizontal (boolean) : indicates whether the stitching should be performed horizonatlly (True) or vertically (False)
    Returns:
        A single PIL.Image containing the stitched segments
    """
    #When stitching, the first check is for the preferred segmentation, followed by the orientation of the image (horizontal, or vertical)
    if prefer_segment_left_or_top:
        if is_horizontal:
            canvas = __stitching_loops(model_dimension, model_dimension, offset, model_dimension, segment_left_or_top, segment_right_or_bottom, offset, 0, canvas, True) #segment copy horizontal           
        else:
            canvas = __stitching_loops(model_dimension, model_dimension, model_dimension, offset, segment_left_or_top, segment_right_or_bottom, 0, offset, canvas, True) #segment copy vertical
    else:
        if is_horizontal:
            canvas = __stitching_loops(offset, model_dimension, model_dimension, model_dimension, segment_left_or_top, segment_right_or_bottom, offset, 0, canvas, False) #segment copy horizontal
        else:
            canvas = __stitching_loops(model_dimension, offset, model_dimension, model_dimension, segment_left_or_top, segment_right_or_bottom, 0, offset, canvas, False) #segment copy vertical
    return canvas

def __count_blobs_and_holes(segment, blob_or_hole):
    """ Performs depth first search on the pixels in a segement image to count either 'blobs' not part of the plastron segment or 'holes' found inside the plastron segment
    Inputs:
        segment (PIL.Image) : the image segment to run the check on
        blob_or_hole (int) : determines whether to check for blobs or holes based on pixel color to check for. 255 (white) for blobs, 0 (black) for holes
    Returns:
        An integer count of blobs or holes
    """
    num_of_blobs_or_holes = 0
    visited = set()
    def bfs(r, c):
        q = deque()
        visited.add((x,y))
        q.append((x,y))
        while q:
            row, col = q.popleft()
            directions =[[1,0], [-1,0], [0,1], [0,-1]]
            for dr, dc in directions:
                r,c = row+dr, col+dc
                if r in range(128) and c in range(128) and segment.getpixel((r,c)) == blob_or_hole and (r, c) not in visited:
                    q.append((r, c))
                    visited.add((r,c))
    for x in range(128):
        for y in range(128):
            if segment.getpixel((x,y)) ==  blob_or_hole and (x,y) not in visited:
                bfs(x,y)
                num_of_blobs_or_holes += 1  
    return num_of_blobs_or_holes

def copy_single_segment_to_canvas(segment, x_offset, y_offset, canvas):
    """ Copies pixel by pixel a 128x128 segment image on to a black canvas of the scaled image dimensions
    Inputs:
        segment (PIL.Image) : the segment to copy
        x_offset (int) : used to determine where to place pixels based on where the plastron resides in the original image
        y_offset (int) : same as x_offset, but for the y-axis
        canvas (PIL.Image) : 'blank' image containing only black pixels of size scaled_image.width by scaled_image.height
    Returns:
        The filled canvas
    """
    for x in range(128):
        for y in range(128):
            if segment.getpixel((x,y)) == 255:
                canvas.putpixel((x + x_offset, y + y_offset), (255,255,255))
    return canvas

def __is_plastron_too_large(segment_left_or_top, segment_right_or_bottom, is_horizontal):
    """Checks the borders of the segmentation images to check if the full plastron from the original image is not fully contained in only segment_left_or_top or segment_right_or_bottom
    Inputs:
        segment_left_or_top (PIL.Image): the first segment generated, no offsets
        segment_right_or_bottom (PIL.Image) : the second segment generated, with offsets
        is_horizontal (boolean) : True if checking the left and right most pixel, False if checking the top and bottom most pixel
    Returns:
        True if the plastron touches the boundaries in both segment images, False otherwise
    """
    possible_edge_left_or_top = False
    possible_edge_right_or_bottom = False
    if is_horizontal:
        for y in range(128):
            if segment_left_or_top.getpixel((127,y)) == 255:
                possible_edge_left_or_top = True
            if segment_right_or_bottom.getpixel((0,y)) == 255:
                possible_edge_right_or_bottom = True
    else:
        for x in range(128):
            if segment_left_or_top.getpixel((x,127)) == 255:
                possible_edge_left_or_top = True
            if segment_right_or_bottom.getpixel((x, 0)) == 255:
                possible_edge_right_or_bottom = True
    if possible_edge_right_or_bottom and possible_edge_left_or_top:
        return True
    else:
        return False

def __find_more_centered_segmentation(segment_left_or_top, segment_right_or_bottom, is_horizontal, offset):
    """Used to determine the preferred segment to copy to the canvas (based on how far the plastron segment is from the center of the image). Also determines whether stitching needs to be performed on the segment images
    Inputs:
        segment_left_or_top (PIL.Image): the first segment generated, no offsets
        segment_right_or_bottom (PIL.Image) : the second segment generated, with offsets
        is_horizontal (boolean) : indicates whether the original image's width > height (True) or width < height (False)
        offset (int) : the starting distance segment_right_or_bottom was copied from in the original image, i.e. not from position (0,0)
    Returns:
        preferred_segment (PIL.Image) : the segment with the plastron closest to the center, or none if sticthing is to be used
        use_stitching (boolean) : indicates whether the stitching loops are necessary or not
        offset (int) : remains the same, unless the preferred segment is segment_left_or_top, in which case the offset will be updated to 0
    """
    distance_left_or_top = 0
    distance_right_or_bottom = 0
    right_or_bottom_most_pixel = 0
    left_or_top_most_pixel = 127
    use_stitching = __is_plastron_too_large(segment_left_or_top, segment_right_or_bottom, is_horizontal)
    preferred_segment = None
    if not use_stitching:
        if is_horizontal:
            for x in range(127):
                for y in range(127):
                    if segment_left_or_top.getpixel((x,y)) == 255 and x > right_or_bottom_most_pixel:
                        right_or_bottom_most_pixel = x
                    if segment_right_or_bottom.getpixel((x,y)) == 255 and x < left_or_top_most_pixel:
                        left_or_top_most_pixel = x
        else:
            for x in range(127):
                for y in range(127):
                    if segment_left_or_top.getpixel((x,y)) == 255 and y > right_or_bottom_most_pixel:
                        right_or_bottom_most_pixel = y
                    if segment_right_or_bottom.getpixel((x,y)) == 255 and y < left_or_top_most_pixel:
                        left_or_top_most_pixel = y
        distance_left_or_top = abs(64 - right_or_bottom_most_pixel)
        distance_right_or_bottom = abs(64 - left_or_top_most_pixel)
        if distance_left_or_top < distance_right_or_bottom:
            preferred_segment = segment_left_or_top
            offset = 0
        elif distance_left_or_top > distance_right_or_bottom:
            preferred_segment = segment_right_or_bottom
        else:
            use_stitching = True
    return preferred_segment, use_stitching, offset


def apply_model_to_image(model, model_dimension, image_file):
    """Creates a segmentation image with the same size dimensions as the passed image_file. Creates two model_dimension x model_dimension images spanning
    
    , applying the model, stitching, and resizing to original size
    
    Inputs:
        model (Keras model): trained neural net model
        model_dimension (int): dimension to use for specific model (128 for Picta, 512 for distress ID)
        image_file (string):  path to the JPG image file

    Returns:
        Resulting stitched PIL.Image
    """
    if model_dimension != 128 and model_dimension != 512:
        print('Invalid dimensions selected. Must be 128 or 512')
        return False
    is_jpeg = filechecks.is_jpeg_filename(image_file)
    if not is_jpeg:
        print('File is not a JPG')
        return False
    image = Image.open(image_file)
    width, height = image.size
    if width > height:      #Meaning horizontal orientation
        horizontal = True
        left_half_or_top, right_half_or_bottom, scaled_width, scaled_height, offset = __crop_and_paste_into_sections(model_dimension, image, horizontal)
    else:                   #Meaning vertical orientation
        horizontal = False
        left_half_or_top, right_half_or_bottom, scaled_width, scaled_height, offset = __crop_and_paste_into_sections(model_dimension, image, horizontal)
    left_or_top_tensor = convert_image_into_tensor_and_apply_model(left_half_or_top, model)
    right_or_bottom_tensor = convert_image_into_tensor_and_apply_model(right_half_or_bottom, model)
    segment_left_or_top = tf.keras.utils.array_to_img(left_or_top_tensor)
    segment_right_or_bottom = tf.keras.utils.array_to_img(right_or_bottom_tensor)
    segment_to_use, use_stitching, offset = __find_more_centered_segmentation(segment_left_or_top, segment_right_or_bottom, horizontal, offset)
    canvas = Image.new("RGB", (scaled_width, scaled_height))
    if use_stitching:
        #When using stitching, the segment with least amount of holes and blobs not part of the plastron is used as the preferred segment   
        blobs_segement_left_or_top = __count_blobs_and_holes(segment_left_or_top, 255)
        holes_in_segment_left_or_top = __count_blobs_and_holes(segment_left_or_top, 0)
        blobs_segement_right_or_bottom = __count_blobs_and_holes(segment_right_or_bottom, 255)
        holes_in_segment_right_or_bottom = __count_blobs_and_holes(segment_right_or_bottom, 0)
        if (blobs_segement_right_or_bottom < blobs_segement_left_or_top or holes_in_segment_right_or_bottom < holes_in_segment_left_or_top) and \
            (blobs_segement_right_or_bottom != 0):
            preferSegmentA = False
        elif (blobs_segement_right_or_bottom > blobs_segement_left_or_top or holes_in_segment_right_or_bottom > holes_in_segment_left_or_top) and \
            (blobs_segement_left_or_top != 0):
            preferSegmentA = True
        else:
            preferSegmentA = True
        filled_canvas = __perform_union_stitching(model_dimension, offset, canvas, segment_left_or_top, segment_right_or_bottom, preferSegmentA, horizontal)
    else:
        if horizontal:
            filled_canvas = copy_single_segment_to_canvas(segment_to_use, offset, 0, canvas)
        else:
            filled_canvas = copy_single_segment_to_canvas(segment_to_use, 0, offset, canvas)                               
    final_mask = filled_canvas.resize((width, height), resample=Image.BOX)
    final_mask_array = np.array(final_mask)
    #To 'smooth' the blocky pixels from upsacling the image, two morphological operations are performed, cv2.morpholgyEx() using MORPH_ELLIPSE and PIL.ImageFileter.ModeFilter(). The first changes the blocky pixels into ellipses, the second smoothes the valleys created by the ellipses. Decreasing the value of size in ModeFilter will speed up the runtime at the cost of 'smoothness' acheived
    smoothed_final_mask = Image.fromarray(cv2.morphologyEx(final_mask_array, cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))).filter(ImageFilter.ModeFilter(size=13))  
    return smoothed_final_mask