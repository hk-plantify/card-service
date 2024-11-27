from fastapi import FastAPI
from database.database import Base, engine
from domain.mycard.routes import router as mycard_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(mycard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)