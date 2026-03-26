"""Tests for AI cost calculator."""
from decimal import Decimal

import pytest

from api.ai.cost_calculator import DEFAULT_PRICING, MODEL_PRICING, calculate_llm_cost


class TestCalculateLlmCost:
    def test_known_model_uses_correct_pricing(self):
        cost = calculate_llm_cost(input_tokens=1_000_000, output_tokens=0, model='gpt-4o')
        assert cost == MODEL_PRICING['gpt-4o']['input']

    def test_output_tokens_priced_correctly(self):
        cost = calculate_llm_cost(input_tokens=0, output_tokens=1_000_000, model='gpt-4o')
        assert cost == MODEL_PRICING['gpt-4o']['output']

    def test_combined_cost(self):
        pricing = MODEL_PRICING['gpt-4o']
        expected = (Decimal('500000') / Decimal('1000000')) * pricing['input'] + \
                   (Decimal('500000') / Decimal('1000000')) * pricing['output']
        cost = calculate_llm_cost(500_000, 500_000, 'gpt-4o')
        assert cost == expected

    def test_unknown_model_uses_default_pricing(self):
        cost = calculate_llm_cost(1_000_000, 0, 'some-unknown-model-xyz')
        assert cost == DEFAULT_PRICING['input']

    def test_zero_tokens_returns_zero(self):
        cost = calculate_llm_cost(0, 0, 'gpt-4o')
        assert cost == Decimal('0')

    def test_returns_decimal(self):
        cost = calculate_llm_cost(1000, 500, 'gpt-4o')
        assert isinstance(cost, Decimal)

    def test_anthropic_model_priced(self):
        cost = calculate_llm_cost(1_000_000, 0, 'claude-sonnet-4-6')
        assert cost == MODEL_PRICING['claude-sonnet-4-6']['input']

    def test_small_token_count_precision(self):
        # 100 input tokens at $3/1M = $0.0000003
        cost = calculate_llm_cost(100, 0, 'claude-sonnet-4-6')
        assert cost == Decimal('100') / Decimal('1000000') * Decimal('3.00')
