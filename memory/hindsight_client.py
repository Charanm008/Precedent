import os
from typing import Optional
from hindsight_client import Hindsight

class HindsightMemoryClient:
    _instance: Optional['HindsightMemoryClient'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        api_key = os.getenv('HINDSIGHT_API_KEY')
        base_url = os.getenv('HINDSIGHT_BASE_URL', 'https://api.hindsight.vectorize.io')
        bank_id = os.getenv('HINDSIGHT_BANK_ID')

        if not api_key:
            raise ValueError('HINDSIGHT_API_KEY environment variable is required')
        if not bank_id:
            raise ValueError('HINDSIGHT_BANK_ID environment variable is required')

        self.client = Hindsight(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0
        )
        self.bank_id = bank_id

    def retain(self, document: str, metadata: dict = None, document_id: str = None):
        """Retain a memory in the bank."""
        # SDK: retain(content, context=None, metadata=None, document_id=None, timestamp=None, bank_id=None)
        return self.client.retain(
            content=document,
            context=None,
            metadata=metadata or {},
            document_id=document_id,
            bank_id=self.bank_id
        )

    def recall(self, query: str, limit: int = 10, metadata_filter: dict = None):
        """Recall memories from the bank."""
        # SDK returns object with .results attribute
        return self.client.recall(
            query=query,
            limit=limit,
            # metadata_filter may not be supported; we'll apply client-side later if needed
        )

    def list_memories(self, limit: int = 100, offset: int = 0):
        """List memories in the bank."""
        return self.client.list_memories(limit=limit, offset=offset, bank_id=self.bank_id)

    def create_bank(self, bank_id: str = None):
        """Create a bank if it doesn't exist."""
        target_bank_id = bank_id or self.bank_id
        return self.client.create_bank(bank_id=target_bank_id)
