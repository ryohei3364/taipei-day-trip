from fastapi import *
from fastapi.staticfiles import StaticFiles
from router.page import page_router
from router.attraction import attraction_router
from router.user import user_router
from router.booking import booking_router
from router.orders import orders_router

app=FastAPI(debug=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(page_router)
app.include_router(attraction_router)
app.include_router(user_router)
app.include_router(booking_router)
app.include_router(orders_router)
