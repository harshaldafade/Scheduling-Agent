# Enhanced Date Handling Guide

## Overview

The Scheduling Agent now includes comprehensive date and time context handling, allowing users to schedule meetings using natural language with relative dates and times. The system automatically converts relative references to absolute dates and times while maintaining timezone awareness.

## Key Features

### 1. Relative Date Parsing
The agent understands and processes various relative date formats:

#### Basic Relative Dates
- **"today"** → Current date
- **"tomorrow"** → Current date + 1 day
- **"next week"** → Current date + 7 days
- **"in X days"** → Current date + X days

#### Day-Specific References
- **"next Monday"** → Next occurrence of Monday
- **"next Tuesday"** → Next occurrence of Tuesday
- **"this Friday"** → Friday of current week
- **"next Friday"** → Friday of next week

#### Combined Date-Time Formats
- **"today at 2pm"** → Today at 2:00 PM
- **"tomorrow at 10am"** → Tomorrow at 10:00 AM
- **"next Monday at 3pm"** → Next Monday at 3:00 PM
- **"in 3 days at 1pm"** → 3 days from now at 1:00 PM

### 2. Time Parsing
The system handles various time formats:

#### 12-Hour Format
- **"2pm"** → 2:00 PM
- **"2:30pm"** → 2:30 PM
- **"9am"** → 9:00 AM
- **"12pm"** → 12:00 PM
- **"12am"** → 12:00 AM

#### 24-Hour Format
- **"14:00"** → 2:00 PM
- **"14:30"** → 2:30 PM
- **"09:00"** → 9:00 AM

### 3. Context-Aware Processing
The agent provides comprehensive date context to the AI:

```
Current Date: Friday, June 27, 2025
Current Time: 04:43 AM
Current Day: Friday

Date References:
- Today: 2025-06-27
- Tomorrow: 2025-06-28 (Saturday)
- Next Week: 2025-07-04

Next Occurrences:
- Next Monday: 2025-06-30
- Next Tuesday: 2025-07-01
- Next Wednesday: 2025-07-02
- Next Thursday: 2025-07-03
- Next Friday: 2025-07-04
- Next Saturday: 2025-06-28
- Next Sunday: 2025-06-29

Business Hours: 9:00 AM - 17:00 PM
```

### 4. Timezone Awareness
- Default timezone: UTC (configurable)
- All dates are stored with timezone information
- Consistent handling across different timezones

### 5. Business Hours Consideration
- Default business hours: 9:00 AM - 5:00 PM
- When no specific time is provided, defaults to 9:00 AM
- Helps ensure meetings are scheduled during appropriate hours

## Usage Examples

### Natural Language Scheduling
Users can now schedule meetings using natural language:

```
"Schedule a team meeting tomorrow at 2pm"
"Book a call with John next Monday at 10am"
"Set up a project review this Friday"
"Create a meeting in 3 days at 1:30pm"
"Schedule a weekly standup next Tuesday"
```

### Meeting Management
The agent can handle date-aware meeting operations:

```
"Reschedule my 2pm meeting to tomorrow"
"Move the team meeting to next Monday"
"Cancel the meeting scheduled for today"
"Show me my meetings for next week"
```

## Technical Implementation

### Core Methods

#### `_parse_relative_datetime(datetime_str: str) → datetime`
Parses relative datetime strings into absolute datetime objects.

#### `_parse_time_string(time_str: str) → datetime.time`
Parses time strings into datetime.time objects.

#### `_process_meeting_dates(meeting_data: Dict) → Dict`
Processes meeting data to convert relative dates to absolute dates.

#### `_get_date_context(current_date: datetime) → str`
Generates comprehensive date context for AI processing.

### Error Handling
- Graceful fallback to current time if parsing fails
- Logging of parsing errors for debugging
- Default values for missing time information

### Edge Cases Handled
- Invalid date formats
- Missing time information
- Timezone conversions
- Business hour constraints
- Weekend scheduling considerations

## Configuration

### Timezone Settings
```python
self.timezone = pytz.timezone('UTC')  # Default timezone
```

### Business Hours
```python
business_start = 9  # 9 AM
business_end = 17   # 5 PM
```

### Default Times
- When no time specified: Current time for "today", 9 AM for other dates
- When no date specified: Today's date

## Testing

Run the test script to verify date handling capabilities:

```bash
python test_date_handling.py
```

This will demonstrate:
- Relative date parsing
- Time string parsing
- Meeting data processing
- Complex date scenarios
- Error handling

## Benefits

1. **User-Friendly**: Natural language scheduling without complex date formats
2. **Intelligent**: Context-aware date processing
3. **Flexible**: Handles various input formats
4. **Reliable**: Robust error handling and fallbacks
5. **Consistent**: Timezone-aware and standardized output
6. **Business-Ready**: Considers business hours and constraints

## Future Enhancements

Potential improvements could include:
- User-specific timezone preferences
- Custom business hours per user
- Holiday calendar integration
- Recurring meeting patterns
- Multi-timezone meeting coordination
- Calendar integration (Google Calendar, Outlook, etc.)

## Integration with Existing Features

The enhanced date handling integrates seamlessly with:
- Meeting creation and scheduling
- Conflict detection and resolution
- Alternative time suggestions
- Meeting updates and rescheduling
- Calendar display and management

This enhancement makes the scheduling agent much more user-friendly and intelligent, allowing users to interact with it using natural language while maintaining precise date and time handling. 