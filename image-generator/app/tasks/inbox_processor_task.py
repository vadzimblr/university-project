"""
Celery tasks for processing inbox events.
These tasks run periodically via Celery Beat.
"""
from ..utils.celery import celery_app
from ..services.inbox_processor import InboxProcessor


@celery_app.task(name="image_generator.process_inbox_events")
def process_inbox_events():
    """
    Processes a batch of unprocessed events from the inbox.
    Scheduled to run every 3 seconds by Celery Beat.
    """
    processor = InboxProcessor()
    
    try:
        stats = processor.process_inbox_events(batch_size=10)
        
        if stats['processed'] > 0:
            print(f"[ImageGenerator] Processed events: {stats['succeeded']}/{stats['processed']}")
        
        if stats['failed'] > 0:
            print(f"[ImageGenerator] Failed to process: {stats['failed']}")
            for error in stats['errors']:
                print(f"  Event {error['event_id']}: {error['error']}")
        
        if stats['dead_letter'] > 0:
            print(f"[ImageGenerator] Moved to DLQ: {stats['dead_letter']}")
        
        return stats
        
    except Exception as e:
        print(f"[ImageGenerator] Error processing inbox events: {e}")
        raise


@celery_app.task(name="image_generator.cleanup_old_inbox_events")
def cleanup_old_inbox_events():
    """
    Cleans up old processed events from the inbox.
    Scheduled to run daily by Celery Beat.
    """
    processor = InboxProcessor()
    
    try:
        deleted = processor.cleanup_old_events(older_than_days=7)
        
        if deleted > 0:
            print(f"[ImageGenerator] Deleted {deleted} old processed events")
        
        return {'deleted': deleted}
        
    except Exception as e:
        print(f"[ImageGenerator] Error cleaning up old events: {e}")
        raise

