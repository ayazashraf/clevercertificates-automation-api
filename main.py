# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

from app.routes import get_template, log_template, save_image, save_etsy_image, save_pdf, template_batch, market_data, sync_template

origins = [
    "http://localhost:3000",  # local dev frontend
    "https://generator.clevercertificates.com",  # optional: production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # Or use ["*"] if you want to allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return JSONResponse(content={"message": "pong"})

# Register all route modules
app.include_router(get_template.router)
app.include_router(log_template.router)
app.include_router(save_image.router)
app.include_router(save_etsy_image.router)
app.include_router(save_pdf.router)
app.include_router(template_batch.router)
app.include_router(market_data.router)
app.include_router(sync_template.router)

print("✔ save_image router registered")
print("✔ save_etsy_image router registered")

@app.on_event("startup")
async def log_routes():
    print("✔ App started, logging routes")

