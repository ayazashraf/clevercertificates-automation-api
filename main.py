# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routes import save_image

app = FastAPI()

@app.get("/ping")
async def ping():
    return JSONResponse(content={"message": "pong"})

app.include_router(save_image.router)
print("✔ save_image router registered")

@app.on_event("startup")
async def log_routes():
    print("✔ App started, logging routes")

