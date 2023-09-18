import cv2
import numpy as np
import os
from pathlib import Path
import shutil
import secrets
import string
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen

import pkg_resources

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string


def build(image_file_paths, feature_names):
    ensure_required_directories_existis()
    current_index = 0
    folder_name = generate_random_string(10)  
    directory_name = f'images/{folder_name}' 
    image_path = pkg_resources.resource_filename('video_images_creator', "builderbackground.png") 
    bg_img = cv2.imread(image_path)
    ending_page_image_path = pkg_resources.resource_filename('video_images_creator', "closingframe_f.png") 
    ending_page_image = cv2.imread(ending_page_image_path) 
    os.mkdir(directory_name)
    for index in range(len(image_file_paths) - 1):
        if index % 2 == 0:
            current_index = create_right_to_left_movement(image_file_paths[index + 1], image_file_paths[index], current_index, directory_name, feature_names[index], feature_names[index + 1], bg_img) 
        else:
            current_index = create_left_to_right_movement(image_file_paths[index], image_file_paths[index + 1], current_index, directory_name, feature_names[index], feature_names[index+1], bg_img) 

    create_ending_frames(current_index, directory_name, ending_page_image)
    run_ffmpeg(directory_name, folder_name) 
    return flush_video_images(directory_name, folder_name)
   

def create_ending_frames(current_index, directory_name, ending_page_image):
    for i in range(110): 
        index = current_index + i
        destination = f'{directory_name}/frame_{index}.jpg'
        #shutil.copyfile(img1, destination)
        cv2.imwrite(destination, ending_page_image)


def create_left_to_right_movement(left_image_file_path, right_image_file_path, current_index_, directory_name, left_screen_name, right_screen_name, bg_img):

    #create images  

    left_image_file_name = left_image_file_path
    right_image_file_name = right_image_file_path

    parent_current_index = current_index_
    left_image = build_screen_optimised(left_image_file_name, f'{directory_name}/combined_left_image_{current_index_}.jpg', 400, "", False,'left')
    right_image = build_screen_optimised(right_image_file_name, f'{directory_name}/combined_right_image_{current_index_}.jpg', 1375, "", False, 'right')  


    put_text(f'{directory_name}/combined_left_image_with_name_{current_index_}.jpg', left_image, left_screen_name, 400)
    put_text(f'{directory_name}/combined_right_image_with_name_{current_index_}.jpg', right_image, right_screen_name, 1375)




    img1 = cv2.imread(left_image)
    img2 = cv2.imread(right_image) 

    #bg_img = read_image("https://builderbuckets.blob.core.windows.net/builder-now-beta/builderbackground.png")





    #these are for feature transitions 
    start_point = np.array([400, 135])  
    end_point = np.array([1375, 135])   


    obj_width = 305
    obj_height = 636 


    #  #create 40 copies of image with names
    # current_index = current_index_

    # file_name =  f'combined_left_image_with_name${parent_current_index}.jpg'
    # for i in range(40): 
    #     index = i + current_index_
    #     destination = f'./images/frame_{index}.jpg'
    #     shutil.copyfile(file_name, destination)
    #     current_index = current_index + 1



    #create 20 copies of image without names
    current_index = current_index_

    #create 20 copies of img1

    file_name = f'{directory_name}/combined_left_image_{parent_current_index}.jpg'
    for i in range(20): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination)
        current_index = current_index + 1

    num_frames = 70 



    temp_current_index = current_index

    for i in range(num_frames):
        t = i / float(num_frames)  

        
        position = (1 - t) * start_point + t * end_point  

        
        img = bg_img.copy()

        
        box1 = img1[int(start_point[1]):int(start_point[1] + obj_height), int(start_point[0]):int(start_point[0] + obj_width)]
        box2 = img2[int(end_point[1]):int(end_point[1] + obj_height), int(end_point[0]):int(end_point[0] + obj_width)]

        
        transition_obj = (1 - t) * box1 + t * box2

        
        img[int(position[1]):int(position[1] + obj_height), int(position[0]):int(position[0] + obj_width)] = transition_obj

        #frame_index = 76 + i + 2 

        frame_index = temp_current_index + i 
        
        cv2.imwrite(f'{directory_name}/frame_{frame_index}.jpg', img)  

        current_index = current_index + 1



    #create 20 copies of imgage without name

    current_index_ = current_index

    file_name =  f'{directory_name}/combined_right_image_{parent_current_index}.jpg'
    for i in range(20): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination) 
        current_index = current_index + 1

    current_index_ = current_index

    file_name =  f'{directory_name}/combined_right_image_with_name_{parent_current_index}.jpg'
    for i in range(40): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination)
        current_index = current_index + 1

   

   

    return current_index






