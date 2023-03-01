# 进入venv虚拟环境
# terminial-> venv/Scripts/activate.bat
import uvicorn
import time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from zipfile import ZipFile
from utils import check_file_exist, get_real_path, tools
from models import model

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMPORT_FOLDER_PATH = "import_nrrd"
EXPORT_FOLDER_PATH = "export_data"
CASE_NAMES = []

#
# @app.on_event("startup")
# async def startup_event():
#     a = check_file_exist("case1", "new_01.nrrd")
#     b = tools.get_all_file_names(IMPORT_FOLDER_PATH, "case1")
#     print(b)

@app.get('/')
async def root():
    return "Welcome to segmentation backend"

@app.get('/api/cases')
async def get_cases_name():
    start_time = time.time()
    if tools.MASKS is not None:
        tools.saveMaskData()
        end_time = time.time()
        run_time = end_time - start_time
        print("save json cost：{:.2f}s".format(run_time))
    folder_path = IMPORT_FOLDER_PATH
    CASE_NAMES = tools.get_all_folder_names(folder_path)
    filename = "mask.json"
    res = {}
    res["names"] = CASE_NAMES
    res["details"] = []
    for directory in CASE_NAMES:
        is_exist = check_file_exist(directory, filename)
        res["details"].append({"name": directory, "masked": is_exist})
    return res


@app.get('/api/case/')
async def send_nrrd_case(name: str = Query(None)):
    start_time = time.time()
    if name is not None:
        file_names = tools.get_all_file_names(IMPORT_FOLDER_PATH, name)
        file_paths = []
        for file in file_names:
            file_paths.append(f'./{IMPORT_FOLDER_PATH}/{name}/{file}')
        with ZipFile('nrrd_files.zip', 'w') as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path)
    end_time = time.time()
    run_time = end_time - start_time
    print("get files cost：{:.2f}s".format(run_time))
    return FileResponse('nrrd_files.zip', media_type='application/zip')


@app.post("/api/mask/init")
async def init_mask(mask: model.Masks):
    tools.write_data_to_json(IMPORT_FOLDER_PATH,mask.caseId,mask.masks)
    return True

@app.post("/api/mask/replace")
async def replace_mask(replace_slice: model.Mask):
    tools.replace_data_to_json(IMPORT_FOLDER_PATH,replace_slice.caseId, replace_slice)
    return True

@app.post("/api/mask/save")
async def save_mask(mask: model.Masks):
    print("received:", len(mask.masks))
    return True


if __name__ == '__main__':
    uvicorn.run(app)
