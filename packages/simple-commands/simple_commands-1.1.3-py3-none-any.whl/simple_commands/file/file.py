import numpy as np
import os
from tqdm import tqdm
import shutil

def main_folder(main_folder_path,file_type=None):
    list_data = []
    if file_type == 'img':
        file_type = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg')
    paths = os.scandir(main_folder_path)
    for path in tqdm(paths, desc='Processing', unit='Folder', ncols=50):
        if path.is_dir():
            path1 = os.path.join(main_folder_path, path)
            path_folder = os.scandir(path1)
            for p in path_folder:
                if p.is_file and file_type == None:
                    list_data.append(p.path)
                elif p.is_file and p.name.endswith(file_type):
                    list_data.append(p.path)
    return list_data


def folder_file(path, file_type=None):

    list_file = []

    if file_type == '.img':
        file_type = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg')
    p = os.scandir(path)
    for pa in p:
        if file_type == None and pa.is_file: 
            list_file.append(pa.path)
        elif pa.is_file and pa.name.endswith(file_type):    
            list_file.append(pa.path)
    return list_file


def list_files_in_current_directory():
    return os.listdir()

def create_new_directory(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Created directory: {directory_name}")
    except FileExistsError:
        print(f"Directory {directory_name} already exists.")

def move_file(source_path, destination_path):
    try:
        shutil.move(source_path, destination_path)
        print(f"Moved {source_path} to {destination_path}")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_directory(directory_path):
    try:
        shutil.rmtree(directory_path)
        print(f"Deleted directory: {directory_path}")
    except FileNotFoundError:
        print("Directory not found.")
    except Exception as e:
        print(f"An error occurred: {e}")