import os
import rawpy
import tempfile
import threading
import tkinter as tk
import tensorflow as tf
import numpy as np
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image, ImageFilter
import cv2
from psd_tools import PSDImage
from collections import deque

def extract_from_psd(dir_name, target_dir):
    """Produces 2 outputs from a psd file, a JPEG of the base image and a PNG of the corresponding segmentation
    
    Inputs:
        dir_name (string) : the directory path to the location of the psd files
        target_dir (string) : the path to write the generated files to
    """
    pics = os.listdir(dir_name)
    for pic in pics:
        fname = pic.replace('.psd', '')
        try:
            print('Processing ' + fname)
            psd = PSDImage.open(os.path.join(dir_name,pic))
            first = True
            last = None
            for layer in psd.descendants():
                image = layer.composite()
                image = image.convert('RGB')
                if first:
                    image.save(os.path.join(target_dir, fname + ".jpg"),'JPEG')
                    first = False
                else: 
                    last = layer
            if last != None:
                image = layer.composite(layer_filter=__layer_filter_true)
                image = image.convert('RGB')
                image.save(os.path.join(target_dir,fname + ".png"),'PNG')
            else:
                print('No last layer found for ' + fname)
        except ValueError:
            print('Failed processing ' + fname)
            
def __layer_filter_true(layer):
    return True

def __crop_and_paste_into_sections(model_dimension, og_image, is_horizontal):
    """Scales down the original image, creates two images of model_dimension x model_dimension size, and copies the respective portion of the original image to said images
    
    Inputs:
        model_dimension (int) : size of the two sections to be created
        og_image (PIL.Image) : the image to copy from
        is_horizontal(boolean) : indicates whether the image has a horizontal (true) or vertical (false) orientation
    Returns:
        left_half_or_top (PIL.Image) : first half of the copied image
        right_half_or_bottom (PIL.Image) : second half of the copied image
        scaled_image.width (int) : width dimension of scaled og_image
        scaled_image.height (int) : height dimension of scaled og_image
        offset (int) : the x or y position where the second image began copying the original image
    """
    aspect_ratio = og_image.width / og_image.height
    left_half_or_top = Image.new("RGB", (model_dimension, model_dimension))
    right_half_or_bottom = Image.new("RGB", (model_dimension, model_dimension))
    if is_horizontal:
        scaled_image = og_image.resize((int(model_dimension * aspect_ratio), model_dimension), resample=Image.BICUBIC)
        offset = scaled_image.width - model_dimension
        right_half_or_bottom.paste(scaled_image.crop((offset, 0, scaled_image.width, scaled_image.height)))
    else:
        scaled_image = og_image.resize((model_dimension, int(model_dimension / aspect_ratio)), resample=Image.BICUBIC)
        offset = scaled_image.height - model_dimension
        right_half_or_bottom.paste(scaled_image.crop((0, offset, scaled_image.width, scaled_image.height)))
    left_half_or_top.paste(scaled_image.crop((0, 0, model_dimension, model_dimension)))
    print("Image size: " + str(og_image.width) + "x" + str(og_image.height) + "\nRescaled to: " + str(scaled_image.width) + "x" + str(scaled_image.height))
    return left_half_or_top, right_half_or_bottom, scaled_image.width, scaled_image.height, offset


def apply_model_to_tensor(image, model):
    """Converts an image into a tensor and applies the trained model
    
    Inputs:
        image (PIL.Image) : the image to convert into a tensor
        model (Keras model) : the model to apply 
    Returns:
        A tf tensor
    """
    image = np.array(image)
    image = tf.convert_to_tensor(image)
    image = tf.cast(image, tf.float32)/255.0
    modeled = tf.math.argmax(model.predict(image[tf.newaxis, ...]),axis=-1)
    modeled = modeled[...,tf.newaxis]
    modeled = modeled[0]
    modeled = modeled * 255
    return modeled

def __stitching_loops(x_range, y_range, x_range2, y_range2, preferred_segment, other_segment, x_offset, y_offset, canvas, preferSegmentA):
    """The stitching loops occur here, where if a white pixel is found on a segment it is copied onto the canvas
    
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
    Returns:
        A PIL.Image containing the stitched pixels
    """
    if preferSegmentA:
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

