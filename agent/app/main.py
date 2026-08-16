from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
logger = logging.getLogger("uvicorn")

from app.api.routes import router
from app.graph.graph import build_graph
from app.rag.ingest import run_ingest
from app.rag.store import get_store, count_documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Agent ready | model={os.getenv('LLM_MODEL')} | provider={os.getenv('LLM_PROVIDER')}")

    app.state.graph = build_graph()

    if count_documents(get_store(Path("./chroma_db"))) == 0:
        logger.info("Chroma ว่าง — กำลัง ingest...")
        run_ingest()

    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)
