from fastapi import FastAPI
from enum import Enum
app = FastAPI()

class ModelName (str, Enum):
    yuwen = 'yuwen'
    shuxue = 'shuxue'
    yingyu = 'yingyu'

@app.get("/student/{student_id}/info")
async def getSyudentInfo(student_id: int):
    return {"student_id": student_id}

@app.get('/model/{model_name}')
async def getModelInfo (model_name : ModelName):
        if model_name is ModelName.yuwen:
            return {'你正在查看' + ModelName[model_name]}
        if model_name == model_name.shuxue:
            return {'   ' + ModelName[model_name]}
        return {'你正在查看' + ModelName[model_name]}