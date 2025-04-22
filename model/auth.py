from fastapi import Request
from fastapi.responses import JSONResponse
import jwt, os, bcrypt, random
from datetime import datetime, timedelta, timezone
from view.response import success_response, error_response

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM")

class Auth:
  def get_current_user(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization or authorization == "Bearer null":
      return error_response("請先登入網站", status_code=403)
    try:
      token = authorization.split("Bearer ")[1]
      decoded_token = jwt.decode(token, PRIVATE_KEY, ALGORITHM)
      return {"data": decoded_token}
    except jwt.ExpiredSignatureError:
      return error_response("使用者登入憑證已過期")

  def get_user_id(user):
    if isinstance(user, JSONResponse):
      print(user)
      return user
    return user["data"]["id"]
    
  def hash_password(password):
    input_password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(input_password, bcrypt.gensalt(rounds=4)) 
    return hashed_password.decode("utf-8")
  
  def check_password(password, hashed_password):
    if isinstance(hashed_password, str):
      hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

  def encoded_jwt(result):
    exp_time = (datetime.now(tz=timezone.utc) + timedelta(days=7)).timestamp()
    payload = {
      "id": result['id'],
      "name": result['name'],
      "email": result['email'],
      "exp": int(exp_time)
    }
    return jwt.encode(payload, PRIVATE_KEY, ALGORITHM)

  def generate_order_number():
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
    random_token = ''.join(str(random.randint(0, 9)) for _ in range(6))
    order_number = f"{timestamp}{random_token}"
    return order_number    