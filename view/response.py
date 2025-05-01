from fastapi.responses import JSONResponse

def success_response(data, status_code=200, key: str = "data"):
  content = {key: data} if key else data
  return JSONResponse(
    status_code=status_code,
    headers={"content-type": "application/json;charset=utf-8"},
    content=content
  )

def error_response(message, status_code=400):
  return JSONResponse(
    status_code=status_code,
    headers={"content-type": "application/json;charset=utf-8"},
    content={
      "error": True,
      "message": message
    }
  )

def DB_error_response(message, status_code=500):  
  return JSONResponse(
    status_code=status_code,
    headers={"content-type": "application/json;charset=utf-8"},
    content={
      "error": True,
      "message": message
    }
  )