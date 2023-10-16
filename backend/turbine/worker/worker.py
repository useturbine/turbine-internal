from celery import Celery, group
from celery.app.task import Context
from config import Config
from turbine.database import Task, db
from turbine.schema import ExistingPipelineSchema
from turbine.vector_database import VectorItem
from datetime import datetime
from uuid import UUID
from types import TracebackType
from logging import getLogger


app = Celery(
    "turbine", backend=Config.celery_backend_url, broker=Config.celery_broker_url
)
logger = getLogger(__name__)


@app.task
def run_pipeline(pipeline: dict, task_id: str):
    pipeline_parsed = ExistingPipelineSchema(**pipeline)
    keys = pipeline_parsed.data_source.get_keys()
    chains = group(
        (get_documents.s(pipeline, key) | process_documents.s(pipeline)) for key in keys
    ) | on_task_success.si(task_id).on_error(on_task_error.s(task_id))
    chains.delay()


@app.task
def process_documents(documents: list[dict], pipeline: dict):
    chains = group(
        (
            create_embedding.s(pipeline, document)
            | store_embedding.s(pipeline, document["id"])
        )
        for document in documents
    )
    chains.delay()


@app.task
def get_keys(pipeline: dict) -> list[str]:
    pipeline_parsed = ExistingPipelineSchema(**pipeline)
    return pipeline_parsed.data_source.get_keys()


@app.task
def get_documents(pipeline: dict, key: str) -> list[dict]:
    pipeline_parsed = ExistingPipelineSchema(**pipeline)
    return [
        document.model_dump()
        for document in pipeline_parsed.data_source.get_documents(key)
    ]


@app.task
def create_embedding(pipeline: dict, document: dict) -> list[float]:
    pipeline_parsed = ExistingPipelineSchema(**pipeline)
    embedding = pipeline_parsed.embedding_model.get_embedding(document["text"])
    return embedding


@app.task
def store_embedding(
    embedding: list[float],
    pipeline: dict,
    document_id: str,
) -> None:
    pipeline_parsed = ExistingPipelineSchema(**pipeline)
    pipeline_parsed.vector_database.insert(
        [VectorItem(id=document_id, vector=embedding)]
    )


@app.task
def on_task_success(task_id: str, *args):
    with db:
        if db.is_closed():
            db.connect()
        try:
            task = Task.get_by_id(task_id)
            task.finished_at = datetime.now()
            task.successful = True
            task.save()
        except Exception as e:
            logger.error("Error while saving task details after task success", e)


@app.task
def on_task_error(
    context: Context, error: Exception, traceback: TracebackType, task_id: UUID, *args
):
    with db:
        if db.is_closed():
            db.connect()
        try:
            task = Task.get_by_id(task_id)
            task.finished_at = datetime.now()
            task.successful = False
            task.save()
        except Exception as e:
            logger.error("Error while saving task details after task error", e)
