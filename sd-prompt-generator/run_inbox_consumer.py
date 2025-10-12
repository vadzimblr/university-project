#!/usr/bin/env python3

import sys
import logging
from app.services.inbox_consumer import SceneEventsInboxConsumer, get_rabbitmq_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Inbox Consumer for sd-prompt-generator")
    
    try:
        connection = get_rabbitmq_connection()
        consumer = SceneEventsInboxConsumer(connection)
        
        logger.info("Consumer started and waiting for events")
        logger.info("  Subscription: scene.saved from exchange 'scene_saved_events'")
        logger.info("  Queue: sd_prompt_generator_scene_saved")
        logger.info("\nPress Ctrl+C to stop\n")
        
        consumer.run()
        
    except KeyboardInterrupt:
        logger.info("\nShutdown signal received")
        logger.info("Consumer stopped gracefully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

