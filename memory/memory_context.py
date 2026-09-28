def memories_to_context(memories: list) -> str:
    """Convert a list of memory objects into a compact context string."""
    if not memories:
        return "No relevant memories found."
    
    context_parts = []
    for i, mem in enumerate(memories, 1):
        # Each memory is dict with keys: text, type, metadata
        text = mem.get('text') if isinstance(mem, dict) else getattr(mem, 'text', '')
        mem_type = mem.get('type') if isinstance(mem, dict) else getattr(mem, 'type', None)
        meta = mem.get('metadata') if isinstance(mem, dict) else getattr(mem, 'metadata', {})
        # Build a readable line
        parts = []
        if mem_type:
            parts.append(f"[{mem_type}]")
        parts.append(str(text))
        if meta:
            # Filter out internal keys if needed
            meta_str = ", ".join(f"{k}={v}" for k, v in meta.items() if not k.startswith('_'))
            if meta_str:
                parts.append(f"({meta_str})")
        context_parts.append(" ".join(parts))
    
    return "\n".join(context_parts)

def memories_to_dict_list(memories: list) -> list:
    """Convert memories to a list of dictionaries for structured context."""
    if not memories:
        return []
    # If already dicts, return as is; else try to convert
    if memories and isinstance(memories[0], dict):
        return memories
    # Attempt to convert objects with __dict__
    result = []
    for mem in memories:
        if hasattr(mem, '__dict__'):
            result.append(mem.__dict__)
        else:
            # Fallback: treat as dict if possible
            result.append(dict(mem))
    return result
