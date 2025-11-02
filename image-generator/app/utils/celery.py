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

task_exchange = Exchange('sd_prompt_tasks', type='topic', durable=True)

celery_app = Celery(
    "image_generator_tasks",
    broker=broker_url,
    backend="rpc://",
    include=[
        "app.tasks.inbox_processor_task",
    ]
)

celery_app.conf.update(
    task_routes={
        '*': {'queue': 'default', 'routing_key': 'tasks.default'},
    },

    task_queues=[
        Queue('default', task_exchange, routing_key='tasks.default', durable=True),
    ],

    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,

    task_create_missing_queues=True,

    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    'process-inbox-events-every-3-seconds': {
        'task': 'image_generator.process_inbox_events',
        'schedule': 3.0,
    },
    'cleanup-old-inbox-events-daily': {
        'task': 'image_generator.cleanup_old_inbox_events',
        'schedule': 86400.0,
    },
}


def get_broker_url():
    return broker_url
