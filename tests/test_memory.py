import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory.hindsight_client import HindsightMemoryClient
from memory.retain import retain_memory, retain_customer_interaction, retain_deal_memory
from memory.recall import recall_memories, recall_customer_memories, recall_deal_memories, recall_relevant_memories
from memory.memory_context import memories_to_context, memories_to_dict_list

class TestHindsightMemoryClient(unittest.TestCase):
    def setUp(self):
        # Reset singleton between tests
        HindsightMemoryClient._instance = None

    @patch('memory.hindsight_client.Hindsight')
    def test_singleton(self, MockHindsight):
        client1 = HindsightMemoryClient()
        client2 = HindsightMemoryClient()
        self.assertIs(client1, client2)

    @patch('memory.hindsight_client.Hindsight')
    def test_init_missing_api_key(self, MockHindsight):
        os.environ.pop('HINDSIGHT_API_KEY', None)
        with self.assertRaises(ValueError):
            HindsightMemoryClient()

    @patch('memory.hindsight_client.Hindsight')
    def test_init_missing_bank_id(self, MockHindsight):
        os.environ.pop('HINDSIGHT_BANK_ID', None)
        with self.assertRaises(ValueError):
            HindsightMemoryClient()

    @patch('memory.hindsight_client.Hindsight')
    def test_retain(self, MockHindsight):
        mock_instance = MagicMock()
        MockHindsight.return_value = mock_instance
        os.environ['HINDSIGHT_API_KEY'] = 'test-key'
        os.environ['HINDSIGHT_BANK_ID'] = 'test-bank'
        client = HindsightMemoryClient()
        result = client.retain('test doc', {'key': 'value'}, 'doc1')
        mock_instance.retain.assert_called_once_with(
            content='test doc',
            context=None,
            metadata={'key': 'value'},
            document_id='doc1',
            bank_id='test-bank'
        )
        self.assertEqual(result, mock_instance.retain.return_value)

    @patch('memory.hindsight_client.Hindsight')
    def test_recall(self, MockHindsight):
        mock_instance = MagicMock()
        MockHindsight.return_value = mock_instance
        os.environ['HINDSIGHT_API_KEY'] = 'test-key'
        os.environ['HINDSIGHT_BANK_ID'] = 'test-bank'
        client = HindsightMemoryClient()
        # Mock recall return object with .results
        mock_result = MagicMock()
        mock_result.results = []
        mock_instance.recall.return_value = mock_result
        result = client.recall('test query', limit=5)
        mock_instance.recall.assert_called_once_with(
            query='test query',
            limit=5
        )
        self.assertEqual(result, mock_result)

    @patch('memory.hindsight_client.Hindsight')
    def test_list_memories(self, MockHindsight):
        mock_instance = MagicMock()
        MockHindsight.return_value = mock_instance
        os.environ['HINDSIGHT_API_KEY'] = 'test-key'
        os.environ['HINDSIGHT_BANK_ID'] = 'test-bank'
        client = HindsightMemoryClient()
        result = client.list_memories(limit=10, offset=0)
        mock_instance.list_memories.assert_called_once_with(
            limit=10,
            offset=0,
            bank_id='test-bank'
        )
        self.assertEqual(result, mock_instance.list_memories.return_value)

    @patch('memory.hindsight_client.Hindsight')
    def test_create_bank(self, MockHindsight):
        mock_instance = MagicMock()
        MockHindsight.return_value = mock_instance
        os.environ['HINDSIGHT_API_KEY'] = 'test-key'
        os.environ['HINDSIGHT_BANK_ID'] = 'test-bank'
        client = HindsightMemoryClient()
        result = client.create_bank()
        mock_instance.create_bank.assert_called_once_with(bank_id='test-bank')
        self.assertEqual(result, mock_instance.create_bank.return_value)

