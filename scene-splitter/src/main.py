from fastapi import FastAPI
from presentation.api.get_job_status_action import router as api_router
from presentation.api.get_scenes_by_job_identifier_action import router as get_scenes_by_job_identifier_router
from core.di.container import Container


def create_app():
    container = Container()

    app = FastAPI(title="Scene Splitter Service")
    app.container = container
    app.include_router(api_router, prefix="/api")
    app.include_router(get_scenes_by_job_identifier_router, prefix="/api")
    return app

app = create_app()
