from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Expense:
    id: Optional[int]
    value: float
    description: str
    paid_by: str
    month: int
    year: int
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
