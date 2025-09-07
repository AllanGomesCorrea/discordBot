from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Split:
    id: Optional[int]
    debtor: str
    creditor: str
    amount: float
    month: int
    year: int
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
