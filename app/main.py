from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="eSnse")

app.include_router(routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
