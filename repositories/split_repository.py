from abc import ABC, abstractmethod
from typing import List, Optional
from models.split import Split

class SplitRepository(ABC):
    @abstractmethod
    async def save_splits(self, splits: List[Split]) -> None:
        """Salva uma lista de splits, sobrescrevendo os existentes do mesmo mês/ano"""
        pass
    
    @abstractmethod
    async def get_splits_by_month(self, month: int, year: int) -> List[Split]:
        """Busca splits por mês e ano"""
        pass
    
    @abstractmethod
    async def delete_splits_by_month(self, month: int, year: int) -> None:
        """Remove todos os splits de um mês/ano específico"""
        pass
