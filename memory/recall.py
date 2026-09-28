from .hindsight_client import HindsightMemoryClient
from typing import List, Dict, Any

def recall_memories(query: str, limit: int = 10, metadata_filter: dict = None) -> List[Dict[str, Any]]:
    """Recall memories matching the query."""
    client = HindsightMemoryClient()
    result = client.recall(query=query, limit=limit)
    # Official SDK returns object with .results list; each memory has .text and .type
    memories = []
    if hasattr(result, 'results'):
        for mem in result.results:
            memories.append({
                'text': getattr(mem, 'text', ''),
                'type': getattr(mem, 'type', None),
                # If there is metadata, include it; otherwise empty dict
                'metadata': getattr(mem, 'metadata', {})
            })
    else:
        # Fallback if result is already a list (for mocking)
        memories = result if isinstance(result, list) else []
    # Apply client-side metadata filtering if needed (since SDK may not support it)
    if metadata_filter:
        filtered = []
        for mem in memories:
            match = True
            for k, v in metadata_filter.items():
                if mem.get('metadata', {}).get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(mem)
        memories = filtered
    # Apply limit after filtering (client-side)
    if limit is not None:
        memories = memories[:limit]
    return memories

def recall_customer_memories(customer_id: str, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Recall memories for a specific customer."""
    metadata_filter = {'customer_id': customer_id} if customer_id else None
    return recall_memories(query=query or '', limit=limit, metadata_filter=metadata_filter)

def recall_deal_memories(deal_id: str, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Recall memories for a specific deal."""
    metadata_filter = {'deal_id': deal_id} if deal_id else None
    return recall_memories(query=query or '', limit=limit, metadata_filter=metadata_filter)

def recall_relevant_memories(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Alias for recall_memories for clarity."""
    return recall_memories(query=query, limit=limit)
