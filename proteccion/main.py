from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from datetime import datetime
import time
from pydantic import BaseModel
from models.fibonacci import Fibonacci as FibonacciModel
from config.database import Session, engine, Base
from jwt_manager import create_token, validate_token
#from send_email import send_email_async


app = FastAPI()
app.title = "Prueba Protección"
app.version = "0.1.0"


Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
  async def __call__(self, request: Request): 
    auth = await super().__call__(request)
    data = validate_token(auth.credentials)
    if data['user'] != "admin":
      raise HTTPException(status_code=403, detail="Credenciales invalidas") 

class User(BaseModel):
  user:str
  password:str

@app.post("/login",tags=["Auth"], status_code=200)
def login(user:User):
  try:
    if user.user == "admin" and user.password=="admin":
      token: str = create_token(user.model_dump())
      return JSONResponse(content=token, status_code=200)
    else:
      return JSONResponse(content={"message":"Invalid credentials"}, status_code=401)
  except: 
    return JSONResponse(content={"message":"Invalid credentials"}, status_code=401)
  
@app.get("/", tags=["Fibonacci"])
async def fibonnacci():  
  try:
    hora_actual = datetime.now()
    minutos = str(hora_actual.time()).split(":")[1]
    segundos = str(hora_actual.time()).split(":")[2].split(".")[0]  
    txtFibonaci = fibonacci(minutos,segundos)
    db = Session()
    add_fibonacci = FibonacciModel(fibonacci=txtFibonaci,fecha=hora_actual)      
    db.add(add_fibonacci)
    db.commit()
    #await send_email_async('Fibonnaci Proteccion','daparamo@hotmail.com',
    #{'Fecha': hora_actual, 'fibonacci': txtFibonaci})
    return {"message": {"minutos":minutos,"segundos":segundos,"fibonacci":txtFibonaci}}
  except NameError: 
    return JSONResponse(content={"message": NameError}, status_code=401)

@app.get("/all", tags=["Fibonacci"])
def fibonnacci():
  db = Session()
  result = db.query(FibonacciModel).all()  
  return JSONResponse(content=jsonable_encoder(result))

@app.post("/", tags=["Fibonacci"], dependencies=[Depends(JWTBearer())])
def fibonnacci(hora:str):
  hora_actual = datetime.fromisoformat(hora)
  minutos = str(hora_actual.time()).split(":")[1]
  segundos = str(hora_actual.time()).split(":")[2].split(".")[0]  
  txtFibonaci = fibonacci(minutos,segundos)
  db = Session()  
  db.commit()
  return {"message": {"minutos":minutos,"segundos":segundos,"fibonacci":txtFibonaci}}

def fibonacci(minutos,segundos):
  txtFibonaci=""
  count = 0
  number1 = int(minutos[0])
  number2 = int(minutos[1])
  print(number1,number2, segundos)
  if segundos <='00':
    return {"Fibonnacci": 0}
  elif segundos == '01':
    return {"Fibonnacci": 1}
  else:
    while count < int(segundos) + 2:
      txtFibonaci += str(number1) + ' '
      fibonacci = int(number1) + int(number2)
      number1 = number2
      number2 = fibonacci
      count += 1
  return txtFibonaci