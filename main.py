from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI()

@app.get("/")
def read_root():
    return {
    "message": "Collaborative-Event-Management-System APIs is live.",
    "docs": "/docs",
    }

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")