def __perform_union_stitching(model_dimension, offset, canvas, segmentA, segmentB, preferSegmentA, is_horizontal):
    """Creates a stitched segmentation image by combining the pixels from segmentA and segmentB
    
    Inputs:
        model_dimension (int) : the size of the segmentation images
        offset (int) : the start of where segmentB copied the orginial image
        canvas (PIL.Image) : the Image object where the copied pixels will be placed
        segmentA (PIL.Image) : the first mask to check for pixels
        segmentB (PIL.Image) : the second mask to check for pixels
        preferSegmentA (boolean) : indicates whether a majority of segmentA will be copied (True) or segmentB (False)
        is_horizontal (boolean) : indicates whether the stitching should be performed horizonatlly (True) or vertically (False)
    Returns:
        A single PIL.Image containing the stitched segments
    """

    #When stitching, the first check is for the preferred segmentation, followed by the orientation of the image (horizontal, or vertical)
    if preferSegmentA:
        if is_horizontal:
            canvas = __stitching_loops(model_dimension, model_dimension, offset, model_dimension, segmentA, segmentB, offset, 0, canvas, True) #segment copy horizontal           
        else:
            canvas = __stitching_loops(model_dimension, model_dimension, model_dimension, offset, segmentA, segmentB, 0, offset, canvas, True) #segment copy vertical
    else:
        if is_horizontal:
            canvas = __stitching_loops(offset, model_dimension, model_dimension, model_dimension, segmentA, segmentB, offset, 0, canvas, False) #segment copy horizontal
        else:
            canvas = __stitching_loops(model_dimension, offset, model_dimension, model_dimension, segmentA, segmentB, 0, offset, canvas, False) #segment copy vertical
    return canvas

def __count_blobs_and_holes(segment, blob_or_hole):
    """255 for blobs, 0 for holes
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
    for x in range(128):
        for y in range(128):
            if segment.getpixel((x,y)) == 255:
                canvas.putpixel((x + x_offset, y + y_offset), (255,255,255))
    return canvas

def __is_plastron_too_large(segment_left_or_top, segment_right_or_bottom, is_horizontal):
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

def apply_model_to_image(model, model_dimension, image_file):
    """Creates a stitched segmentation image by scaling to model_dimension, creating two halves, applying the model, stitching, and resizing to original size
    
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
    is_jpeg = is_jpeg_filename(image_file)
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

    left_or_top_tensor = apply_model_to_tensor(left_half_or_top, model)
    right_or_bottom_tensor = apply_model_to_tensor(right_half_or_bottom, model)
    #Converting the tensors into images for stitching and creating the canvas to put the sticthed image
    segment_left_or_top = tf.keras.utils.array_to_img(left_or_top_tensor)
    segment_right_or_bottom = tf.keras.utils.array_to_img(right_or_bottom_tensor)
    segment_to_use, use_stitching, offset = __find_more_centered_segmentation(segment_left_or_top, segment_right_or_bottom, horizontal, offset)
    canvas = Image.new("RGB", (scaled_width, scaled_height))
    if use_stitching:   
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
    smoothed_final_mask = Image.fromarray(cv2.morphologyEx(final_mask_array, cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))).filter(ImageFilter.ModeFilter(size=13))  
    return smoothed_final_mask

#Temporary directory for use with loading single NEF files
temp_dir = tempfile.TemporaryDirectory()

window = tk.Tk()
window.title("Apply Model to Image")
window.geometry("1400x750")


model = ''
fname = ''
file_path = ''
segment_image = ''
og_image = ''
og_image_display = tk.Label()
segment_display = tk.Label()
merged_image_display = tk.Label()
not_merged = True
no_segment_loaded = True

jpeg_list = []
png_list = []
index_of_image_lists = 0
input_directory = ''
output_directory = ''
cancel_image_process = False

def load_model():
    global model
    model_path = filedialog.askopenfilename(filetypes=[('keras files', '*.keras')])
    model = tf.keras.models.load_model(model_path)
    file_menu.entryconfig(0, state=tk.ACTIVE)
    file_menu.entryconfig(1, state=tk.ACTIVE)
    file_menu.entryconfig(2, state=tk.ACTIVE)
    file_menu.entryconfig(3, state=tk.ACTIVE)
    file_menu.entryconfig(4, state=tk.ACTIVE)
    file_menu.entryconfig(5, state=tk.ACTIVE)
    file_menu.entryconfig(6, state=tk.DISABLED)

def open_file_dialog():
    global jpeg_list
    jpeg_list.clear()
    global index_of_image_lists
    index_of_image_lists = 0
    global no_segment_loaded
    no_segment_loaded = True
    global og_image_display
    __clear_screen()
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("JPG files", "*.jpg")])
    global output_directory
    output_directory = os.path.dirname(file_path)
    global fname
    fname = os.path.basename(file_path)
    jpeg_list.append(fname)
    label_selected_image_name.config(text='Selected: ' + fname)
    global og_image
    og_image = Image.open(file_path)
    resized = __fit_image(og_image)
    og_imagetk = ImageTk.PhotoImage(resized)  
    og_image_display = tk.Label(window, image=og_imagetk)
    og_image_display.image = og_imagetk
    og_image_display.grid(row=3, column=0, columnspan=1)
    button_apply_model['state'] = tk.ACTIVE
    button_next_image['state'] = tk.DISABLED
    button_previous_image['state'] = tk.DISABLED
    
    

