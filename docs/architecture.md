# Precedent Architecture

## Phase 2: Persistent Memory

### Overview
Phase 2 introduces a persistent memory layer using the Hindsight client to store and retrieve contextual information about customers, deals, and interactions.

### Component Diagram

#### Memory Storage Flow
`
Application
    ?
retain.py
    ?
hindsight_client.py
    ?
Hindsight Memory Bank
`

#### Memory Retrieval Flow
`
Application / Agent
    ?
recall.py
    ?
hindsight_client.py
    ?
Hindsight Recall
    ?
memory_context.py
    ?
Agent Context
`

### Details

#### memory/hindsight_client.py
- Singleton wrapper around the official hindsight-client Python package.
- Reads configuration from environment variables:
  - HINDSIGHT_API_KEY (required)
  - HINDSIGHT_BASE_URL (defaults to Hindsight Cloud)
  - HINDSIGHT_BANK_ID (required)
- Provides methods for etain, ecall, list_memories, and create_bank.

#### memory/retain.py
- Application-level functions for storing different types of memories:
  - etain_memory: generic memory storage.
  - etain_customer_interaction: stores customer-specific interactions.
  - etain_deal_memory: stores deal-related memories.
- Functions format metadata and document IDs appropriately before delegating to the Hindsight client.

#### memory/recall.py
- Functions for querying memories:
  - ecall_memories: general recall with optional filtering.
  - ecall_customer_memories: recall filtered by customer ID.
  - ecall_deal_memories: recall filtered by deal ID.
  - ecall_relevant_memories: alias for general recall.
- Returns structured data from Hindsight's recall operation.

#### memory/memory_context.py
- Provider-independent helpers to convert recalled memories into contexts:
  - memories_to_context: produces a compact, readable string.
  - memories_to_dict_list: returns memories as a list of dictionaries for structured use.

### Integration with Phase 1
- Phase 1's deal-management endpoints can invoke Phase 2's memory functions to store interaction histories.
- Agents or services in Phase 1 can retrieve relevant memories to enrich deal context (e.g., past customer objections, negotiation outcomes).
- No direct modifications to Phase 1 code are required; integration is via function calls.

### Dependencies
- hindsight-client: official Python client for Hindsight memory platform.

### Configuration
- Add to .env (not committed):
  `
  HINDSIGHT_API_KEY=your_key_here
  HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
  HINDSIGHT_BANK_ID=precedent-demo
  `
- See .env.example for variable names and defaults.