class TestRetainFunctions(unittest.TestCase):
    @patch('memory.retain.HindsightMemoryClient')
    def test_retain_memory(self, MockClient):
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.retain.return_value = {'id': '123'}
        result = retain_memory('hello', metadata={'a':1}, memory_id='m1')
        mock_client.retain.assert_called_once_with(document='hello', metadata={'a':1}, document_id='m1')
        self.assertEqual(result, {'id': '123'})

    @patch('memory.retain.retain_memory')
    def test_retain_customer_interaction(self, mock_retain):
        mock_retain.return_value = {'id': '456'}
        result = retain_customer_interaction('cust123', 'call', 'Discussed pricing', {'duration': '10min'})
        # retain_memory(text, metadata, memory_id)
        args, kwargs = mock_retain.call_args
        self.assertEqual(kwargs['text'], 'Discussed pricing')
        self.assertEqual(kwargs['metadata']['customer_id'], 'cust123')
        self.assertEqual(kwargs['metadata']['interaction_type'], 'call')
        self.assertEqual(kwargs['metadata']['duration'], '10min')
        self.assertEqual(kwargs['memory_id'], 'cust_cust123_call')
        self.assertEqual(result, {'id': '456'})

    @patch('memory.retain.retain_memory')
    def test_retain_deal_memory(self, mock_retain):
        mock_retain.return_value = {'id': '789'}
        result = retain_deal_memory('deal456', 'negotiation', 'Agreed on terms', {'amount': 5000})
        args, kwargs = mock_retain.call_args
        self.assertEqual(kwargs['text'], 'Agreed on terms')
        self.assertEqual(kwargs['metadata']['deal_id'], 'deal456')
        self.assertEqual(kwargs['metadata']['event_type'], 'negotiation')
        self.assertEqual(kwargs['metadata']['amount'], 5000)
        self.assertEqual(kwargs['memory_id'], 'deal_deal456_negotiation')
        self.assertEqual(result, {'id': '789'})

class TestRecallFunctions(unittest.TestCase):
    @patch('memory.recall.HindsightMemoryClient')
    def test_recall_memories(self, MockClient):
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        # Mock recall return object with .results containing two memory objects
        mock_mem1 = MagicMock()
        mock_mem1.text = 'hello'
        mock_mem1.type = 'note'
        mock_mem1.metadata = {'src': 'test'}
        mock_mem2 = MagicMock()
        mock_mem2.text = 'world'
        mock_mem2.type = 'note'
        mock_mem2.metadata = {}
        mock_result = MagicMock()
        mock_result.results = [mock_mem1, mock_mem2]
        mock_client.recall.return_value = mock_result
        result = recall_memories('query', limit=5)
        # Should have applied client-side filtering (none) and limit
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['text'], 'hello')
        self.assertEqual(result[0]['type'], 'note')
        self.assertEqual(result[0]['metadata'], {'src': 'test'})
        self.assertEqual(result[1]['text'], 'world')
        self.assertEqual(result[1]['type'], 'note')
        self.assertEqual(result[1]['metadata'], {})
        mock_client.recall.assert_called_once_with(query='query', limit=5)

    @patch('memory.recall.recall_memories')
    def test_recall_customer_memories(self, mock_recall):
        mock_recall.return_value = [{'text': 'x', 'type': 't', 'metadata': {'customer_id': 'c1'}}]
        result = recall_customer_memories('cust99', query='hello', limit=3)
        mock_recall.assert_called_once_with(query='hello', limit=3, metadata_filter={'customer_id': 'cust99'})
        self.assertEqual(result, [{'text': 'x', 'type': 't', 'metadata': {'customer_id': 'c1'}}])

    @patch('memory.recall.recall_memories')
    def test_recall_deal_memories(self, mock_recall):
        mock_recall.return_value = [{'text': 'x', 'type': 't', 'metadata': {'deal_id': 'd1'}}]
        result = recall_deal_memories('deal88', query='bye', limit=1)
        mock_recall.assert_called_once_with(query='bye', limit=1, metadata_filter={'deal_id': 'deal88'})
        self.assertEqual(result, [{'text': 'x', 'type': 't', 'metadata': {'deal_id': 'd1'}}])

    @patch('memory.recall.recall_memories')
    def test_recall_relevant_memories(self, mock_recall):
        mock_recall.return_value = [{'text': 'test'}]
        result = recall_relevant_memories('test query', limit=7)
        mock_recall.assert_called_once_with(query='test query', limit=7)
        self.assertEqual(result, [{'text': 'test'}])

class TestMemoryContext(unittest.TestCase):
    def test_memories_to_context_empty(self):
        self.assertEqual(memories_to_context([]), "No relevant memories found.")

    def test_memories_to_context_with_data(self):
        memories = [
            {'text': 'Customer likes coffee', 'type': 'preference', 'metadata': {'customer_id': '1'}},
            {'text': 'Customer dislikes tea', 'type': 'preference', 'metadata': {'customer_id': '1', 'source': 'survey'}}
        ]
        context = memories_to_context(memories)
        self.assertIn('[preference] Customer likes coffee', context)
        self.assertIn('[preference] Customer dislikes tea', context)
        self.assertIn('customer_id=1', context)
        self.assertIn('source=survey', context)

    def test_memories_to_dict_list(self):
        # Already dicts
        mem = [{'a': 1}, {'b': 2}]
        self.assertEqual(memories_to_dict_list(mem), mem)
        # Objects with __dict__
        class Dummy:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
        mem2 = [Dummy(x=1), Dummy(y=2)]
        result = memories_to_dict_list(mem2)
        self.assertEqual(result, [{'x': 1}, {'y': 2}])

if __name__ == '__main__':
    unittest.main()