def open_nef_dialog():
    global jpeg_list
    jpeg_list.clear()
    global index_of_image_lists
    index_of_image_lists = 0
    global no_segment_loaded
    no_segment_loaded = True
    global og_image_display
    __clear_screen()
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[('NEF files', '*.NEF')])
    global output_directory
    output_directory = os.path.dirname(file_path)
    global fname
    fname = os.path.basename(file_path)
    jpeg_list.append(fname)
    label_selected_image_name.config(text='Selected: ' + fname)
    raw_file = rawpy.imread(file_path)
    raw_array = raw_file.postprocess(use_auto_wb=True)
    global og_image 
    og_image = Image.fromarray(raw_array)
    resized = __fit_image(og_image)
    og_imagetk = ImageTk.PhotoImage(resized)
    og_image_display = tk.Label(window, image=og_imagetk)
    og_image_display.image = og_imagetk
    og_image_display.grid(row=3, column=0, columnspan=1)
    print(temp_dir.name)
    base_name = os.path.splitext(fname)[0]
    file_path = os.path.join(temp_dir.name, base_name+'.jpg')
    og_image.save(file_path, 'JPEG')
    button_apply_model['state'] = tk.ACTIVE
    button_next_image['state'] = tk.DISABLED
    button_previous_image['state'] = tk.DISABLED

    

def display_segmentation():
    """Functionality for button_apply_model. 
    """
    global segment_display
    segment_display.grid_forget()
    global no_segment_loaded
    no_segment_loaded = False
    global segment_image
    segment_image = apply_model_to_image(model, 128, file_path)
    resized = __fit_image(segment_image)
    segment_imagetk = ImageTk.PhotoImage(resized)
    segment_display = tk.Label(window, image=segment_imagetk)
    segment_display.image = segment_imagetk
    segment_display.grid(row=3, column=1)
    button_merge_images['state'] = tk.NORMAL
    button_save_segmented_area['state'] = tk.ACTIVE
    button_apply_model['state'] = tk.DISABLED
    #This won't work until I change the way I process loading of single images, needs to match the way directories are loaded
    #button_pick_new_segmentation.grid(row=2, column= 1)
    #button_pick_new_segmentation['state'] = tk.ACTIVE

def merge_images():
    """Functionality for button_merge_images. Overlays the segmentation image over the original image through the use of PIL Image.blend()
    """
    global not_merged
    if not_merged:
        og_image_display.grid_forget()
        merged_image = Image.blend(og_image, segment_image, 0.5)
        resized = __fit_image(merged_image)       
        merged_imagetk = ImageTk.PhotoImage(resized)
        global merged_image_display
        merged_image_display = tk.Label(window, image=merged_imagetk)
        merged_image_display.image = merged_imagetk
        merged_image_display.grid(row=3, column=0)
        not_merged = False
    else:
        merged_image_display.grid_forget()
        og_image_display.grid(row=3, column=0, columnspan=1)
        segment_display.grid(row=3, column=1)
        not_merged = True

def save_segment():
    if no_segment_loaded:
        messagebox.showerror('Error', 'No segmentation has been generated.')
    else:
        directory = filedialog.askdirectory()
        if directory:
            base_name = os.path.basename(fname)
            path_and_name = os.path.join(directory, 'segmented-'+base_name)
            print(path_and_name)
            segment_image.save(path_and_name)

def __fit_image(image):
    """Resizes the image for the purpose of fitting it in on the window screen.

    Inputs:
        image (PIL.Image) : the image to be resized 
    """
    window_width, window_height = window.winfo_width(), window.winfo_height()
    aspect_ratio = image.width / image.height
    if aspect_ratio > 1:  # Image is wider
        width = int(window_width * 0.48)
        height = int(width / aspect_ratio)
    else:  # Image is taller
        height = int(window_height * 0.7) 
        width = int(height * aspect_ratio)
    image = image.resize((width, height), Image.BICUBIC)
    return image

def __clear_screen():
    """Removes the labels containing images and sets the screen back to a neutral state
    """
    og_image_display.grid_forget()
    segment_display.grid_forget()
    merged_image_display.grid_forget()
    button_pick_new_segmentation.grid_forget()
    button_apply_model['state'] = tk.DISABLED
    button_pick_new_segmentation['state'] = tk.DISABLED
    button_next_image['state'] = tk.DISABLED
    button_previous_image['state'] = tk.DISABLED
    button_save_segmented_area['state'] = tk.DISABLED
    button_process_jpeg_directory['state'] = tk.DISABLED
        
