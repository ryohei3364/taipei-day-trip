from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dbconf import sql_pool
from datetime import datetime, timedelta, timezone
import os, json, jwt, bcrypt

app=FastAPI()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password):
  input_password = password.encode("utf-8")
  hashed_password = bcrypt.hashpw(input_password, bcrypt.gensalt(rounds=4)) 
  return hashed_password.decode("utf-8")

def check_password(password, hashed_password):
  if isinstance(hashed_password, str):
    hashed_password = hashed_password.encode("utf-8")
  return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

def encoded_jwt(user):
  exp_time = (datetime.now(tz=timezone.utc) + timedelta(days=7)).timestamp()
  payload = {
    "id": user['id'],
    "name": user['name'],
    "email": user['email'],
    "exp": int(exp_time)
  }
  return jwt.encode(payload, PRIVATE_KEY, ALGORITHM)
                    
def get_current_user(request: Request):
  authorization = request.headers.get("Authorization")
  if not authorization or authorization == "Bearer null":
    return JSONResponse(
      status_code=403,
      content={
        "error": True,
        "message": "請先登入網站"
      }
    )
  try:
    token = authorization.split("Bearer ")[1]
    decoded_token = jwt.decode(token, PRIVATE_KEY, ALGORITHM)
    return {"data": decoded_token}
  except jwt.ExpiredSignatureError:
    return {"error": "使用者登入憑證已過期"}

@app.get("/api/booking")
async def current_booking(request: Request, user=Depends(get_current_user)):
  if isinstance(user, JSONResponse):
    return user
  userId = user['data']['id']
  query = """
    SELECT * FROM attraction INNER JOIN booking ON attraction.id=booking.attractionId WHERE booking.userId=%s;
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (userId,))
      result = cursor.fetchone()
      if result is None:
        return JSONResponse(
          status_code=200,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "data": None
          }
        )
      attractionId = result.get("attractionId")
      name = result.get("name")
      address = result.get("address")
      date = result.get("date")
      images = json.loads(result["images"])  # 使用 json.loads() 把字串轉成 Python 的 list
      image = images[0]
      time = result.get("time")
      price = result.get("price")
      return JSONResponse(
        status_code=200,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "data": {
            "attraction": {
              "id": attractionId,
              "name": name,
              "address": address,
              "image": image      
            },
            "date": str(date),
            "time": time,
            "price": price
          }
        }
      )   
  except Exception as e:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close() 

@app.post("/api/booking")
async def update_booking(request: Request, user=Depends(get_current_user)):
  if isinstance(user, JSONResponse):
    return user
  result = await request.json()
  userId = user['data']['id']
  attractionId = result.get("attractionId")
  date = result.get("date")
  time = result.get("time")
  price = result.get("price")
    
  if not attractionId or not date or not time or not price:
    return JSONResponse(
      status_code=400,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "資料提供不完整"
      }
    )
  select_query = "SELECT * FROM booking WHERE userId = %s"
  delete_query = "DELETE FROM booking WHERE userId = %s"
  insert_query = """
    INSERT INTO booking(userId,attractionId,date,time,price) VALUES(%s,%s,%s,%s,%s)
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(select_query, (userId,))
      existing = cursor.fetchone()
      if existing:
        print("已有預約資料，準備刪除舊的")
        cursor.execute(delete_query, (userId,))
      if time == "morning":
        time = "上午 9 點到下午 4 點"
      else:
        time = "下午 2 點到晚上 9 點"
      cursor.execute(insert_query, (userId,attractionId,date,time,price))
      cnx.commit()
      return JSONResponse(
        status_code=200,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "ok": True
        }
      )        
  except Exception as e:
    print(f"[ERROR] API 取得用戶資料庫失敗: {e}")
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()

@app.delete("/api/booking")
def delete_booking(request: Request, user=Depends(get_current_user)):
  if isinstance(user, JSONResponse):
    return user
  userId = user['data']['id']
  delete_query = "DELETE FROM booking WHERE userId = %s"
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(delete_query, (userId,))
      if cursor.rowcount == 0:
        return JSONResponse(
          status_code=400,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "error": True,
            "message": "目前沒有預定行程"
          }
        )
      cnx.commit()
      return JSONResponse(
        status_code=200,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "ok": True
        }
      )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()

