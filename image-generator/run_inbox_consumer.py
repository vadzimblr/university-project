#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.services.prompt_extracted_consumer import main

if __name__ == '__main__':
    print("Starting Inbox Consumer for image-generator...")
    print("Listening for prompt.extracted events from sd-prompt-generator")
    print("Press Ctrl+C to stop\n")
    main()
