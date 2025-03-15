from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
import mysql.connector, os, json

load_dotenv()
MYSQL_PW=os.getenv("MYSQL_PW")

app=FastAPI()

con = mysql.connector.pooling.MySQLConnectionPool(
  pool_name = "mypool",
  pool_size = 10,
  user = "demo",
  password = MYSQL_PW,
  host = "localhost",
  database = "website",
  charset='utf8'
)

cnx=con.get_connection()
cursor = cnx.cursor(dictionary=True)

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
      
  except Exception:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
    

# 根據景點編號取得景點資料 /api/attraction/{attractionId}
@app.get("/api/attraction/{attractionId}")
async def attraction_id(request: Request, attractionId: int):
  try:
    query = """
      SELECT id, name, category, description, address, transport, mrt, lat, lng, images
      FROM attraction WHERE data_id=%s
    """
    cursor.execute(query, (attractionId,))
    data = cursor.fetchall()
    # print(data[0])
    # print(data[0]['images'])
    
    if data:
      for spot in data:
        spot['images'] = json.loads(spot['images'])

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
  except Exception:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )


# 取得捷運站名稱列表 /api/mrts
@app.get("/api/mrts")
async def station(request: Request):
  try:
    query = """
        SELECT mrt, COUNT(mrt) FROM attraction 
        GROUP BY mrt ORDER BY COUNT(mrt) DESC
      """ 
    cursor.execute(query)
    data = cursor.fetchall()

    if data:
      mrt_list = [mrt["mrt"] for mrt in data if mrt and mrt.get("mrt") is not None]
      return JSONResponse(
        headers={"content-type": "application/json;charset=utf-8"},
        content={"data": mrt_list}
      )
      
  except Exception:
    return JSONResponse(
      status_code=500,
      headers={"content-type": "application/json;charset=utf-8"},
      content={
        "error": True,
        "message": "伺服器內部錯誤"
      }
    )
  