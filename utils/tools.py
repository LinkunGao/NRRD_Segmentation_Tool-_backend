import os
import json
import time

MASKS = None
FILE_PATH = ""

def check_file_exist(directory, filename):
    cwd = os.getcwd()
    filepath = os.path.join(cwd, 'import_nrrd', directory, filename)
    if os.path.exists(filepath):
        return True
    else:
        return False


def get_real_path(directory, subdirectory, filename):
    cwd = os.getcwd()
    filepath = os.path.join(cwd, directory, subdirectory, filename)
    if os.path.exists(filepath):
        return filepath
    else:
        return ''


def get_all_folder_names(directory, subdirectory=""):
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, directory, subdirectory)
    folder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    return folder_names


def get_all_file_names(directory, subdirectory=""):
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, directory, subdirectory)
    items = os.listdir(folder_path)
    for item in items:
        if ('.nrrd' not in item) and ('.json' not in item):
            items.remove(item)

    file_names = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
    sorted_files_names = sorted(file_names)
    return sorted_files_names

def write_data_to_json(directory,subdirectory,masks):
    global MASKS
    global FILE_PATH
    start_time = time.time()
    cwd = os.getcwd()
    file_path = os.path.join(cwd, directory, subdirectory, "mask.json")
    # for mask in masks:
    #     base = mask["width"]*mask["height"]*4
    #     mask["data"] = [0] * base
    # with open(file_path, "w") as file:
    #     json.dump(masks, file)
    FILE_PATH = file_path
    MASKS = masks
    saveMaskData()
    end_time = time.time()
    run_time = end_time - start_time
    # print("代码运行时间为：{:.2f}秒".format(run_time))

def replace_data_to_json(directory,subdirectory,slice):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, directory, subdirectory, "mask.json")
    index = slice.sliceId
    if os.path.isfile(file_path):
        # Open the JSON file in read mode
        # with open(file_path, 'r') as f:
        #     # Load the JSON data from the file into a Python object
        #     masks = json.load(f)
        masks = getMaskData(file_path)
        masks[index]["data"] = slice.mask
        # with open(file_path, "w") as file:
        #     json.dump(masks, file)


def getMaskData(path):
    global MASKS
    global FILE_PATH
    FILE_PATH = path
    if MASKS is None:
        with open(path, 'r') as f:
            # Load the JSON data from the file into a Python object
            MASKS = json.load(f)
    return MASKS

def saveMaskData():
    global MASKS
    global FILE_PATH
    with open(FILE_PATH, "w") as file:
        json.dump(MASKS, file)
    MASKS = None