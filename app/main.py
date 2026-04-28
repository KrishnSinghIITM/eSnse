from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.api import routes

# Use ORJSONResponse as the default response class so JSON responses
# include literal Unicode characters (e.g., the rupee sign ₹) instead
# of escaped sequences like "\u20b9".
app = FastAPI(title="eSnse", default_response_class=ORJSONResponse)

app.include_router(routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
