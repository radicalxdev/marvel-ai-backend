from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router

def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")

app = FastAPI()

app.include_router(router)

# Startup functions
# REDIS in-memory
# any other service start