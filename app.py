from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
import mysql.connector, os

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
@app.get("/api/attractions", include_in_schema=False)
async def search(request: Request, page: int=0, keyword: str=None):
  PAGE_SIZE = 12
  offset = page * PAGE_SIZE
  
  if keyword:
    query = """
      SELECT id, name, category, description, address, transport, mrt, lat, lng, images
      FROM attraction WHERE name LIKE %s OR mrt=%s LIMIT %s OFFSET %s
    """
    keyword_param=f"%{keyword}%"
    params = (keyword_param, keyword, PAGE_SIZE, offset)
    print(params)
    
    cursor.execute(query, params)
    attractions = cursor.fetchall()
    
    if not attractions:
      return {
        "nextPage": None,
        "data": [],
      }
    else:
      return {
        "nextPage": page + 1,
        "data": attractions,
      }
  else:
    return JSONResponse(
      status_code=500,
      content={
        "error": True,
        "message": "請輸入關鍵字查詢"
      }
    )

# 根據景點編號取得景點資料 /api/attraction/{attractionId}
@app.get("/api/attraction/{attractionId}", include_in_schema=False)
async def attraction_id(request: Request, attractionId: int):
  if attractionId:
    query = """
      SELECT id, name, category, description, address, transport, mrt, lat, lng, images
      FROM attraction WHERE data_id=%s
    """
    cursor.execute(query, (attractionId,))
    data = cursor.fetchall()
    if data:
      return {
        "data": data
      }
    else:
      return JSONResponse(
        status_code=400,
        content={
          "error": True,
          "message": "景點編號錯誤"
        }
      )
  else:
    return JSONResponse(
      status_code=500,
      content={
        "error": True,
        "message": "請輸入景點編號查詢"
      }
    )


# 取得捷運站名稱列表 /api/mrts
@app.get("/api/mrts", include_in_schema=False)
async def station(request: Request):
  query = """
      SELECT mrt, COUNT(mrt) FROM attraction 
      GROUP BY mrt ORDER BY COUNT(mrt) DESC
    """ 
  cursor.execute(query)
  data = cursor.fetchall()
  
  if data:
    mrt_list = [mrt["mrt"] for mrt in data if mrt and mrt.get("mrt") is not None]
    return {
      "data": mrt_list
    }
  else:
    return JSONResponse(
      status_code=500,
      content={
        "error": True,
        "message": "查無資料"
      }
    )
  