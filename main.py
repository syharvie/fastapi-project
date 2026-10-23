from fastapi import FastAPI, Cookie, Query, Header, Form, File, UploadFile, HTTPException, Request, Depends, Path, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
from datetime import date, datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
import time
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


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
    "shallwe1": {
        'user_name': 'shallwe1',
        'user_password': '$argon2id$v=19$m=65536,t=3,p=4$DN8po4gCPpcHWQnjVJG37g$OD2hWJyQKyX7zWRMqf5oQI9Ze3lFomslDLemGIduCdU',
        'real_name': '小明',
        'token': 'dshdjhwk2334444',
        'age': 19,
        'sex': 0,
        'birth': '2020-12-03',
        'disabled': None
    },
    "shallwe2": {
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


SECRET_KEY = "753f10b942672c08e591d3a7460b825cf1907d483ae2596bf04718d265ec391"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash('dummypassword')

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def fake_hash_password(password: str):
    return 'fakehashed'  + password

class StudentInDb(Student):
    user_password: str

def get_student(db, token: str):
    for el in db.values():
        if el.get('token') == token:
            return StudentInDb(**el)

def get_student_by_name(db, username: str):
    if username in db:
        user_dict = db[username]
        return StudentInDb(**user_dict)
                
def fake_decode_token(token):
    student = get_student(fake_student_db, token)
    return  student

def authenticate_student(fake_student_db, username: str, password: str):
    student = get_student_by_name(fake_student_db,  username)
    if not student:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, student.user_password):
        return False
    return student

def create_access_token(data: dict, expires_detla: timedelta | None = None):
    to_encode = data.copy()
    if expires_detla:
        expires = datetime.now(timezone.utc) + expires_detla
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expires})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt    


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

async def get_current_student(token: Annotated[str, Depends(oauth2_shcema)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    student  = get_student_by_name(fake_student_db, username=token_data.username)
    if student is None:
        raise credentials_exception
    return student    
        

async def get_current_active_student(current_student: Annotated[Student, Depends(get_current_student)]):
    if current_student.disabled:
        raise HTTPException(status_code=400, detail='Inactive Student')
    return current_student



@app.post('/token')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    student = authenticate_student(fake_student_db, form_data.username, form_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': student.user_name},
        expires_detla=access_token_expires
    )
    return Token(access_token = access_token, token_type='bearer')

@app.get('/student/me')
async def read_student_me(current_student: Annotated[Student, Depends(get_current_active_student)]):
    return current_student


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

from sqlmodel import Field,Session,SQLModel,create_engine,select

class Hero (SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str

mysql_url = 'mysql+pymysql://root:123456@127.0.0.1:3306/fastapi_hero?charset=utf8mb4'
engine = create_engine(
    mysql_url,
    pool_recycle=1800,
    pool_pre_ping=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('应用启动，创建数据表')

    