from fastapi import FastAPI
from database.database import Base, engine
from domain.mycard.routes import mycard_router as mycard_router
from domain.mycard.routes import card_router as card_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(mycard_router)
app.include_router(card_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)