def __display_image_and_mask():
    __clear_screen()
    global fname
    fname = jpeg_list[index_of_image_lists]
    base_name = os.path.basename(fname)
    label_selected_image_name.config(text='Viewing: ' + base_name)
    global og_image
    og_image = Image.open(os.path.join(output_directory, jpeg_list[index_of_image_lists]))
    resized_image = __fit_image(og_image)
    og_imagetk = ImageTk.PhotoImage(resized_image)
    global og_image_display
    og_image_display = tk.Label(window, image=og_imagetk)
    og_image_display.image = og_imagetk
    og_image_display.grid(row=3, column=0)
    global segment_image
    segment_image = Image.open(os.path.join(output_directory, png_list[index_of_image_lists]))
    resized_segment = __fit_image(segment_image)
    global no_segment_loaded
    no_segment_loaded = False
    segment_imagetk = ImageTk.PhotoImage(resized_segment)
    global segment_display
    segment_display = tk.Label(window, image=segment_imagetk)
    segment_display.image = segment_imagetk
    segment_display.grid(row=3, column=1)
    button_previous_image['state'] = tk.ACTIVE
    button_next_image['state'] = tk.ACTIVE
    button_pick_new_segmentation.grid(row=2, column= 1)
    button_pick_new_segmentation['state'] = tk.ACTIVE
    button_save_segmented_area['state'] = tk.ACTIVE    

    

def __pick_input_and_output_directory():
    messagebox.showinfo('Instructions', 'Select the folder with your raw image .NEF files')
    input_directory = filedialog.askdirectory()  
    if input_directory:
        messagebox.showinfo('Instructions', 'Select which folder to output the generated JPEGs and masks')
        output_directory = filedialog.askdirectory()
        if output_directory:
            return input_directory, output_directory

def __pick_directory_for_jpegs():
    global input_directory
    global output_directory
    messagebox.showinfo('Instructions', 'Select the folder with your .jpg image files')
    input_directory = filedialog.askdirectory()
    if input_directory:
        output_directory = input_directory
        return input_directory, output_directory

def cancel_process_image():
    global cancel_image_process
    cancel_image_process = True

def load_JPEG_files():
    __clear_screen
    global input_directory
    global output_directory
    try:
        input_directory, output_directory = __pick_directory_for_jpegs()  
        button_process_jpeg_directory['state'] = tk.ACTIVE
        label_selected_image_name.config(text='Next click the \"Load JPEG files\" button', font=('', '15'))

    except:
        print('Yeah it messed up')
        label_selected_image_name.config(text='Error when picking directories, try again.', font=('', '15'))
        button_process_directory['state'] = tk.DISABLED


def start_thread_for_process_JPEG_files():
    t1 = threading.Thread(target=process_JPEG_files)
    t1.start()

def process_JPEG_files():
    """Functionality for button_process_jpeg_directory. Takes all jpegs from global variable input_directory, produces and saves a segmentation, and then displays the iamge and segmentation.
    
    """
    global cancel_image_process
    cancel_image_process = False
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100, length=250)
    progress_bar.place(relx=0.40, rely=0.45)
    jpg_files = os.listdir(input_directory)
    stop_button = tk.Button(window, text='Cancel', command=cancel_process_image)
    stop_button.place(relx=0.47, rely=0.49)
    for i in range(len(jpg_files)):
        try:
            if '.jpg' in jpg_files[i]:
                base_filename = os.path.splitext(jpg_files[i])[0]
                mask_png = apply_model_to_image(model, 128, os.path.join(input_directory, base_filename+'.jpg'))
                mask_png.save(os.path.join(output_directory, base_filename+'_masked.png'), 'PNG') #Second arg of 'PNG' ensures image will be saved with PNG encoding
                progress_var.set((i + 1) * 100 / len(jpg_files))
                window.update_idletasks()
        except:
            print('Invalid file found, skipping.')
    progress_bar.place_forget()
    stop_button.place_forget()
    #messagebox.showinfo('Info', 'Wrote ' + str(i*2 - 1) + ' files to ' + output_directory)
    load_directory(input_directory)
    __display_image_and_mask()
    button_next_image['state'] = tk.ACTIVE
    button_process_jpeg_directory['state'] = tk.DISABLED
    button_merge_images['state'] = tk.ACTIVE 

