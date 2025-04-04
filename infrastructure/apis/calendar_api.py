"""
Calendar API Client implementations for Jarvis

This module provides implementations for calendar service APIs,
following the clean architecture patterns.
"""

import json
import os
import logging
import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger('jarvis.infrastructure.apis.calendar')

# Conditionally import Google Calendar API
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

class GoogleCalendarClient:
    """
    Client for the Google Calendar API
    """
    
    # If modifying these scopes, delete the token.json file
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def __init__(self, credentials_file: str, token_file: str = 'token.json'):
        """
        Initialize the Google Calendar client
        
        Args:
            credentials_file: Path to credentials.json file
            token_file: Path to token.json file for storing authorized user token
        """
        if not GOOGLE_CALENDAR_AVAILABLE:
            raise ImportError("Google Calendar API libraries not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
        # Initialize the calendar service
        self._initialize_service()
        
        logger.info("Google Calendar client initialized")
    
    def _initialize_service(self) -> None:
        """Initialize the Google Calendar service"""
        creds = None
        
        # Try to load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(self.token_file).read()),
                self.SCOPES
            )
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired credentials
                creds.refresh(Request())
            else:
                # Get new credentials
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Build the service
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_upcoming_events(self, max_results: int = 10, time_min: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
            time_min: Earliest time to include events for (defaults to now)
            
        Returns:
            List of calendar events
        """
        try:
            if not self.service:
                self._initialize_service()
                
            if not time_min:
                time_min = datetime.datetime.utcnow()
                
            time_min_str = time_min.isoformat() + 'Z'  # 'Z' indicates UTC time
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.debug(f"Retrieved {len(events)} upcoming events")
            return events
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return []
    
    def get_todays_events(self) -> List[Dict[str, Any]]:
        """
        Get events for today
        
        Returns:
            List of today's events
        """
        try:
            if not self.service:
                self._initialize_service()
                
            # Get today's date boundaries
            now = datetime.datetime.utcnow()
            start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + 'Z'
            end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.debug(f"Retrieved {len(events)} events for today")
            return events
            
        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return []
    
    def get_events_by_date(self, date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get events for a specific date
        
        Args:
            date: The date to get events for
            
        Returns:
            List of events for the specified date
        """
        try:
            if not self.service:
                self._initialize_service()
                
            # Get date boundaries
            start_of_day = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
            end_of_day = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.debug(f"Retrieved {len(events)} events for {date}")
            return events
            
        except Exception as e:
            logger.error(f"Error getting events for date {date}: {e}")
            return []