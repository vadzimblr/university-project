from app.utils.celery import celery_app
from app.services.event_publisher import get_event_publisher


@celery_app.task(name="publish_outbox_events")
def publish_outbox_events():
    publisher = get_event_publisher()

    try:
        stats = publisher.process_outbox_events(batch_size=100)

        if stats['published'] > 0:
            print(f"Published events: {stats['published']}/{stats['processed']}")

        if stats['failed'] > 0:
            print(f"Failed to publish: {stats['failed']}")
            for error in stats['errors']:
                print(f"  Event {error['event_id']}: {error['error']}")

        return stats

    except Exception as e:
        print(f"Error while publishing Outbox events: {e}")
        raise


@celery_app.task(name="cleanup_old_outbox_events")
def cleanup_old_outbox_events():
    publisher = get_event_publisher()

    try:
        deleted = publisher.cleanup_old_events(older_than_days=0)

        if deleted > 0:
            print(f"Deleted old events: {deleted}")

        return {'deleted': deleted}

    except Exception as e:
        print(f"Error while cleaning up old Outbox events: {e}")
        raise
