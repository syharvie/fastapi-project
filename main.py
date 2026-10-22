from fastapi import FastAPI, Cookie, Query, Header, Form, File, UploadFile, HTTPException, Request, Depends, Path, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
from datetime import date
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
oauth2_shcema = OAuth2PasswordBearer(tokenUrl='token')
import random
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


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
    token: str = 'token123'
    birth: date = '2020-12-03',
    disabled: bool | None = None

class StudentOut(BaseModel):
    user_name: str
    real_name: str
    age: int = Field(ge=18)
    sex: SexEnum
    birth: date
    disabled: bool | None = None


class NoStudent (Exception):
    pass

def getStudent():
    try:
        yield 'xiaoing'
    except NoStudent:
        print('233----ahaha')     

async def auth_validate(user_token: Annotated[str, Header()]):
    if user_token != '123':
        raise HTTPException(status_code=400, detail="X-Token header invalid")

CommonPagerionData = Annotated[CommonPagerionClass, Depends()]
app = FastAPI()
@app.exception_handler(UnicornException)
@app.get('/student/list', response_model=list[Student], status_code=200)
async def getStudentList (common: CommonPagerionData, token: Annotated[str, Depends(oauth2_shcema)]) -> any:
    return {"token": token}
    return [
        Student(name='小红', age=18, sex=1, birth='2012-12-12'),
        Student(name='小明', age=18, sex=0, birth='2012-12-12'),
    ]


students = {
    'id1': { 'real_name': '小明', 'age' : 30 },
    'id2': { 'real_name': '小红', 'sex' : 1 }
}


@app.get("/student/{student_id}/info", response_model=Student, response_model_exclude_unset=True)
async def getSyudentInfo(student_id: Annotated[str, Path()]):
    if student_id == 'id3':
        raise NoStudent('vvvvvvv-id3')
    if student_id == 'id4':
        raise 
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



# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler (request, exc):
#     return PlainTextResponse(str(exc.detail), status_code=413)

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


fake_student_db = {
    "id1": {
        'user_name': 'shallwe1',
        'user_password': 'fakehashed123',
        'real_name': '小明',
        'token': 'dshdjhwk2334444',
        'age': 19,
        'sex': 0,
        'birth': '2020-12-03',
        'disabled': None
    },
    "id2": {
        'user_name': 'shallwe2',
        'user_password': 'fakehashed456',
        'real_name': '小红',
        'age': 20,
        'sex': 1,
        'token': 'ndksjc91@@#d',
        'birth': '2022-12-03',
        'disabled': True
    },
}

def fake_hash_password(password: str):
    return 'fakehashed'  + password

class StudentInDb(Student):
    user_password: str

def get_student(db, token: str):
    for el in db.values():
        if el.get('token') == token:
            return StudentInDb(**el)
def fake_decode_token(token):
    student = get_student(fake_student_db, token)
    return  student

async def get_current_student(token: Annotated[str, Depends(oauth2_shcema)]):
    student = fake_decode_token(token)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return student


async def get_current_active_student(current_student: Annotated[Student, Depends(get_current_student)]):
    if current_student.disabled:
        raise HTTPException(status_code=400, detail='Inactive Student')
    return current_student



@app.post('/token/')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    student_dict = fake_student_db.get(form_data.username)
    if not student_dict:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    student = StudentInDb(**student_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == student.user_password:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    return {'access_token' : student.token, 'token_type': 'bearer'}


@app.get('/student/me')
async def read_student_me(current_student: Annotated[Student, Depends(get_current_active_student)]):
    return current_student
