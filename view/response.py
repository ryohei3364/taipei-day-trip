from fastapi.responses import JSONResponse

def success_response(data, status_code=200, key: str = "data", cache_control: str = None):
  content = {key: data} if key else data
  headers = {"content-type": "application/json;charset=utf-8"}
  
  if cache_control:
    headers["Cache-Control"] = cache_control
    
  return JSONResponse(
    status_code=status_code,
    headers=headers,
    content=content
  )

def error_response(message, status_code=400, cache_control: str = None):
  headers = {"content-type": "application/json;charset=utf-8"}
  
  if cache_control:
    headers["Cache-Control"] = cache_control
    
  return JSONResponse(
    status_code=status_code,
    headers=headers,
    content={
      "error": True,
      "message": message
    }
  )

def DB_error_response(message, status_code=500, cache_control: str = None):
  headers = {"content-type": "application/json;charset=utf-8"}

  if cache_control:
    headers["Cache-Control"] = cache_control
    
  return JSONResponse(
    status_code=status_code,
    headers=headers,
    content={
      "error": True,
      "message": message
    }
  )
