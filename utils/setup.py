from pathlib import Path
from dotenv import load_dotenv
import os


def get_base_from_env():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    return os.environ["BASE"]

class Config:
    MASKS = None
    METADATA = None
    Connected_Websocket = None
    Updated_Mesh = False
    ClearAllMask = False
    Current_Case_Name = ""
    BASE_PATH = Path(get_base_from_env())
    METADATA_PATH = "./manifest.xlsx"
    MASK_FILE_PATH = ""
    MASK_FOLDER_PATH = ""
    IMPORT_FOLDER_PATH = "import_nrrd"
    EXPORT_FOLDER_PATH = "export_data"
    CASE_NAMES = []


