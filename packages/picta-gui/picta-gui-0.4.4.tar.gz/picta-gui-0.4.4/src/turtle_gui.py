import os
import rawpy
import tempfile
import threading
import tkinter as tk
import tensorflow as tf
import numpy as np
from src.genau_image_tools.imagetransforms import apply_model_to_image, convert_image_into_tensor_and_apply_model, copy_single_segment_to_canvas
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image


window = tk.Tk()
window.title("Apply Model to Image")
window.geometry("1400x750")


"""
The following variables are used as global variables:
    model (keras model) : the model used for creating plastron segmentations
    fname (String) : the filename of the jpeg being displayed. Used in both label_selected_image_name and for naming purposes in saving segmentations.
    file_path (String) : the path to the displayed image
    segment_image (PIL.Image) : the png segment image loaded into a PIL.Image object
    og_image (PIL.Image) : the original jpeg image loaded into a PIL.Image object
    og_image_display (tk.Label) : label used for displaying the original jpeg
    segment_display (tk.Label) : same as og_image_display but for the generated segment image
    merged_image_display (tk.Label) : used for displaying the 'blended' image of the segmentation image over the original image
    not_merged (boolean) : used for determining if the 'blended' image is currently being displayed.
    no_segment_loaded (boolean) : primarily used for in processing a single image. Stops the user from trying to use File -> Save Segment without first generating a segmentation image
    jpeg_list (list) : used for loading, displaying, and navigating through a directory of jpeg images. Contains a list of strings associated with the files in a directory.
    png_list (list) : same as jpeg_list, just for segmentation images.
    index_of_image_lists (int) : used for navigating through jpeg_list and png_list. Increments when displaying the next image, decrements when displaying the previous image.
    input_directory (String) : path to where the opened directory of images is.
    output_directory (String) : path where to save segmentation images to.
    cancel_image_process (boolean) : used as a flag to stop the routine of applying the model to the nefs or jpegs in a directory.
"""
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

#Temporary directory for use with loading single NEF files
temp_dir = tempfile.TemporaryDirectory()

#Label that displays the currently loaded image
label_selected_image_name = tk.Label(window, text='', padx=5, pady=5)
label_selected_image_name.grid(row=2)    

def load_model():
    #Functionality for File -> Load Model. Loads the keras model into the program and enables the rest of the program's functionality.
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
    #Functionality for File -> Open .JPG File. Loads a single jpeg image into the program and enables functionality to generate a segment image
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
    #Functionality for File -> Open .NEF File. Loads a single nef file into the program by converting into a jpeg image, saving the jpeg into the temp_dir, and then displaying said jpeg. 
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
    #Functionality for button_apply_model. Applies the model to the image, and displays the segmentation.
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
    button_pick_new_segmentation.grid(row=2, column= 1)
    button_pick_new_segmentation['state'] = tk.ACTIVE

def merge_images():
    #Functionality for button_merge_images. Overlays the segmentation image over the original image through the use of PIL Image.blend()
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
    #Functionality for File -> Save Segmentation. Saves the currently displayed segmentation image to the chosen directory.
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
    #Removes the labels containing images and sets the screen back to a neutral state
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
    #Used for displaying both the image and mask from the loaded directory
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

def __pick_input_and_output_directory(file_type):
    """Used for getting the the directory of NEF files to process, and where to save the generated segmentation images.
    Inputs:
        file_type (String) : indicates whether jpegs or nefs are being dealt with
    Returns:
        input_directory (String) : the path to the directory with the nef images.
        output_directory (String) : the path to the directory to save the segmentation images.
    """
    if file_type == 'nef':
        messagebox.showinfo('Instructions', 'Select the folder with your raw image .NEF files')
    else:
        messagebox.showinfo('Instructions', 'Select the folder with your .jpg image files')
    input_directory = filedialog.askdirectory()  
    if input_directory:
        if file_type == 'nef':
            messagebox.showinfo('Instructions', 'Select which folder to output the generated JPEGs and masks')
            output_directory = filedialog.askdirectory()
            if output_directory:
                return input_directory, output_directory
        else:
            output_directory = input_directory
            return input_directory, output_directory
     

