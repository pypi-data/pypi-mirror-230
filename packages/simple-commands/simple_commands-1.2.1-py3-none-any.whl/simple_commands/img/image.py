from PIL.Image import open as op
import numpy as np
import cv2
import os
import random as rd

def load_images(image_path):
    return np.array(op(image_path))

def gray_image(image, path=None, name=None):
    if path is not None:
        os.makedirs(path, exist_ok=True)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if name is not None:
        if path is not None:
            file_path = os.path.join(path, f"{name}.jpg")
        else:
            file_path = f"{name}.jpg"
        cv2.imwrite(file_path, gray_image)
    
    return gray_image if name is None else None


def new_data_image(image_path, output_dir, base_name=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image = cv2.imread(image_path)
    rotated_images = [
        image,
        cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
        cv2.rotate(image, cv2.ROTATE_180),
        cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    ]
    list_img = [] 
    if base_name is not None:
        for rot_idx, rotated_image in enumerate(rotated_images):
            file_name = f"{base_name}_{rot_idx}.jpg"
            file_path = os.path.join(output_dir, file_name)
            cv2.imwrite(file_path, rotated_image)
    else:
        for rot_idx, rotated_image in enumerate(rotated_images):     
          list_img.append(rotated_image) 
        return list_img
def use_PIL(image):
    return Image.fromarray(image)




def show(name, image, waitKey='q'):
    cv2.imshow(name, image)
    print(f"Image opened successfully")
    while True:
        if cv2.waitKey(1) & 0xFF == ord(waitKey):
            break
    # ปิดหน้าต่าง
    cv2.destroyAllWindows()
    print(f"closed image successfully")
    return

def adjust_img_color(image, number_new=1, color_value=0.5, color_value_end=1.5):
    list_img = []
    for _ in range(number_new+1):
        number = rd.uniform(color_value, color_value_end)
        if number != 1:
            list_img.append(cv2.convertScaleAbs(image, alpha=number))
    return list_img

def resize(image, size):
    return cv2.resize(image, size)