def create_right_to_left_movement(left_image_file_path, right_image_file_path, current_index_, directory_name, right_screen_name, left_screen_name, bg_img):
    #create images
    left_image_file_name = left_image_file_path
    right_image_file_name = right_image_file_path

    parent_current_index = current_index_

    #images with no feature name
    left_image = build_screen_optimised(left_image_file_name, f'{directory_name}/combined_left_image_{current_index_}.jpg', 400, "", False, 'left')
    right_image = build_screen_optimised(right_image_file_name, f'{directory_name}/combined_right_image_{current_index_}.jpg', 1375, "", False, 'right') 

    #images with feature names
    put_text(f'{directory_name}/combined_left_image_with_name_{current_index_}.jpg', left_image, left_screen_name, 400) 
    put_text(f'{directory_name}/combined_right_image_with_name_{current_index_}.jpg', right_image, right_screen_name, 1375) 


    img1 = cv2.imread(left_image)
    img2 = cv2.imread(right_image) 

    #bg_img = read_image("https://builderbuckets.blob.core.windows.net/builder-now-beta/builderbackground.png")

    #these are for feature transitions 
    start_point = np.array([1375, 135])  
    end_point = np.array([400, 135])


    obj_width = 305
    obj_height = 636


    #create 40 copies of image with names
    current_index = current_index_

    file_name =  f'{directory_name}/combined_right_image_with_name_{parent_current_index}.jpg'
    for i in range(40): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination)
        current_index = current_index + 1



    #create 20 copies of image without names
    current_index_ = current_index
    file_name =  f'{directory_name}/combined_right_image_{parent_current_index}.jpg'
    for i in range(20): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination)
        current_index = current_index + 1

    num_frames = 70 



    temp_current_index = current_index

    for i in range(0,num_frames):
        t = i / float(num_frames)  
        
        # Get current position 
        position = (1 - t) * start_point + t * end_point  
        
        # Create a copy of the background
        img = bg_img.copy()

        # Define object from img2
        box1 = img2[int(start_point[1]):int(start_point[1] + obj_height), int(start_point[0]):int(start_point[0] + obj_width)]
        # Define object from img1
        box2 = img1[int(end_point[1]):int(end_point[1] + obj_height), int(end_point[0]):int(end_point[0] + obj_width)]
        
        # If the transition is at the start, take the object from img2, otherwise take it from img1
        # if t <= 0.5:
        #     transition_obj = box1
        # else:
        #     transition_obj = box2

        transition_obj = (1 - t) * box1 + t * box2
        
        # Add object to the current image
        img[int(position[1]):int(position[1] + obj_height), int(position[0]):int(position[0] + obj_width)] = transition_obj

        #frame_index = 76 + i + 2 

        frame_index = temp_current_index + i 
        
        cv2.imwrite(f'{directory_name}/frame_{frame_index}.jpg', img)  

        current_index = current_index + 1



    current_index_ = current_index

    #create 25 copies of imgage without names

    file_name = f'{directory_name}/combined_left_image_{parent_current_index}.jpg'
    for i in range(25): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination) 
        current_index = current_index + 1



    #create 40 copies of image with names
    current_index_ = current_index

    file_name =  f'{directory_name}/combined_left_image_with_name_{parent_current_index}.jpg'
    for i in range(40): 
        index = i + current_index_
        destination = f'{directory_name}/frame_{index}.jpg'
        shutil.copyfile(file_name, destination)
        current_index = current_index + 1


    
  
    


   

    return current_index

def refined_alpha_blend(roi, overlay):
    # Extract the alpha channel and normalize it
    alpha = overlay[:, :, 3] / 255.0
    inverse_alpha = 1.0 - alpha

    # Ensure both images have 4 channels
    if roi.shape[2] == 3:
        roi = np.dstack([roi, np.ones((roi.shape[0], roi.shape[1]), dtype="uint8") * 255])

    # Premultiply RGB channels with the alpha
    overlay_premul = overlay.copy()
    roi_premul = roi.copy()
    for c in range(3):
        overlay_premul[:, :, c] = overlay_premul[:, :, c] * alpha
        roi_premul[:, :, c] = roi_premul[:, :, c] * inverse_alpha

    # Blend the premultiplied images
    blended = overlay_premul + roi_premul
    blended[:, :, 3] = overlay[:, :, 3]  # Set the alpha channel

    return blended