def load_files(file_type):
    """Functionality for File -> Process .NEF Files and File -> Procress .JPEG Files. Let's the user pick which directories to load the NEF files and subsequently where to save the segmentation images to.
    Inputs:
        file_type (string) : indicates whether loading jpegs or nefs
    """
    __clear_screen()
    global input_directory
    global output_directory
    try:
        input_directory, output_directory = __pick_input_and_output_directory(file_type)
        if file_type == 'nef':
            button_process_nef_directory['state'] = tk.ACTIVE
            label_selected_image_name.config(text='Next click the \"Load NEF files\" button', font=('', '15'))
        else:
            button_process_jpeg_directory['state'] = tk.ACTIVE
            label_selected_image_name.config(text='Next click the \"Load JPEG files\" button', font=('', '15'))
    except:
        print('Yeah it messed up')
        label_selected_image_name.config(text='Error when picking directories, try again.', font=('', '15'))
        button_process_nef_directory['state'] = tk.DISABLED
        button_process_jpeg_directory['state'] = tk.DISABLED

def cancel_process_image():
    #Functionality for stop_button. Signals to stop the thread procesing the images.
    global cancel_image_process
    cancel_image_process = True

def start_thread_for_process_JPEG_files():
    #Seperate thread for function process_JPEG_files so it can be cancelled by clicking stop_button
    t1 = threading.Thread(target=process_JPEG_files)
    t1.start()

def process_JPEG_files():
    #Functionality for button_process_jpeg_directory. Takes all jpegs from input_directory, produces and saves a segmentation, and then displays the image and segmentation.
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
            if '.jpg' in jpg_files[i] and not '_segmented' in jpg_files[i]:
                base_filename = os.path.splitext(jpg_files[i])[0]
                mask_png = apply_model_to_image(model, 128, os.path.join(input_directory, base_filename+'.jpg'))
                mask_png.save(os.path.join(output_directory, base_filename+'_masked.png'), 'PNG') #Second arg of 'PNG' ensures image will be saved with PNG encoding
                progress_var.set((i + 1) * 100 / len(jpg_files))
                window.update_idletasks()
        except:
            print('Invalid file found, skipping.')
    progress_bar.place_forget()
    stop_button.place_forget()
    messagebox.showinfo('Info', 'Wrote ' + str(i*2) + ' files to ' + output_directory)
    load_directory(input_directory)
    __display_image_and_mask()
    button_next_image['state'] = tk.ACTIVE
    button_process_jpeg_directory['state'] = tk.DISABLED
    button_merge_images['state'] = tk.ACTIVE 


def start_thread_process_raw_images():
    #Seperate thread for function process_raw_images so it can be cancelled by clicking stop_button
    t1 = threading.Thread(target=process_raw_images)
    t1.start()

def process_raw_images():
    #Functionality for button_process_nef_directory. Takes all NEF files from the input_directory list, converts them into jpegs, applies the model, saves the segmentation, then displays the assocaited images.
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
    messagebox.showinfo('Info', 'Wrote ' + str(i*2) + ' files to ' + output_directory)
    load_directory(output_directory)
    __display_image_and_mask()
    button_next_image['state'] = tk.ACTIVE
    button_process_nef_directory['state'] = tk.DISABLED
    button_merge_images['state'] = tk.ACTIVE   

def load_directory(path):
    """Adds all images in the given path to jpeg_list and png_list. Assumes the original image and its associated segmentation image are in the same directory.
    Inputs:
        path (String) : path to the directory containing the images to be displayed
    """
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
    #Functionality for File -> Load Directory. Takes a directory of already processed images and loads them into the program.
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
    #Functionality for button_previous_image. Decrements the position of index_of_image_lists if possible, then displays displays image and mask
    
    global index_of_image_lists
    button_next_image['state'] = tk.NORMAL
    if index_of_image_lists == 0:
        button_previous_image['state'] = tk.DISABLED
        return
    button_previous_image['state'] = tk.NORMAL
    index_of_image_lists -= 1
    __display_image_and_mask()

