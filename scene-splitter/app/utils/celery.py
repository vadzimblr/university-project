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

task_exchange = Exchange('tasks', type='topic', durable=True)

celery_app = Celery(
    "scene_splitter_tasks",
    broker=broker_url,
    backend="rpc://",
    include=[
        "app.services.tasks.extract_text_task",
    ]
)

celery_app.conf.update(
    task_routes={
        '*.pdf.*': {'queue': 'pdf_tasks', 'routing_key': 'tasks.pdf'},
        '*': {'queue': 'default', 'routing_key': 'tasks.default'},
    },
    
    task_queues=[
        Queue('pdf_tasks', task_exchange, routing_key='tasks.pdf', durable=True),
        Queue('default', task_exchange, routing_key='tasks.default', durable=True),
    ],
    
    task_acks_late=True,
    worker_prefetch_multiplier=int(os.getenv('CELERY_WORKER_CONCURRENCY', 2)),
    task_reject_on_worker_lost=True,
    
    task_create_missing_queues=True,
    
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.task_routes.update({
    'extract_text_task': {'queue': 'pdf_tasks', 'routing_key': 'tasks.pdf'},
})

if os.getenv('CELERY_ENABLE_MONITORING', 'false').lower() == 'true':
    celery_app.conf.worker_send_task_events = True
    celery_app.conf.task_send_sent_event = True