@app.post("/api/user")
async def signup(request: Request):
  cnx = None
  result = await request.json()
  name = result.get("name")
  email = result.get("email")
  password = result.get("password")
  query = """
    SELECT email, password FROM member WHERE email=%s
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (email,))
      user = cursor.fetchone()

    if user:
      return JSONResponse(
        status_code=400,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "error": True,
          "message": "Email 已註冊會員帳戶"
        }
      )
    else:
      query = """
        INSERT INTO member(name,email,password) VALUES(%s,%s,%s)
      """ 
      with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(query, (name,email,hash_password(password)))
        cnx.commit() 
        return JSONResponse(
          status_code=200,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "ok": True,
            "message": "註冊成功，請登入網站"
          }
        )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()
      
      
@app.put("/api/user/auth")
async def login(request: Request):
  result = await request.json()
  email = result.get("email")
  password = result.get("password")
  query = """
    SELECT id, name, email, password FROM member WHERE email=%s
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (email,))
      user = cursor.fetchone()
      
      if user and check_password(password, user["password"]):
        return JSONResponse(
          status_code=200,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "token": encoded_jwt(user),
            "message": "登入成功，歡迎回來"
          }
        )
      else:
        return JSONResponse(
          status_code=400,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "error": True,
            "message": "電子郵件或密碼錯誤"
          }
        )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()
      
      
@app.get("/api/user/auth")
def signin(user=Depends(get_current_user)):
  return user
  
# 取得景點資料列表 /api/attractions?page=int&keyword=str
@app.get("/api/attractions")
async def search(page: int=0, keyword: str=None):
  PAGE_SIZE = 12
  offset = page * PAGE_SIZE
  cnx = None
  
  base_query = """
    SELECT id, name, category, description, address, transport, mrt, lat, lng, images
    FROM attraction
  """
  page_query = " LIMIT %s OFFSET %s"
  
  if keyword:
    keyword_query = " WHERE name LIKE %s OR mrt = %s"
    full_query = base_query + keyword_query + page_query
    keyword_param = f"%{keyword}%"
    params = (keyword_param, keyword, PAGE_SIZE, offset)
  else:
    full_query = base_query + page_query
    params = (PAGE_SIZE, offset)
  
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(full_query, params)
      data = cursor.fetchall()
  
    next_page = page + 1 if len(data) == PAGE_SIZE else None

    if data:
      for spot in data:
        spot['images'] = json.loads(spot['images'])
      
      return JSONResponse(
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "nextPage": next_page,
          "data": data,
        }
      )
      
  except Exception as e:
    print(f"[ERROR] API 取得景點資料失敗: {e}")
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()
    

@app.get("/api/attraction/{attractionId}")
async def get_attraction(attractionId: int):
  cnx = None
  query = """
    SELECT id, name, category, description, address, transport, mrt, lat, lng, images
    FROM attraction WHERE id=%s
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (attractionId,))
      data = cursor.fetchone()
    
    if data:
      data['images'] = json.loads(data['images'])
      return JSONResponse(
        headers={"content-type": "application/json;charset=utf-8"},
        content={"data": data}
      )
    else:
      return JSONResponse(
        status_code=400,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "error": True,
          "message": "景點編號錯誤"
        }
      )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()


@app.get("/api/mrts")
async def station():
  query = """
    SELECT mrt, COUNT(mrt) FROM attraction 
    GROUP BY mrt ORDER BY COUNT(mrt) DESC
  """ 
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query)
      data = cursor.fetchall()

    if data:
      mrt_list = [mrt["mrt"] for mrt in data if mrt and mrt.get("mrt") is not None]
      return JSONResponse(
        headers={"content-type": "application/json;charset=utf-8"},
        content={"data": mrt_list}
      )
      
  except Exception as e:
    print(f"[ERROR] API 取得捷運站資料失敗: {e}")
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  finally:
    if cnx:
      cnx.close()

  
# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return templates.TemplateResponse(request=request, name="index.html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return templates.TemplateResponse(request=request, name="attraction.html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return templates.TemplateResponse(request=request, name="booking.html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
  return templates.TemplateResponse(request=request, name="thankyou.html")
  
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="./static/templates")