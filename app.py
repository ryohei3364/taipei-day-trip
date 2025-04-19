from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from model.dbconf import sql_pool
from model.model import Attraction
from datetime import datetime, timedelta, timezone
import os, json, jwt, bcrypt, random, requests

app=FastAPI()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM")
PARTNER_KEY = os.getenv("PARTNER_KEY")
MERCHANT_ID = os.getenv("MERCHANT_ID")

TAPPAY_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

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

def get_booking_by_userId(userId: int):
  query = """
    SELECT * FROM attraction 
    INNER JOIN booking ON attraction.id=booking.attractionId 
    WHERE booking.userId=%s;
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (userId,))
      result = cursor.fetchone()
      return result
  except:
    return None
  finally:
    if cnx:
      cnx.close()
      
def generate_order_number():
  timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
  random_token = ''.join(str(random.randint(0, 9)) for _ in range(6))
  order_number = f"{timestamp}{random_token}"
  return order_number

def pay_by_prime(prime, order_number, amount, contact_name, contact_email, contact_phone):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": PARTNER_KEY
    }
    payload = {
        "prime": prime,
        "partner_key": PARTNER_KEY,
        "merchant_id": MERCHANT_ID,
        "details": "TapPay Test",
        "amount": amount,
        "cardholder": {
            "phone_number": contact_phone,
            "name": contact_name,
            "email": contact_email,
        },
        "order_number": order_number
    }
    response = requests.post(TAPPAY_URL, headers=headers, json=payload)
    return response.json()
      
@app.get("/api/order/{orderNumber}")
async def current_order(orderNumber: str, request: Request, user=Depends(get_current_user)):
  orderNumber = orderNumber.strip()
  if isinstance(user, JSONResponse):
    return user
  query = """
    SELECT * FROM orders WHERE orderNumber=%s
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(query, (orderNumber,))
      order = cursor.fetchone()
      
      if order:
        userId = user['data']['id']
        attraction = get_booking_by_userId(userId)
        images = json.loads(attraction["images"])
        image = images[0]

        return JSONResponse(
          status_code=200,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "data": {
              "number": orderNumber,
              "price": order['price'],
              "trip": {
                "attraction": {
                  "id": attraction['id'],
                  "name": attraction['name'],
                  "address": attraction['address'],
                  "image": image
                },
                "date": str(order['date']),
                "time": order['time']
              },
              "contact": {
                "name": order['contactName'],
                "email": order['contactEmail'],
                "phone": order['contactPhone'],
              },
              "status": order['status']
            }
          }
        )
      else:
        return JSONResponse(
          status_code=200,
          headers={"content-type": "application/json;charset=utf-8"},
          content={
            "data": None
          }
        )
        
  except Exception as e:
    print("訂單建立失敗：", e)
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
    
          
@app.post("/api/orders")
async def current_order(request: Request, user=Depends(get_current_user)):
  if isinstance(user, JSONResponse):
    return user
  result = await request.json()

  if result is None:
    return JSONResponse(
      status_code=400,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "訂單資訊不完整"
      }
    )
  number = generate_order_number()
  userId = user['data']['id']
  data = get_booking_by_userId(userId)
  bookingId = data['bookingId']
  date = result['order']['trip']['date']
  time = result['order']['trip']['time']
  contactName = result['order']['contact']['name']
  contactEmail = result['order']['contact']['email']
  contactPhone = result['order']['contact']['phone']
  prime = result['prime']
  price = result['order']['price']
  
  insert_query = """
    INSERT INTO orders(orderNumber,bookingId,date,time,price,contactName,contactEmail,contactPhone,status) 
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
  """
  check_existing_order_query = """
    SELECT * FROM orders WHERE bookingId = %s AND status = 1
  """
  update_status_query = """
    UPDATE orders SET status = 0 WHERE bookingId = %s
  """
  delete_booking_query = """
    DELETE FROM booking WHERE bookingId = %s
  """
  try:
    cnx = sql_pool.get_connection()
    with cnx.cursor(dictionary=True) as cursor:
      cursor.execute(check_existing_order_query, (bookingId,))
      existing_order = cursor.fetchone()
      
      if existing_order:
        number = existing_order['orderNumber']
        tappay_result = pay_by_prime(prime, number, price, contactName, contactEmail, contactPhone)
          
        if tappay_result.get("status") == 0:
          with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(update_status_query, (bookingId,))
            cursor.execute(delete_booking_query, (bookingId,))
            cnx.commit()
          return JSONResponse(
            status_code=200,
            headers={"content-type": "application/json;charset=utf-8"},
            content={
              "data": {
                "number": number,
                "payment": {
                  "status": 0,
                  "image": "付款成功"  
                }
              }
            }
          )
        else:
          return JSONResponse(
            status_code=400,
            headers={"content-type": "application/json;charset=utf-8"},
            content={
              "error": True,
              "message": "已有未付款訂單，且付款驗證失敗，TapPay status: " + str(tappay_result.get("status"))
            }
          )
      cursor.execute(insert_query, (number,bookingId,date,time,price,contactName,contactEmail,contactPhone,1))
      cnx.commit()
    
    tappay_result = pay_by_prime(prime, number, price, contactName, contactEmail, contactPhone)

    if tappay_result.get("status") == 0:
      with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(update_status_query, (bookingId,))
        cursor.execute(delete_booking_query, (bookingId,))
        cnx.commit()
      return JSONResponse(
        status_code=200,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "data": {
            "number": number,
            "payment": {
              "status": 0,
              "image": "付款成功"
            }
          }
        }
      )
    else:
      return JSONResponse(
        status_code=400,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "error": True,
          "message": "付款失敗，TapPay status: " + str(tappay_result.get("status"))
        }
      )

  except Exception as e:
    print("訂單建立失敗：", e)
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

@app.get("/api/booking")
async def current_booking(request: Request, user=Depends(get_current_user)):
  if isinstance(user, JSONResponse):
    return user
  userId = user['data']['id']
  result = get_booking_by_userId(userId)
  try: 
    if result is None:
      return JSONResponse(
        status_code=200,
        headers={"content-type": "application/json;charset=utf-8"},
        content={
          "data": None
        }
      )
    else:
      attractionId = result.get("id")
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
  
@app.get("/api/attractions")
async def search(page: int=0, keyword: str=None):
  search_result = Attraction().search_attractions(page, keyword)
  if search_result:
    for spot in search_result['data']:
      images = json.loads(spot["images"]) # 把字串轉回 Python 的資料
      spot['images'] = images[0] 
    return JSONResponse(
      headers={"content-type": "application/json;charset=utf-8"},
      content=search_result
    )

@app.get("/api/attraction/{id}")
async def get_attraction(id: int):
  attraction_instance = Attraction(id) 
  attraction = attraction_instance.to_dict() # 確保是 dict，不是 class 物件
  if attraction:
    attraction['images'] = json.loads(attraction['images'])
    return JSONResponse(
      headers={"content-type": "application/json;charset=utf-8"},
      content={"data": attraction}
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
async def thankyou(request: Request, number: str):
  return templates.TemplateResponse(request=request, name="thankyou.html", context={"message": number})
  
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="./static/templates")