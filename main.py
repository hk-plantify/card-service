from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from database import models
import os
from domain import oauth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

elastic_ip = os.getenv("ELASTIC_IP")

origins = [
    "http://localhost:3000",
    f"http://{elastic_ip}",
    "http://host.docker.internal:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(oauth.router)
app.include_router(home.router)
app.include_router(sic.router)
app.include_router(mypage.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