def load_NEF_files():
    __clear_screen()
    global input_directory
    global output_directory
    try:
        input_directory, output_directory = __pick_input_and_output_directory()  
        button_process_directory['state'] = tk.ACTIVE
        label_selected_image_name.config(text='Next click the \"Load NEF files\" button', font=('', '15'))

    except:
        print('Yeah it messed up')
        label_selected_image_name.config(text='Error when picking directories, try again.', font=('', '15'))
        button_process_directory['state'] = tk.DISABLED

def start_thread_process_raw_images():
    t1 = threading.Thread(target=process_raw_images)
    t1.start()

def process_raw_images():
    global cancel_image_process
    cancel_image_process = False
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100, length=250)
    progress_bar.place(relx=0.40, rely=0.45)
    stop_button = tk.Button(window, text='Cancel', command=cancel_process_image)
    stop_button.place(relx=0.47, rely=0.49)
    raw_files = os.listdir(input_directory)
    for i in range(len(raw_files)):
        if not cancel_image_process:
            try:
                if '.NEF' in raw_files[i] or '.nef' in raw_files[i]:
                    base_filename = os.path.splitext(raw_files[i])[0]
                    raw_file = rawpy.imread(os.path.join(input_directory, raw_files[i]))
                    raw_array = raw_file.postprocess(use_auto_wb=True)
                    new_jpeg = Image.fromarray(raw_array)
                    new_jpeg.save(os.path.join(output_directory, base_filename+'.jpg'), 'JPEG')
                    mask_png = apply_model_to_image(model, 128, os.path.join(output_directory, base_filename+'.jpg'))
                    mask_png.save(os.path.join(output_directory, base_filename+'_masked.png'), 'PNG') #Second arg of 'PNG' ensures image will be saved with PNG encoding
                    progress_var.set((i + 1) * 100 / len(raw_files))
                    window.update_idletasks()
            except:
                print('Invalid file found, skipping.')
        else:
            break
    progress_bar.place_forget()
    stop_button.place_forget()
    messagebox.showinfo('Info', 'Wrote ' + str(i*2 - 1) + ' files to ' + output_directory)
    load_directory(output_directory)
    __display_image_and_mask()
    button_next_image['state'] = tk.ACTIVE
    button_process_directory['state'] = tk.DISABLED
    button_merge_images['state'] = tk.ACTIVE   

def load_directory(path):
    global jpeg_list
    global png_list
    global index_of_image_lists
    index_of_image_lists = 0
    jpeg_list.clear()
    png_list.clear()
    files = os.listdir(path)
    print(files)
    for file in files:
        if '.jpg' in file:
            if not '_segmented' in file:
                jpeg_list.append(file)
        if '.png' in file:
            png_list.append(file)
    jpeg_list.sort()
    png_list.sort()

def file_function_load_directory():
    try:
        global output_directory
        output_directory = filedialog.askdirectory()
        load_directory(output_directory)
        __display_image_and_mask()
        button_next_image['state'] = tk.ACTIVE
        button_merge_images['state'] = tk.ACTIVE
    except:
        label_selected_image_name.config(text='Invalid directory selected, try again.', font=('', '15'))
        print('Error loading directory. Possibly no JPEGs or PNGs included in directory')

def display_previous_image():
    """Functionality for button_previous_image. Decrements the position of index_of_image lists if possible, then displays displays image and mask
    """
    global index_of_image_lists
    button_next_image['state'] = tk.NORMAL
    if index_of_image_lists == 0:
        button_previous_image['state'] = tk.DISABLED
        return False
    button_previous_image['state'] = tk.NORMAL
    index_of_image_lists -= 1
    __display_image_and_mask()

def display_next_image():
    """Functionality for button_next_image. Increments the position of index_of_image lists if possible, then displays displays image and mask
    """
    global index_of_image_lists
    index_of_image_lists += 1
    button_previous_image['state'] = tk.NORMAL
    if index_of_image_lists >= len(jpeg_list):
        button_next_image['state'] = tk.DISABLED
        return False
    button_next_image['state'] = tk.NORMAL 
    __display_image_and_mask()


