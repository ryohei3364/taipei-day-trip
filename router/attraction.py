from fastapi import APIRouter
from model.model import Attraction, Mrt
from view.response import success_response, error_response, DB_error_response
import json

attraction_router = APIRouter()

@attraction_router.get("/api/attractions")
async def search(page: int=0, keyword: str=None):
  try:
    get_attraction_by_keyword = Attraction.search_by_keyword(page, keyword)
  
    if get_attraction_by_keyword :
      for spot in get_attraction_by_keyword ['data']:
        images = json.loads(spot["images"])
        spot['images'] = images[0] 
      return success_response(get_attraction_by_keyword, key=None, cache_control="public, max-age=3600")
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")

@attraction_router.get("/api/attraction/{id}")
async def get_attraction(id: int):
  try:
    get_attraction_by_id = Attraction.search_by_column("id", id)
    if get_attraction_by_id:
      get_attraction_by_id['images'] = json.loads(get_attraction_by_id['images'])
      return success_response(get_attraction_by_id, cache_control="public, max-age=3600")
    else:
      return error_response("景點編號錯誤")
  except Exception as e:
    return DB_error_response("伺服器內部錯誤")
  
@attraction_router.get("/api/mrts")
async def station():
  try:
    get_mrt = Mrt.search_all()
    mrt_list = [mrt['mrt'] for mrt in get_mrt if mrt['mrt']]
    return success_response(mrt_list, cache_control="public, max-age=3600")
  except Exception as e:
    print(f"[API ERROR] /api/mrts 錯誤: {e}")
    return DB_error_response("伺服器內部錯誤")