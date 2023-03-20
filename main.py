# 进入venv虚拟环境
# terminial-> venv/Scripts/activate.bat
import uvicorn
import time
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from zipfile import ZipFile
from utils import tools, Config
from models import model
from io import BytesIO
from task import task_oi


app = FastAPI()

origins = [
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


#
# @app.on_event("startup")
# async def startup_event():



@app.get('/')
async def root():
    return "Welcome to segmentation backend"


@app.get('/api/cases')
async def get_cases_name(background_tasks: BackgroundTasks):
    background_tasks.add_task(tools.save)
    tools.get_metadata()
    case_names = tools.get_all_case_names()
    case_names.sort()

    res = {}
    res["names"] = case_names
    res["details"] = []
    for name in case_names:
        is_exist = tools.check_mask_json_file(name, "mask.json")
        res["details"].append({"name": name, "masked": is_exist})
    return res


@app.get('/api/case/')
async def send_nrrd_case(name: str = Query(None)):
    start_time = time.time()
    file_paths = []
    if name is not None:
        # TODO 1: get all nrrd file paths
        nrrds_df = Config.METADATA[(Config.METADATA["file type"] == "nrrd") & (Config.METADATA["patient_id"] == name)]
        file_paths.extend(list(nrrds_df["filename"]))
        # TODO 2: get mask.json file path
        json_df = Config.METADATA[(Config.METADATA["file type"] == "json") & (Config.METADATA["patient_id"] == name)]
        file_paths.extend(list(json_df["filename"]))
        # TODO 3: add base url to these paths
        file_paths = [Config.BASE_PATH / x for x in file_paths]
        # TODO 4: zip nrrd and json files
        with ZipFile('nrrd_files.zip', 'w') as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path)
    end_time = time.time()
    run_time = end_time - start_time
    print("get files cost：{:.2f}s".format(run_time))
    return FileResponse('nrrd_files.zip', media_type='application/zip')


@app.post("/api/mask/init")
async def init_mask(mask: model.Masks):
    tools.write_data_to_json(mask.caseId, mask.masks)
    return True


@app.post("/api/mask/replace")
async def replace_mask(replace_slice: model.Mask):
    tools.replace_data_to_json(replace_slice.caseId, replace_slice)
    return True


@app.get("/api/mask/save")
async def save_mask(name: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(task_oi.json_to_nii, name)
    return True


@app.get("/api/mask")
async def get_mask(name: str = Query(None)):
    if name is not None:
        mask_json_path = tools.get_file_path(name, "json")
        cheked = tools.check_mask_json_file(name, "mask.json")
        if (cheked):
            with open(mask_json_path, mode="rb") as file:
                file_contents = file.read()
            file_object = BytesIO(file_contents)
            return StreamingResponse(file_object, media_type="application/json")
        else:
            return False


if __name__ == '__main__':
    uvicorn.run(app)