def pick_new_segmentation():
    def __get_plastron_distance_from_center(segment_left_or_top, is_horizontal):
        """Used to determine the offset for Segment B (the 'middle' position of the plastron) by checking for the white pixel closest to the center of the plastron

        segment_left_or_top (PIL.Image) : the Segment A ('left' most position of the plastron ) of the original image
        is_horizontal (boolean) : true if the image width > height, false otherwise. Determines whether to use Left/Right most pixel or Top/Bottom most pixel
        """
        left_or_top_most_pixel = 127
        right_or_bottom_most_pixel = 0
        if is_horizontal:
            for x in range(127):
                for y in range(127):
                    if segment_left_or_top.getpixel((x,y)) == 255:
                        if x < left_or_top_most_pixel:
                            left_or_top_most_pixel = x
                        if x > right_or_bottom_most_pixel:
                            right_or_bottom_most_pixel = x
        else:
            for x in range(127):
                for y in range(127):
                    if segment_left_or_top.getpixel((x,y)) == 255:
                        if y < left_or_top_most_pixel:
                            left_or_top_most_pixel = y
                        if y > right_or_bottom_most_pixel:
                            right_or_bottom_most_pixel = y
        distance_left_or_top = abs(128 - left_or_top_most_pixel)
        distance_right_or_bottom = abs(128 - right_or_bottom_most_pixel)
        if distance_left_or_top < distance_right_or_bottom:
            distance = distance_left_or_top
        else:
            distance = distance_right_or_bottom
        return distance

    def __create_cropped_sections(path_to_image):
        left_or_top = Image.new("RGB", (128, 128))
        middle = Image.new("RGB", (128, 128))
        right_or_bottom = Image.new("RGB", (128, 128))
        image = Image.open(path_to_image)
        width, height = image.size   
        if width > height:
            is_horizontal = True
        else:
            is_horizontal = False
        aspect_ratio = width / height
        if is_horizontal:
            scaled_image = image.resize((int(128 * aspect_ratio), 128), resample=Image.BICUBIC)
            offset = scaled_image.width - 128
        else:
            scaled_image = image.resize((128, int(128 * aspect_ratio)), resample=Image.BICUBIC)
            offset = scaled_image.height - 128
        left_or_top.paste(scaled_image.crop((0, 0, 128, 128)))
        tensor_left_or_top = apply_model_to_tensor(left_or_top, model)
        segment_left_or_top = tf.keras.utils.array_to_img(tensor_left_or_top)
        middle_offset = __get_plastron_distance_from_center(segment_left_or_top, is_horizontal)
        if is_horizontal:
            middle.paste(scaled_image.crop((middle_offset, 0, 128 + middle_offset, 128 + middle_offset)))
            right_or_bottom.paste(scaled_image.crop((offset, 0, scaled_image.width, scaled_image.height)))
        else:
            middle.paste(scaled_image.crop((0, middle_offset, 128 + middle_offset, 128 + middle_offset)))
            right_or_bottom.paste(scaled_image.crop((0, offset, scaled_image.width, scaled_image.height)))
        tensor_middle = apply_model_to_tensor(middle, model)
        segment_middle = tf.keras.utils.array_to_img(tensor_middle)
        tensor_right_or_bottom = apply_model_to_tensor(right_or_bottom, model)
        segement_right_or_bottom = tf.keras.utils.array_to_img(tensor_right_or_bottom) 
        segments_and_offsets = [segment_left_or_top, 0, segment_middle, middle_offset, segement_right_or_bottom, offset] 
        return segments_and_offsets, scaled_image

    def __resize_segment_choices(image):
        window_width, window_height = window.winfo_width(), window.winfo_height()
        width = int(window_width * 0.15)
        height = int(window_height * 0.25)
        image = image.resize((width, height), Image.BICUBIC)
        return image

    def __resize_segment_to_image_size(segment, offset, scaled_image):
        canvas = Image.new("RGB", (scaled_image.width, scaled_image.height))
        if scaled_image.width > scaled_image.height:
            filled_canvas = copy_single_segment_to_canvas(segment, offset, 0, canvas)
        else:
            filled_canvas = copy_single_segment_to_canvas(segment, 0, offset, canvas)
        new_segment = filled_canvas.resize((original_image.width, original_image.height), resample=Image.BOX)
        __compare_new_segment_to_og(new_segment)

    def __redisplay_segment_choices():
        choice_window.destroy()
        pick_new_segmentation()

    def __show_merged_segments(new_segment):
        global segments_merged
        if segments_merged:
            global display_merged_image_old
            global display_merged_image_new
            display_merged_image_new.grid_forget()
            display_merged_image_old.grid_forget()
            old_segment_display.grid(row=1, column=0)
            new_segment_display.grid(row=1, column=1)
            segments_merged = False
        else:
            new_segment_display.grid_forget()
            old_segment_display.grid_forget()
            merged_image_old = Image.blend(original_image, segment_image, 0.5)
            merged_image_new = Image.blend(original_image, new_segment, 0.5)
            merged_image_oldtk = ImageTk.PhotoImage(__fit_image(merged_image_old))
            merged_image_newtk = ImageTk.PhotoImage(__fit_image(merged_image_new))
            display_merged_image_old = tk.Label(choice_window, image=merged_image_oldtk)
            display_merged_image_old.image = merged_image_oldtk
            display_merged_image_new = tk.Label(choice_window, image=merged_image_newtk)
            display_merged_image_new.image = merged_image_newtk
            display_merged_image_old.grid(row=1,column=0)
            display_merged_image_new.grid(row=1,column=1)
            segments_merged = True

    def __update_and_save_new_segmentation(new_segment):
        segment_path = os.path.join(output_directory, png_list[index_of_image_lists])
        new_segment.save(segment_path)
        choice_window.destroy()
        __display_image_and_mask()

    def __compare_new_segment_to_og(new_segment):
        global label_for_og_segment
        global label_for_new_segment
        global button_see_segment_choices
        global button_overwrite_and_save_new_segment
        global old_segment_display
        global new_segment_display
        segmentA_display.grid_forget()
        segmentB_display.grid_forget()
        segmentC_display.grid_forget()
        btn_segmentA.grid_forget()
        btn_segmentB.grid_forget()
        btn_segmentC.grid_forget()
        original_segment_display.grid_forget()
        label_original_segment.grid_forget()
        label_for_og_segment = tk.Label(choice_window, text='Original Segmentation')
        label_for_og_segment.grid(row=0, column=0)
        old_segmenttk = ImageTk.PhotoImage(__fit_image(segment_image))
        old_segment_display = tk.Label(choice_window, image=old_segmenttk)
        old_segment_display.image = old_segmenttk
        old_segment_display.grid(row=1, column=0)
        label_for_new_segment = tk.Label(choice_window, text='New Segmentation')
        label_for_new_segment.grid(row=0, column=1)
        new_segmenttk = ImageTk.PhotoImage(__fit_image(new_segment))
        new_segment_display = tk.Label(choice_window, image=new_segmenttk)
        new_segment_display.image = new_segmenttk
        new_segment_display.grid(row=1, column=1)
        button_see_segment_choices = tk.Button(choice_window, text='<- Back', command=__redisplay_segment_choices)
        button_see_segment_choices.place(relx=0.26, rely=0.8)
        button_show_overlay_on_og_image = tk.Button(choice_window, text='Show Merged On Original Image', command=lambda:__show_merged_segments(new_segment))
        button_show_overlay_on_og_image.place(relx=0.38, rely=0.8)
        button_overwrite_and_save_new_segment = tk.Button(choice_window, text='Update and Save New Segmentation', command=lambda:__update_and_save_new_segmentation(new_segment))
        button_overwrite_and_save_new_segment.place(relx=0.55, rely=0.8)
    
    choice_window = tk.Toplevel(window)
    choice_window.geometry('1400x750')
    choice_window.title('Choose Different Segmentation')
    choice_window.transient(window)
    choice_window.grab_set()
    global index_of_image_lists
    global jpeg_list
    global png_list
    global output_directory
    global btn_segmentA
    global btn_segmentB
    global btn_segmentC
    global segmentA_display
    global segmentB_display
    global segmentC_display
    global original_segment_display
    global label_original_segment
    global original_image
    global segments_merged
    segments_merged = False
    original_image_path = os.path.join(output_directory, jpeg_list[index_of_image_lists])
    original_image = Image.open(original_image_path)
    segments_and_offsets, scaled_image =  __create_cropped_sections(original_image_path)
    #Displaying segment options and original segmentation
    segmentAtk = ImageTk.PhotoImage(__resize_segment_choices(segments_and_offsets[0]))
    segmentA_display = tk.Label(choice_window, image=segmentAtk)
    segmentA_display.image = segmentAtk
    segmentA_display.grid(row=1, column=0)
    segmentBtk = ImageTk.PhotoImage(__resize_segment_choices(segments_and_offsets[2]))
    segmentB_display = tk.Label(choice_window, image=segmentBtk)
    segmentB_display.image = segmentBtk
    segmentB_display.grid(row = 1, column = 1)
    segmentCtk = ImageTk.PhotoImage(__resize_segment_choices(segments_and_offsets[4]))
    segmentC_display = tk.Label(choice_window, image=segmentCtk)
    segmentC_display.image = segmentCtk
    segmentC_display.grid(row= 1, column=2)
    original_segmenttk = ImageTk.PhotoImage(__fit_image(segment_image))
    original_segment_display = tk.Label(choice_window, image=original_segmenttk)
    original_segment_display.image = original_segmenttk
    original_segment_display.grid(row=3, column=1)
    label_original_segment = tk.Label(choice_window, text='Current Segment')
    label_original_segment.grid(row=4, column=1)
    btn_segmentA = tk.Button(choice_window, text='Segment A', command=lambda:__resize_segment_to_image_size(segments_and_offsets[0], segments_and_offsets[1], scaled_image))
    btn_segmentA.grid(row=2, column=0)
    btn_segmentB = tk.Button(choice_window, text='Segment B', command=lambda:__resize_segment_to_image_size(segments_and_offsets[2], segments_and_offsets[3], scaled_image))
    btn_segmentB.grid(row=2, column=1)
    btn_segmentC = tk.Button(choice_window, text='Segment C', command=lambda:__resize_segment_to_image_size(segments_and_offsets[4], segments_and_offsets[5], scaled_image))
    btn_segmentC.grid(row=2, column=2)

