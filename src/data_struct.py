from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class BaseData:
    def to_dict(self):
        return asdict(self)

@dataclass
class LineOfLogFile(BaseData):
    content: str
    line_number: int
    name: str
    id: int
    timestamp: datetime

    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to strings
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()  # Convert to ISO 8601 format
        return data

@dataclass
class LastLineRead(BaseData):
    last_line_read: int
    id: int
    name: str
