from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routes import save_image

app = FastAPI()

@app.get("/ping")
async def ping():
    return JSONResponse(content={"message": "pong"})

# Register /save-image route
app.include_router(save_image.router)
