from app import app
from app.routes.api import api_router
app.include_router(api_router)
