from fastapi import *
from model.model import Booking, Orders
from model.auth import Auth
from view.response import success_response, error_response, DB_error_response
import json

booking_router = APIRouter()

@booking_router.get("/api/booking")
async def current_booking(request: Request, user=Depends(Auth.get_current_user)):
  userId = Auth.get_user_id(user)
  try:
    arrange_booking_data = Booking.get_booking_by_userId(userId)
    if arrange_booking_data is None:
      return success_response(None)
    else:
      attractionId = arrange_booking_data.get("id")
      name = arrange_booking_data.get("name")
      address = arrange_booking_data.get("address")
      date = arrange_booking_data.get("date")
      images = json.loads(arrange_booking_data["images"])
      image = images[0]
      time = arrange_booking_data.get("time")
      price = arrange_booking_data.get("price")
      data = {
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
      return success_response(data)
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
  
@booking_router.post("/api/booking")
async def update_booking(request: Request, user=Depends(Auth.get_current_user)):
  userId = Auth.get_user_id(user)
  result_json = await request.json()
  attractionId = result_json.get("attractionId")
  date = result_json.get("date")
  time = result_json.get("time")
  price = result_json.get("price")
  
  if not attractionId or not date or not time or not price:
    return error_response("資料提供不完整")
  try:
    booking_data = Booking.search_by_column("userId", userId)
    if booking_data:
      Booking.delete_by_column("userId", userId)
    if time == "morning":
      time = "上午 9 點到下午 4 點"
    else:
      time = "下午 2 點到晚上 9 點"
      
    Booking.insert(params=("userId","attractionId","date","time","price"), values=(userId,attractionId,date,time,price))
    return success_response(True, key="ok")
  
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
  
@booking_router.delete("/api/booking")
def delete_booking(request: Request, user=Depends(Auth.get_current_user)):
  userId = Auth.get_user_id(user)
  try:  
    booking_data = Booking.search_by_column("userId", userId)
    
    if booking_data:
      bookingId = booking_data.get("bookingId")
      delete_booking_data = Booking.delete_by_column("userId", userId)
      if delete_booking_data != 0:
        Orders.delete_by_column("bookingId", bookingId)
        return success_response(True, key="ok")
    else:
      return error_response("目前沒有預定行程")
    
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")