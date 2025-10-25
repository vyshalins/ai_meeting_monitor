def get_meeting_duration(start_time: str, end_time: str) -> float:
    from datetime import datetime

    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    duration = (end - start).total_seconds() / 60  # duration in minutes
    return duration

def format_meeting_notes(notes: str) -> str:
    return notes.strip().replace('\n', ' ').replace('  ', ' ')

def validate_meeting_data(meeting_data: dict) -> bool:
    required_fields = ['title', 'start_time', 'end_time', 'participants']
    return all(field in meeting_data for field in required_fields)