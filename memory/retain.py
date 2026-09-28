from .hindsight_client import HindsightMemoryClient

def retain_memory(text: str, metadata: dict = None, memory_id: str = None):
    """Retain a generic memory."""
    client = HindsightMemoryClient()
    return client.retain(document=text, metadata=metadata, document_id=memory_id)

def retain_customer_interaction(customer_id: str, interaction_type: str, summary: str, 
                               metadata: dict = None):
    """Retain a customer interaction memory."""
    meta = {
        'customer_id': customer_id,
        'interaction_type': interaction_type,
        **(metadata or {})
    }
    return retain_memory(
        text=summary,
        metadata=meta,
        memory_id=f'cust_{customer_id}_{interaction_type}'
    )

def retain_deal_memory(deal_id: str, event_type: str, description: str, 
                      metadata: dict = None):
    """Retain a deal-related memory."""
    meta = {
        'deal_id': deal_id,
        'event_type': event_type,
        **(metadata or {})
    }
    return retain_memory(
        text=description,
        metadata=meta,
        memory_id=f'deal_{deal_id}_{event_type}'
    )
