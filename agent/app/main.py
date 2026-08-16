from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
logger = logging.getLogger("uvicorn")

from app.api.routes import router
from app.graph.graph import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Agent ready | model={os.getenv('LLM_MODEL')} | provider={os.getenv('LLM_PROVIDER')}")

    app.state.graph = build_graph()

    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)