def get_rounded_image(image, mask):
    # Separate the color and alpha channels from the mask
    mask_color = mask[:, :, :3]
    mask_alpha = mask[:, :, 3] if mask.shape[2] == 4 else None

    # Apply the mask to get the rounded image
    rounded_img = cv2.bitwise_and(image, mask_color)
    
    # If the image doesn't already have an alpha channel, add one
    if image.shape[2] == 3:
        rounded_img = np.dstack([rounded_img, mask_alpha if mask_alpha is not None else mask_color[:, :, 0]])
    
    return rounded_img



def create_rounded_mask(image, corner_radius):
    mask = np.zeros_like(image)
    
    # Draw 4 ellipses at the corners to make them rounded
    cv2.ellipse(mask, (corner_radius, corner_radius), (corner_radius, corner_radius), 180, 0, 90, (255,255,255), -1)
    cv2.ellipse(mask, (image.shape[1] - corner_radius, corner_radius), (corner_radius, corner_radius), 270, 0, 90, (255,255,255), -1)
    cv2.ellipse(mask, (corner_radius, image.shape[0] - corner_radius), (corner_radius, corner_radius), 90, 0, 90, (255,255,255), -1)
    cv2.ellipse(mask, (image.shape[1] - corner_radius, image.shape[0] - corner_radius), (corner_radius, corner_radius), 0, 0, 90, (255,255,255), -1)
    
    # Draw the rectangles to fill the interior parts
    cv2.rectangle(mask, (corner_radius, 0), (image.shape[1] - corner_radius, image.shape[0]), (255, 255, 255), -1)
    cv2.rectangle(mask, (0, corner_radius), (image.shape[1], image.shape[0] - corner_radius), (255, 255, 255), -1)
    
    return mask


def build_screen(screen_file, combine_file_name, x_coordinate, sceen_name, text_to_be_added):

    # Load the images
    background = read_image("https://builderbuckets.blob.core.windows.net/builder-now-beta/builderbackground.png")
    overlay = read_image(screen_file)
    mobile = read_image("https://builderbuckets.blob.core.windows.net/builder-now-beta/310x640-with-border-radius.png")

    # Resize overlay to fit inside the mobile screen
    # Assuming the visible screen area dimensions are (280, 520) for the mobile image
    screen_width, screen_height = 284, 609
    overlay = cv2.resize(overlay, (screen_width, screen_height))
    
    # Ensure mobile has an alpha channel
    if mobile.shape[2] < 4:
        mobile = np.dstack([mobile, np.ones((mobile.shape[0], mobile.shape[1]), dtype="uint8") * 255])

    # Overlay the mobile image onto the background
    m_x, m_y, m_w, m_h = x_coordinate, 135, mobile.shape[1], mobile.shape[0]
    roi = background[m_y:m_y+m_h, m_x:m_x+m_w]
    img_blend = cv2.addWeighted(roi, 1, mobile[:, :, 0:3], 1, 0)
    background[m_y:m_y+m_h, m_x:m_x+m_w, 0:3] = img_blend * (mobile[:, :, 3:] / 255.0) + background[m_y:m_y+m_h, m_x:m_x+m_w, 0:3] * (1 - mobile[:, :, 3:] / 255.0)
    
    # Overlay the screen onto the background
    # Assuming the top-left corner of the visible screen area is at position (15, 60) for the mobile image 

    corner_radius = 30
    mask = create_rounded_mask(overlay, corner_radius)

    # Generate the rounded image
    rounded_image = get_rounded_image(overlay, mask) 

    x, y = x_coordinate + 13, 135 + 15
    h_o, w_o, _ = rounded_image.shape  

    # Overlay the rounded image onto the background
    m_x, m_y, m_w, m_h = x_coordinate, 135, rounded_image.shape[1], rounded_image.shape[0]  

    if rounded_image.shape[2] < 4:
        rounded_image = np.dstack([rounded_image, np.ones((rounded_image.shape[0], rounded_image.shape[1]), dtype="uint8") * 255])


    roi = background[y:y+h_o, x:x+w_o]  

    alpha = rounded_image[:, :, 3] / 255.0
    inverse_alpha = 1.0 - alpha  


    blended_roi = refined_alpha_blend(background[y:y+h_o, x:x+w_o], rounded_image)
    background[y:y+h_o, x:x+w_o] = blended_roi[:, :, :3]  # Only take BGR channels, ignore alpha


    if text_to_be_added:
        # Convert OpenCV image to Pillow format
        pil_image = Image.fromarray(cv2.cvtColor(background, cv2.COLOR_BGR2RGB))
        
        # Load the custom font
        font_path = pkg_resources.resource_filename('video_images_creator', 'Rubik-Medium.ttf')
        font_size = 47
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(pil_image)
        
        max_width = 400  # The maximum width for text
        lines = []
        words = sceen_name.split()
        while words:
            line = ''
            while words and int(draw.textlength(line + words[0], font=font)) <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)
        
        # Limit to 3 lines
        lines = lines[:3]
        
        y = background.shape[0] - 600
        for i, line in enumerate(lines):
            if x_coordinate == 400:
                x = x_coordinate + 350
            else:
                x = x_coordinate - 400  
            draw.text((x, y + i*font_size), line.strip(), font=font, fill=(255, 255, 255))

        background = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Save and return the modified image
    cv2.imwrite(combine_file_name, background)
    return combine_file_name


