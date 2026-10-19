from fastapi import FastAPI, Query
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
import random
app = FastAPI()

class ModelName (str, Enum):
    yuwen = 'yuwen'
    shuxue = 'shuxue'
    yingyu = 'yingyu'

class SexEnum (int, Enum):
    female = 0
    male = 1

class PageParams (BaseModel):
    model_config = {"extra": "forbid"}
    pageSize: int = Field(100, gt=1, le=1000)
    pageNumber: int = Field(1, ge=1)
    orderBy: Literal['created_at', 'updated_at'] = 'created_at'



@app.get('/student/list')
async def getStudentList (pageParams: Annotated[PageParams, Query()]):
    return {'list': []}

@app.get("/student/{student_id}/info")
async def getSyudentInfo(student_id: int):
    return {"student_id": student_id}

@app.get('/model/{model_name}')
async def getModelInfo (model_name : ModelName):
        if model_name is ModelName.yuwen:
            return {"model_name": model_name, "message": "Deep Learning FTW!"}
        if model_name == model_name.shuxue:
            return {'你正在查看' + ModelName[model_name]}
        return {'你正在查看' + ModelName[model_name]}

@app.get('/files/{file_path:path}')
async def read_file (file_path:str):
    return {'file_path': file_path}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
@app.get('/items/')
async def read_items (skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]

def check_q (qstr: str):
    if not qstr.startswith('qp'):
        raise ValueError('错误的开头参数，必学以qp开头')
    return qstr

@app.get('/users/{user_id}/items/{item_id}')
async def read_item (item_id: str, user_id:str, short: bool, q: Annotated[str | None, Query(title='查询', max_length=20), AfterValidator(check_q)]):
    item = {'user_id': user_id, 'item_id': item_id}
    if q:
        item.update({'q': f'id-{random.randrange(100)}'})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"}) 
    return item


# 请求体
class Student(BaseModel):
    name: str
    age: int = Field(ge=18)
    sex: SexEnum
    birth: str

@app.post('/student/add')
async def student_add(student: Student):
    return student