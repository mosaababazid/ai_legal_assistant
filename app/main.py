from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


# Create FastAPI application instance
configure_logging()
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes.router)


@app.get("/")
async def root() -> dict:
    return {"message": "API is running correctly."}