from app.utils.celery import celery_app
from app.services.inbox_processor import InboxProcessor


@celery_app.task(name="process_inbox_events")
def process_inbox_events():
    processor = InboxProcessor()
    
    try:
        stats = processor.process_inbox_events(batch_size=10)
        
        if stats['processed'] > 0:
            print(f"Processed events: {stats['succeeded']}/{stats['processed']}")
        
        if stats['failed'] > 0:
            print(f"Failed to process: {stats['failed']}")
            for error in stats['errors']:
                print(f"  Event {error['event_id']}: {error['error']}")
        
        return stats
        
    except Exception as e:
        print(f"Error processing inbox events: {e}")
        raise


@celery_app.task(name="cleanup_old_inbox_events")
def cleanup_old_inbox_events():
    processor = InboxProcessor()
    
    try:
        deleted = processor.cleanup_old_events(older_than_days=7)
        
        if deleted > 0:
            print(f"Deleted old events: {deleted}")
        
        return {'deleted': deleted}
        
    except Exception as e:
        print(f"Error cleaning up old events: {e}")
        raise
