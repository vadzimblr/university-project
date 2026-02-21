import os
from celery import Celery
from kombu import Queue, Exchange

required_env_vars = ["RABBITMQ_USER", "RABBITMQ_PASS", "RABBITMQ_HOST", "RABBITMQ_PORT"]
for var in required_env_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

RABBITMQ_USER = os.environ["RABBITMQ_USER"]
RABBITMQ_PASS = os.environ["RABBITMQ_PASS"]
RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT = os.environ["RABBITMQ_PORT"]

broker_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"

TASK_EXCHANGE_NAME = "scene_splitter.tasks"
TASK_ROUTING_PREFIX = "scene_splitter.tasks"
TASK_DEFAULT_QUEUE = "scene_splitter.tasks.default"
TASK_PDF_QUEUE = "scene_splitter.tasks.pdf"

task_exchange = Exchange(TASK_EXCHANGE_NAME, type='topic', durable=True)

celery_app = Celery(
    "scene_splitter_tasks",
    broker=broker_url,
    backend=None,
    include=[
        "infrastructure.celery.tasks.scene_segmentation_task",
    ]
)

celery_app.conf.update(
    task_routes={
        '*.pdf.*': {'queue': TASK_PDF_QUEUE, 'routing_key': f'{TASK_ROUTING_PREFIX}.pdf'},
        '*': {'queue': TASK_DEFAULT_QUEUE, 'routing_key': f'{TASK_ROUTING_PREFIX}.default'},
    },
    task_queues=[
        Queue(TASK_PDF_QUEUE, task_exchange, routing_key=f'{TASK_ROUTING_PREFIX}.pdf', durable=True),
        Queue(TASK_DEFAULT_QUEUE, task_exchange, routing_key=f'{TASK_ROUTING_PREFIX}.default', durable=True),
    ],
    task_default_exchange=TASK_EXCHANGE_NAME,
    task_default_exchange_type='topic',
    task_default_routing_key=f'{TASK_ROUTING_PREFIX}.default',
    task_default_queue=TASK_DEFAULT_QUEUE,
    task_acks_late=True,
    worker_prefetch_multiplier=int(os.getenv('CELERY_WORKER_CONCURRENCY', 2)),
    task_reject_on_worker_lost=True,
    task_create_missing_queues=False,
    task_ignore_result=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.task_routes.update({
    'scene_segmentation_task': {'queue': TASK_PDF_QUEUE, 'routing_key': f'{TASK_ROUTING_PREFIX}.pdf'},
})

if os.getenv('CELERY_ENABLE_MONITORING', 'false').lower() == 'true':
    celery_app.conf.worker_send_task_events = True
    celery_app.conf.task_send_sent_event = True

def get_broker_url():
    return broker_url