def display_next_image():
    #Functionality for button_next_image. Increments the position of index_of_image_lists if possible, then displays displays image and mask
    global index_of_image_lists
    index_of_image_lists += 1
    button_previous_image['state'] = tk.NORMAL
    if index_of_image_lists >= len(jpeg_list):
        button_next_image['state'] = tk.DISABLED
        index_of_image_lists -= 1
        return
    button_next_image['state'] = tk.NORMAL 
    __display_image_and_mask()


def pick_new_segmentation():
    #Functionality for button_pick_new_segmentation. Takes the user to a new window displaying three choices of different generated segemntations, created by applying the model to images of the plastron in three different locations. 
    #Allows the user to compare these new choices to the original, and gives the option to overwrite the old segmentation.

    def __get_plastron_distance_from_center(segment_left_or_top, is_horizontal):
        """Used to determine the offset for Segment B (the 'middle' position of the plastron) by checking for the white pixel closest to the center of the plastron, subtracting that distance from 128, and using that calculation as a new offset
        Inputs:
            segment_left_or_top (PIL.Image) : the Segment A ('left or top' most position of the plastron) of the original image
            is_horizontal (boolean) : true if the image width > height, false otherwise. Determines whether to use Left/Right most pixel or Top/Bottom most pixel
        Returns:
            distance (int) : Used for calculating the offset of the 'middle' position of the plastron
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
        """Chops the original image into three 128x128 images.
        Inputs:
            path_to_image(String) : path to the original image being used to create the 3 cropped sections.
        Returns:
            segments_and_offsets (list) : contains the cropped PIL.Image objects followed by its associated offset. Ex: left_or_top at position 0, its offset at position 1
            scaled_image (PIL.Image) : the resized image of the original scaled down to width or height of 128 pixels. Used for keeping image dimensions when resizing to the image's original size
        """
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
        tensor_left_or_top = convert_image_into_tensor_and_apply_model(left_or_top, model)
        segment_left_or_top = tf.keras.utils.array_to_img(tensor_left_or_top)
        middle_offset = __get_plastron_distance_from_center(segment_left_or_top, is_horizontal)
        if is_horizontal:
            middle.paste(scaled_image.crop((middle_offset, 0, 128 + middle_offset, 128 + middle_offset)))
            right_or_bottom.paste(scaled_image.crop((offset, 0, scaled_image.width, scaled_image.height)))
        else:
            middle.paste(scaled_image.crop((0, middle_offset, 128 + middle_offset, 128 + middle_offset)))
            right_or_bottom.paste(scaled_image.crop((0, offset, scaled_image.width, scaled_image.height)))
        tensor_middle = convert_image_into_tensor_and_apply_model(middle, model)
        segment_middle = tf.keras.utils.array_to_img(tensor_middle)
        tensor_right_or_bottom = convert_image_into_tensor_and_apply_model(right_or_bottom, model)
        segement_right_or_bottom = tf.keras.utils.array_to_img(tensor_right_or_bottom) 
        segments_and_offsets = [segment_left_or_top, 0, segment_middle, middle_offset, segement_right_or_bottom, offset] 
        return segments_and_offsets, scaled_image

    def __resize_segment_choices(image):
        """Resizes the three segmentation options to fit on screen
        Inputs:
            image (PIL.Image) : the segmentation to resize
        Returns:
            image (PIL.Image) : the resized segmentation image
        """
        window_width, window_height = window.winfo_width(), window.winfo_height()
        width = int(window_width * 0.15)
        height = int(window_height * 0.25)
        image = image.resize((width, height), Image.BICUBIC)
        return image

    def __resize_segment_to_image_size(segment, offset, scaled_image):
        """Used to resize the segmentation option to the original image size for comparison sake.
        Inputs:
            segment (PIL.Image) : the segment option to resize
            offset (int) : used to ensure the pixel placement in copy_single_segment_to_canvas matches the original image
            scaled_image (PIL.Image) : the original image scaled down. Primarily used to get the dimensions for the 'canvas' to put the segmentation on
        """
        canvas = Image.new("RGB", (scaled_image.width, scaled_image.height))
        if scaled_image.width > scaled_image.height:
            filled_canvas = copy_single_segment_to_canvas(segment, offset, 0, canvas)
        else:
            filled_canvas = copy_single_segment_to_canvas(segment, 0, offset, canvas)
        new_segment = filled_canvas.resize((original_image.width, original_image.height), resample=Image.BOX)
        __compare_new_segment_to_og(new_segment)

    def __redisplay_segment_choices():
        #Functionality for button_see_segment_choices. Redisplays the 3 segment choices
        choice_window.destroy()
        pick_new_segmentation()

    def __show_merged_segments(new_segment):
        #Functionality for button_show_overlay_on_og_image. Allows the user to compare the old segmentation and new segmentation overlayed on the original image
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
        """Functionality for button_overwrite_and_save_new_segment. Saves the new segmentation and overwrites the old one.
        Inputs:
            new_segment (PIL.Image) : the new segmentation to be saved
        """
        segment_path = os.path.join(output_directory, png_list[index_of_image_lists])
        new_segment.save(segment_path)
        choice_window.destroy()
        __display_image_and_mask()

    def __compare_new_segment_to_og(new_segment):
        """Displays the original segmentation and new segmentation side by side for comparison sake.
        Inputs:
            new_segment (PIL.Image) : one of the three new segment choices selected by the user
        """
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
    #Functionality for button_save_segmented_area. Saves the area of the original image that is occupied by the segmentation, then displays the next image in the directory
    global segment_image
    global og_image
    original_image_array = np.array(og_image)
    binary_mask = np.array(segment_image) == 255
    segmented_area = np.zeros_like(original_image_array)
    segmented_area[binary_mask] = original_image_array[binary_mask]
    segmented_image = Image.fromarray(segmented_area)
    base_filename = os.path.splitext(jpeg_list[index_of_image_lists])[0]
    segmented_image.save(os.path.join(output_directory, base_filename+'_segmented.jpg'), 'JPEG')
    display_next_image()


#---All menu and interface buttons---#
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="Open .JPG File", command=open_file_dialog)
file_menu.add_command(label='Open .NEF File', command=open_nef_dialog)
file_menu.add_command(label='Process .NEF Files', command=lambda:load_files('nef'))
file_menu.add_command(label='Process .JPG Files', command=lambda:load_files('jpeg'))
file_menu.add_command(label='Load Directory', command=file_function_load_directory)
file_menu.add_command(label="Save Segmentation", command=save_segment)
file_menu.add_command(label='Load Model', command=load_model)
help_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)

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

button_process_nef_directory = tk.Button(window, text='Load NEF files', command=start_thread_process_raw_images, state=tk.DISABLED)
button_process_nef_directory.place(relx=0.4, rely=0.83)

button_process_jpeg_directory = tk.Button(window, text='Load JPEG files', command=start_thread_for_process_JPEG_files, state=tk.DISABLED)
button_process_jpeg_directory.place(relx=0.51, rely=0.83)

button_merge_images = tk.Button(window, text="Display Merged", command=merge_images, state=tk.DISABLED)
button_merge_images.place(relx=0.64, rely=0.83)

button_pick_new_segmentation = tk.Button(window, text='Try Different Segmentation', command=pick_new_segmentation)

button_save_segmented_area =  tk.Button(window, text='Save Segmented Area', command=get_segmented_area, state=tk.DISABLED)
button_save_segmented_area.place(relx=0.64, rely=0.75)

window.config(menu=menu_bar)
window.mainloop()