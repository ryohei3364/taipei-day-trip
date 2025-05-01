from fastapi import *
from model.model import Member
from model.auth import Auth
from view.response import success_response, error_response, DB_error_response

user_router = APIRouter()

@user_router.post("/api/user")
async def signup(request: Request):
  result_json = await request.json()
  name = result_json.get("name")
  email = result_json.get("email")
  password = result_json.get("password")
  
  try:
    get_user = Member.search_by_column("email", email)
    if get_user:
      return error_response("Email 已註冊會員帳戶")
    else:
      Member.insert(params=("name","email","password"), values=(name,email,Auth.hash_password(password)))
      return success_response(True, key="ok")
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
      
@user_router.put("/api/user/auth")
async def login(request: Request):
  result_json = await request.json()
  email = result_json.get("email")
  password = result_json.get("password")
  
  try:
    get_user = Member.search_by_column("email", email)
    if get_user and Auth.check_password(password, get_user["password"]):
      return success_response(Auth.encoded_jwt(get_user), key="token")
    else:
      return error_response("電子郵件或密碼錯誤")
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")      
      
@user_router.get("/api/user/auth")
def signin(user=Depends(Auth.get_current_user)):
  return user