def build_screen_optimised(screen_file, combine_file_name, x_coordinate, sceen_name, text_to_be_added, position):
    overlay = read_image(screen_file) 
    screen_width, screen_height = 284, 609
    x, y = x_coordinate + 13, 135 + 15
   
    overlay = cv2.resize(overlay, (screen_width, screen_height))

    if position == 'left': 
        image_path = pkg_resources.resource_filename('video_images_creator', "combined_left.jpg")
        background = cv2.imread(image_path) 
    else:
        image_path = pkg_resources.resource_filename('video_images_creator', "combined_right.jpg")
        background = cv2.imread(image_path)

    corner_radius = 30
    mask = create_rounded_mask(overlay, corner_radius)

    # Generate the rounded image
    rounded_image = get_rounded_image(overlay, mask)
    h_o, w_o, _ = rounded_image.shape 
    blended_roi = refined_alpha_blend(background[y:y+h_o, x:x+w_o], rounded_image)
    background[y:y+h_o, x:x+w_o] = blended_roi[:, :, :3]  # Only take BGR channels, ignore alpha 

    cv2.imwrite(combine_file_name, background)

    return combine_file_name

def put_text(combine_file_name, background, sceen_name, x_coordinate): 
    background = cv2.imread(background)
    pil_image = Image.fromarray(cv2.cvtColor(background, cv2.COLOR_BGR2RGB))
        
    # Load the custom font
    font_path = pkg_resources.resource_filename('video_images_creator', 'Rubik-Medium.ttf')
    #font_path = 'features/Rubik-Medium.ttf'
    font_size = 47
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(pil_image)
    
    max_width = 400  # The maximum width for text
    lines = []
    words = sceen_name.split()
    while words:
        line = ''
        while words and int(draw.textlength(line + words[0], font=font)) <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line)
    
    # Limit to 3 lines
    lines = lines[:3]
    
    y = background.shape[0] - 600
    for i, line in enumerate(lines):
        if x_coordinate == 400:
            x = x_coordinate + 350
        else:
            x = x_coordinate - 450 
        draw.text((x, y + i*font_size), line.strip(), font=font, fill=(255, 255, 255))

    background = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Save and return the modified image
    cv2.imwrite(combine_file_name, background)

def run_ffmpeg(directory_name, uniq_code):
    audio_path = pkg_resources.resource_filename('video_images_creator', 'video-music.wav')
    os.system(f"ffmpeg -y -framerate 60 -i {directory_name}/frame_%d.jpg -i {audio_path} -c:v libx264 -crf 18 -pix_fmt yuv420p -r 60 -c:a aac -strict experimental -shortest outputs/output_{uniq_code}.mp4")
    

def flush_video_images(diretory_name, folder_name):
    try:
        # Use shutil.rmtree() to remove the entire folder and its contents
        shutil.rmtree(diretory_name)
        #print(f"Folder '{diretory_name}' and its contents have been deleted.")
        return f"outputs/output_{folder_name}.mp4"
    except Exception as e:
        #print(f"An error occurred: {e}")
        return f"outputs/output_{folder_name}.mp4"

def read_image(image_url):
    resp = urlopen(image_url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR) # The image object
    return image 

def ensure_required_directories_existis():
    if not os.path.exists("images"):
        try:
            os.mkdir("images") 
        except Exception as e:
            print("Exception occured", e) 
    if not os.path.exists("outputs"):
        try:
            os.mkdir("outputs")
        except Exception as e:
            print("Exception occured..", e)


if __name__ == "__main__":
    image_file_paths = ["video_images_creator/features/launch.png", "video_images_creator/features/first.png","video_images_creator/features/second.png", "video_images_creator/features/third.png", "video_images_creator/features/fourth.png", "video_images_creator/features/fifth.png"] 
    feature_names = ["Splash Screen", "Search", "Dashboard", "Settings", "Profile/Bio", "Analytics" ]
    #image_file_paths = ["video_images_creator/features/launch.png", "video_images_creator/features/first.png", "video_images_creator/features/second.png"]

    build(image_file_paths, feature_names) 


