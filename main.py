from fastapi import FastAPI, Cookie, Query, Header, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
from datetime import date
import random
app = FastAPI()

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_hanle (request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=412,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

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


class CommonPagerionClass:
    def __init__(self, page_size: int = 10, page_num:int = 1, order_by:str = 'asc'):
        self.page_size = page_size
        self.page_num = page_num
        self.order_by = order_by

class Cookies (BaseModel):
    session_id:str
    isTma: bool

class CommonHeaders(BaseModel):
    host: str | None = None
    save_data: bool = False

# 请求体
class Student(BaseModel):
    user_name: str = ''
    user_password: str = ''
    real_name: str = ''
    age: int = Field(ge=18)
    sex: SexEnum = 1
    birth: date = '2020-12-03'

class StudentOut(BaseModel):
    user_name: str
    real_name: str
    age: int = Field(ge=18)
    sex: SexEnum
    birth: date


async def auth_validate(user_token: Annotated[str, Header()]):
    if user_token != '123':
        raise HTTPException(status_code=400, detail="X-Token header invalid")

CommonPagerionData = Annotated[CommonPagerionClass, Depends()]
@app.get('/student/list', response_model=list[Student], status_code=200, dependencies=[Depends(auth_validate)])
async def getStudentList (common: CommonPagerionData) -> any:
    return [
        Student(name='小红', age=18, sex=1, birth='2012-12-12'),
        Student(name='小明', age=18, sex=0, birth='2012-12-12'),
    ]


students = {
    'id1': { 'real_name': '小明', 'age' : 30 },
    'id2': { 'real_name': '小红', 'sex' : 1 }
}

@app.get("/student/{student_id}/info", response_model=Student, response_model_exclude_unset=True)
async def getSyudentInfo(student_id: int):
    return students[student_id]

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
        raise ValueError('错误的开头参数，必需qp开')
    return qstr

@app.get('/users/{user_id}/items/{item_id}')
async def read_item (item_id: str, user_id:str, short: bool, q: Annotated[str | None, Query(title='查询', max_length=20), AfterValidator(check_q)]):
    item = {'user_id': user_id, 'item_id': item_id}
    if q:
        item.update({'q': f'id-{random.randrange(100)}'})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"}) 
    return item


student_db = {}

@app.post('/student/add', response_model=StudentOut)
async def student_add(student: Student) -> any:
    """
        注册学生信息
    """
    jsondata = jsonable_encoder(student)
    return jsondata


class LoginFormData(BaseModel):
    username: str
    password: str
    model_config = {
        'extra': 'forbid'
    }



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler (request, exc):
    return PlainTextResponse(str(exc.detail), status_code=413)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler (request, exc: RequestValidationError):
    message = 'Validation errors:'
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=402)    

@app.post('/login')
async def login(form_data : Annotated[LoginFormData, Form()]):
    if form_data.username != 'shallwe':
        # raise UnicornException('shallwe')
        raise HTTPException(status_code=411, detail='defalut')
    return form_data

@app.post('/upload/add')
async def upload_add(file: UploadFile):
    return {'filename': file.filename}