def get_segmented_area():
    global segment_image
    global og_image
    original_image_array = np.array(og_image)
    binary_mask = np.array(segment_image) == 255
    segmented_area = np.zeros_like(original_image_array)
    segmented_area[binary_mask] = original_image_array[binary_mask]
    segmented_image = Image.fromarray(segmented_area)
    base_filename = os.path.splitext(jpeg_list[index_of_image_lists])[0]
    segmented_image.save(os.path.join(output_directory, base_filename+'_segmented.jpg'), 'JPEG')
    messagebox.showinfo('Save Successful', 'Segmented area saved')



""" def show_help():
    help_window = tk.Toplevel()
    help_window.title('Instructions')
    help_text = scrolledtext.ScrolledText(help_window, width=100, height=100)
    help_text.insert(tk.INSERT, 'File Functions:\n \
                     -------------\n \
                     Open .JPEG file: opens a single a .jpg file from a directory. After opening the file, you can then create a mask of the plastron.\n \
                     Open .NEF File: same as the above function, for a single .nef files.\n \
                     Process .NEF files: takes an entire directory of nef files, converts them into .jpg files and gets their assocated mask image. \
                     Start by selecting the folder with the nef files and then the folder where you want to put the newly created .jpgs and masks.')
    help_text.configure(state='disabled')
    help_text.pack()
    
    help_window.mainloop() """
   

