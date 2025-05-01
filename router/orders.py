from fastapi import *
from model.model import Booking, Orders
from model.auth import Auth
from view.response import success_response, error_response, DB_error_response
import os, json, requests

orders_router = APIRouter()

PARTNER_KEY = os.getenv("PARTNER_KEY")
MERCHANT_ID = os.getenv("MERCHANT_ID")
TAPPAY_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"              

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

@orders_router.get("/api/orders")
async def all_orders(request: Request, user=Depends(Auth.get_current_user)):
  try:
    userId = Auth.get_user_id(user)
    orders_data = Orders.search_by_column("userId", userId)
    
    if orders_data:
      order_list = []
      paid_count = 0
      unpaid_count = 0
      for order in orders_data:
        if order['status'] == 0:
          paid_count += 1
        else:
          unpaid_count += 1
        order_list.append({
          "id": order['id'],
          "orderNumber": order['orderNumber'],
          "date": order['date'].isoformat(),
          "time": order['time'],
          "contactName": order['contactName'],
          "contactEmail": order['contactEmail'],
          "contactPhone": order['contactPhone'],
          "orderTime": order['orderTime'].isoformat(),
          "status": order['status'],
        })
        data = {
          "order_paid": paid_count,
          "order_unpaid": unpaid_count,
          "data": order_list
        }
      return success_response(data, key=None)
    else:
      return success_response(None)
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
            
@orders_router.get("/api/order/{orderNumber}")
async def current_order(orderNumber: str, request: Request, user=Depends(Auth.get_current_user)):
  try:
    orderNumber = orderNumber.strip()
    orders_data = Orders.search_by_column("orderNumber", orderNumber)
    
    if orders_data:
      result = Orders.get_data_by_orderNumber(orderNumber)
      
      images = json.loads(result["images"])
      image = images[0]
      data = {
        "number": orderNumber,
        "price": orders_data['price'],
        "trip": {
          "attraction": {
          "id": result['id'],
          "name": result['name'],
          "address": result['address'],
          "image": image
          },
          "date": str(orders_data['date']),
          "time": orders_data['time']
        },
        "contact": {
          "name": orders_data['contactName'],
          "email": orders_data['contactEmail'],
          "phone": orders_data['contactPhone'],
        },
        "status": orders_data['status']
      }
      return success_response(data)
    else:
      return success_response(None)
    
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
          
@orders_router.post("/api/orders")
async def current_order(request: Request, user=Depends(Auth.get_current_user)):
  try:
    userId = Auth.get_user_id(user)
    result_json = await request.json()

    if result_json is None:
      return error_response("訂單資訊不完整")
      
    number = Auth.generate_order_number()
    userId = user['data']['id']
    data = Booking.get_booking_by_userId(userId)
    if not data:
      return error_response("找不到預約資訊")
    
    bookingId = data['bookingId']
    attractionId = data['attractionId']
    date = result_json['order']['trip']['date']
    time = result_json['order']['trip']['time']
    contactName = result_json['order']['contact']['name']
    contactEmail = result_json['order']['contact']['email']
    contactPhone = result_json['order']['contact']['phone']
    prime = result_json['prime']
    price = result_json['order']['price']
    
    existing_order = Orders.search_by_columns({"bookingId": bookingId, "status": 1})
    
    if existing_order:
      number = existing_order['orderNumber']
      tappay_result = pay_by_prime(prime, number, price, contactName, contactEmail, contactPhone)
      
      if tappay_result.get("status") == 0:
        Orders.update_by_column("bookingId", bookingId, {"status": 0})
        Booking.delete_by_column("bookingId", bookingId)
        data = {
          "number": number,
          "payment": {
            "status": 0,
            "image": "付款成功"  
          }
        }
        return success_response(data)
      else:
        return error_response("已有未付款訂單，且付款驗證失敗，TapPay status: " + str(tappay_result.get("status")))
    
    Orders.insert(
      params=("orderNumber","bookingId","attractionId","userId","date","time","price","contactName","contactEmail","contactPhone","status"), 
      values=(number,bookingId,attractionId,userId,date,time,price,contactName,contactEmail,contactPhone,1)
    )
    tappay_result = pay_by_prime(prime, number, price, contactName, contactEmail, contactPhone)
  
    if tappay_result.get("status") == 0:
      Orders.update_by_column("bookingId", bookingId, {"status": 0})
      Booking.delete_by_column("bookingId", bookingId)
      data = {
        "number": number,
        "payment": {
          "status": 0,
          "image": "付款成功"  
        }
      }
      return success_response(data)
    else:
      return error_response("已有未付款訂單，且付款驗證失敗，TapPay status: " + str(tappay_result.get("status")))
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")