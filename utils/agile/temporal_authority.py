#!/usr/bin/env python3
"""
Temporal Authority - Single Source of Truth for All Time Operations
Implements the Temporal Trust Rule across all agile artifact generation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TemporalTrustViolation(Exception):
    """Raised when temporal trust rules are violated."""
    pass

class SystemTimeAuthority:
    """
    The definitive temporal reference for all system operations.
    Implements the Temporal Trust Rule: Always trust the local machine's time.
    """
    
    def __init__(self):
        """Initialize temporal authority with system trust."""
        self._validate_system_time_access()
        logger.debug("SystemTimeAuthority initialized - trusting local machine")
    
    def _validate_system_time_access(self):
        """Ensure we can access system time."""
        try:
            current_time = datetime.now()
            assert isinstance(current_time, datetime)
        except Exception as e:
            raise TemporalTrustViolation(f"Cannot access system time: {e}")
    
    def now(self) -> datetime:
        """Get authoritative current time from local machine."""
        return datetime.now()  # Always trust the machine
    
    def today(self) -> str:
        """Get current date in ISO format."""
        return self.now().strftime('%Y-%m-%d')
    
    def timestamp(self) -> str:
        """Get current datetime in standard format."""
        return self.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def iso_timestamp(self) -> str:
        """Get current datetime in ISO format."""
        return self.now().isoformat()
    
    def artifact_timestamp(self) -> str:
        """Get timestamp formatted for artifact creation."""
        return self.now().strftime('%Y-%m-%d %H:%M')
    
    def sprint_dates(self, sprint_length_days: int) -> Dict[str, str]:
        """Calculate sprint dates from current system time."""
        start_date = self.now()
        end_date = start_date + timedelta(days=sprint_length_days)
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'start_datetime': start_date.strftime('%Y-%m-%d %H:%M'),
            'end_datetime': end_date.strftime('%Y-%m-%d %H:%M')
        }
    
    def file_timestamp(self) -> str:
        """Get timestamp suitable for filenames."""
        return self.now().strftime('%Y%m%d_%H%M%S')
    
    def creation_metadata(self, agent_name: str = "AgileAgent") -> Dict[str, str]:
        """Standard creation metadata for all artifacts."""
        current_time = self.now()
        
        return {
            'created_date': current_time.strftime('%Y-%m-%d'),
            'created_timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'created_datetime': current_time.strftime('%Y-%m-%d %H:%M'),
            'iso_timestamp': current_time.isoformat(),
            'agent_id': agent_name,
            'temporal_authority': 'local_machine'
        }
    
    def time_range(self, start_offset_days: int = 0, end_offset_days: int = 14) -> Dict[str, str]:
        """Get time range relative to current system time."""
        base_time = self.now()
        start_time = base_time + timedelta(days=start_offset_days)
        end_time = base_time + timedelta(days=end_offset_days)
        
        return {
            'start_date': start_time.strftime('%Y-%m-%d'),
            'end_date': end_time.strftime('%Y-%m-%d'),
            'start_datetime': start_time.strftime('%Y-%m-%d %H:%M'),
            'end_datetime': end_time.strftime('%Y-%m-%d %H:%M'),
            'duration_days': end_offset_days - start_offset_days
        }

# Global temporal authority instance - single source of truth
TEMPORAL_AUTHORITY = SystemTimeAuthority()

def get_temporal_authority() -> SystemTimeAuthority:
    """Get the global temporal authority instance."""
    return TEMPORAL_AUTHORITY

def validate_temporal_compliance(content: str) -> bool:
    """Validate that content contains real system timestamps."""
    import re
    
    # Check for placeholder dates
    forbidden_patterns = [
        r'\[DATE\]', r'\[TIMESTAMP\]', r'TODO.*date', r'TBD.*date',
        r'2024-01-01',  # Obviously fake dates
        r'1900-01-01', r'2000-01-01',
        r'YYYY-MM-DD', r'HH:MM:SS'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            raise TemporalTrustViolation(f"Placeholder temporal data detected: {pattern}")
    
    # Verify current year is present
    current_year = TEMPORAL_AUTHORITY.now().year
    if str(current_year) not in content:
        logger.warning(f"Current system year {current_year} not found in artifact content")
    
    return True

def temporal_compliance_decorator(func):
    """Decorator to enforce temporal trust in artifact generation."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # If result contains generated content, validate it
        if isinstance(result, str):
            validate_temporal_compliance(result)
        elif isinstance(result, dict) and 'content' in result:
            validate_temporal_compliance(result['content'])
        
        return result
    return wrapper