label_selected_image_name = tk.Label(window, text='', padx=5, pady=5)
label_selected_image_name.grid(row=2)    

#---All menu and interface buttons---#
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="Open .JPG File", command=open_file_dialog)
file_menu.add_command(label='Open .NEF File', command=open_nef_dialog)
file_menu.add_command(label='Process .NEF Files', command=load_NEF_files)
file_menu.add_command(label='Process .JPG Files', command=load_JPEG_files)
file_menu.add_command(label='Load Directory', command=file_function_load_directory)
file_menu.add_command(label="Save Segmentation", command=save_segment)
file_menu.add_command(label='Load Model', command=load_model)
help_menu = tk.Menu(menu_bar, tearoff=False)
#help_menu.add_command(label='Instructions', command=show_help)
menu_bar.add_cascade(label="File", menu=file_menu)
#menu_bar.add_cascade(label='Help', menu=help_menu)

#File menu functions only become active after loading the model
file_menu.entryconfig(0, state=tk.DISABLED)
file_menu.entryconfig(1, state=tk.DISABLED)
file_menu.entryconfig(2, state=tk.DISABLED)
file_menu.entryconfig(3, state=tk.DISABLED)
file_menu.entryconfig(4, state=tk.DISABLED)
file_menu.entryconfig(5, state=tk.DISABLED)

button_previous_image = tk.Button(window, text='<- Previous', command=display_previous_image, state=tk.DISABLED)
button_previous_image.place(relx=0.4, rely=0.75)

button_next_image = tk.Button(window, text='Next ->', command=display_next_image, state=tk.DISABLED)
button_next_image.place(relx=0.54, rely=0.75)

button_apply_model = tk.Button(window, text='Create Segmentation', command=display_segmentation, state=tk.DISABLED)
button_apply_model.place(relx=0.24, rely=0.83)

button_process_directory = tk.Button(window, text='Load NEF files', command=start_thread_process_raw_images, state=tk.DISABLED)
button_process_directory.place(relx=0.4, rely=0.83)

button_process_jpeg_directory = tk.Button(window, text='Load JPEG files', command=start_thread_for_process_JPEG_files, state=tk.DISABLED)
button_process_jpeg_directory.place(relx=0.51, rely=0.83)

button_merge_images = tk.Button(window, text="Display Merged", command=merge_images, state=tk.DISABLED)
button_merge_images.place(relx=0.64, rely=0.83)

button_pick_new_segmentation = tk.Button(window, text='Try Different Segmentation', command=pick_new_segmentation)

button_save_segmented_area =  tk.Button(window, text='Save Segmented Area', command=get_segmented_area, state=tk.DISABLED)
button_save_segmented_area.place(relx=0.64, rely=0.75)

window.config(menu=menu_bar)
window.mainloop()

