import json
import time
import pandas as pd
from .setup import Config


def get_metadata():
    """
    :return: df format metadata
    """
    metadata_path = Config.BASE_PATH / Config.METADATA_PATH
    if metadata_path.is_file() and metadata_path.suffix == ".xlsx":
        Config.METADATA = pd.read_excel(metadata_path, sheet_name="Sheet1")


def get_all_case_names():
    """
    :return: get each case name, the patient id for user to switch cases
    """
    if Config.METADATA is not None:
        case_names = list(set(Config.METADATA["patient_id"]))
        Config.CASE_NAMES = case_names
        return case_names
    return []


def check_file_exist(patient_id, filetype, filename):
    """
    :param patient_id: case name
    :param filename: mask.json mask.obj
    :return: if there is a mask.json file return true, else create a mask.json and return false
    """
    file_path = get_file_path(patient_id, filetype, filename)
    if file_path != "":
        if filetype == "json":
            # Create the directory and all parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.name != filename:
                new_file_path = file_path.parent / filename
                new_file_path.touch()
            else:
                if file_path.exists():
                    return True
                else:
                    file_path.touch()
        else:
            return file_path.exists()
    return False


def write_data_to_json(patient_id, masks):
    # todo 1: find mask.json path base on patient_id
    mask_json_path = get_file_path(patient_id, "json", "mask.json")
    Config.MASK_FOLDER_PATH = mask_json_path.parent
    Config.MASK_FILE_PATH = mask_json_path
    Config.MASKS = masks
    saveMaskData()


def get_file_path(patient_id, file_type, file_name):
    """
    :param patient_id: case name
    :param file_type: json, nrrd, nii
    :return: file full path via pathlib
    """
    if Config.METADATA is not None:
        file_df = Config.METADATA[
            (Config.METADATA["patient_id"] == patient_id) & (Config.METADATA["file type"] == file_type)]
        # index = mask_json_df.index.tolist()
        # path = mask_json_df.loc[index[0], 'filename']
        paths = list(file_df['filename'])
        new_paths = []
        for path in paths:
            new_paths.append(Config.BASE_PATH / path)
        file_path_arr = [path for path in new_paths if path.name==file_name]
        if len(file_path_arr) >0:
            file_path_full = file_path_arr[0]
            return file_path_full
    return ""

def replace_data_to_json(patient_id, slice):
    """
    :param patient_id: case name
    :param slice: a single slice mask pixels
    """
    mask_json_path = get_file_path(patient_id, "json", "mask.json")
    index = slice.sliceId
    label = slice.label
    if Config.MASKS == None:
        if mask_json_path.is_file():
            getMaskData(mask_json_path)

    Config.MASKS[label][index]["data"] = slice.mask
    Config.MASKS["hasData"] = True



def getMaskData(path):
    """
    :param path: A mask.json file full path
    :return:
    """
    Config.MASK_FILE_PATH = path
    if Config.MASKS is None:
        with open(path, 'rb') as file:
            # Load the JSON data from the file into a Python object
            Config.MASKS = json.loads(file.read().decode('utf-8'))
    return Config.MASKS


def saveMaskData():
    """
    save mask.json to local drive
    """
    if Config.MASK_FILE_PATH != "":
        with open(Config.MASK_FILE_PATH, "wb") as file:
            # json.dump(MASKS, file)
            file.write(json.dumps(Config.MASKS).encode('utf-8'))
        Config.MASKS = None


def save():
    start_time = time.time()
    if Config.MASKS is not None:
        saveMaskData()
    end_time = time.time()
    run_time = end_time - start_time
    print("save json cost：{:.2f}s".format(run_time))
