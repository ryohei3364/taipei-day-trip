from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from connection import sql_pool
import json

app=FastAPI()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


# 取得景點資料列表 /api/attractions?page=int&keyword=str
@app.get("/api/attractions")
async def search(request: Request, page: int=0, keyword: str=None):
  PAGE_SIZE = 12
  offset = page * PAGE_SIZE
  cnx = None
  
  base_query = """
    SELECT data_id AS id, name, category, description, address, transport, mrt, lat, lng, images
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
    

# 根據景點編號取得景點資料 /api/attraction/{attractionId}
@app.get("/api/attraction/{attractionId}")
async def attraction_id(request: Request, attractionId: int):
  cnx = None
  query = """
    SELECT data_id AS id, name, category, description, address, transport, mrt, lat, lng, images
    FROM attraction WHERE data_id=%s
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


# 取得捷運站名稱列表 /api/mrts
@app.get("/api/mrts")
async def station(request: Request):
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
  
