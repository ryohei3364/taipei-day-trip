from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

page_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@page_router.get("/", include_in_schema=False)
async def index(request: Request):
	return templates.TemplateResponse(request=request, name="index.html")
@page_router.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return templates.TemplateResponse(request=request, name="attraction.html")
@page_router.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return templates.TemplateResponse(request=request, name="booking.html")
@page_router.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request, number: str):
  return templates.TemplateResponse(request=request, name="thankyou.html", context={"message": number})
@page_router.get("/member", include_in_schema=False)
async def member(request: Request):
	return templates.TemplateResponse(request=request, name="member.html")
