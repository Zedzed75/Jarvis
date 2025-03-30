#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point

This is the entry point for the Jarvis assistant application. It initializes
all necessary components and starts the assistant.
"""

import os
import sys
import logging
import argparse
import signal
from pathlib import Path

# Infrastructure layer
from infrastructure.config.config_manager import ConfigManager
from infrastructure.notifications.factory import create_notification_service

# Application layer
from application.services.notification_service import NotificationService
from application.services.assistant_service import AssistantService

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jarvis.log')
    ]
)
logger = logging.getLogger('jarvis')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Jarvis AI Assistant')
    parser.add_argument(
        '--config', 
        type=str, 
        default=os.path.join('config', 'assistant.yaml'),
        help='Path to configuration file'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode'
    )
    parser.add_argument(
        '--no-voice', 
        action='store_true', 
        help='Disable voice and use text mode only'
    )
    return parser.parse_args()

def signal_handler(sig, frame):
    """Handle interrupt signal."""
    logger.info("Shutting down Jarvis...")
    sys.exit(0)

def main():
    """Main function."""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse arguments
    args = parse_arguments()
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger('jarvis').setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Load configuration
    try:
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize services
    try:
        # Initialize notification service if configured
        notification_provider = create_notification_service(config.get('notifications', {}))
        notification_service = NotificationService(notification_provider) if notification_provider else None
        
        if notification_service:
            logger.info("Notification service initialized")
        else:
            logger.warning("Notification service not available")
            
        # Initialize and start assistant
        assistant = AssistantService(
            config=config,
            text_mode=args.no_voice,
            notification_service=notification_service
        )
        
        # Send startup notification if notifications are enabled
        if notification_service:
            notification_service.notify("Jarvis is now online and ready to assist you.")
        
        # Start assistant
        logger.info("Starting Jarvis...")
        assistant.start()
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()