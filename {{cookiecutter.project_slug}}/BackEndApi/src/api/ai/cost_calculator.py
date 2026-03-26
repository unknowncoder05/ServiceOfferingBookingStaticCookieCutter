"""LLM cost calculation based on token usage and model pricing."""
from decimal import Decimal

# Pricing per 1M tokens in USD
# Source: Official provider pricing pages
MODEL_PRICING = {
    # OpenAI
    'gpt-4o':        {'input': Decimal('2.50'),  'output': Decimal('10.00')},
    'gpt-4o-mini':   {'input': Decimal('0.15'),  'output': Decimal('0.60')},
    'gpt-4-turbo':   {'input': Decimal('10.00'), 'output': Decimal('30.00')},
    'gpt-4':         {'input': Decimal('30.00'), 'output': Decimal('60.00')},
    'gpt-3.5-turbo': {'input': Decimal('0.50'),  'output': Decimal('1.50')},
    # Anthropic
    'claude-opus-4-6':           {'input': Decimal('15.00'), 'output': Decimal('75.00')},
    'claude-sonnet-4-6':         {'input': Decimal('3.00'),  'output': Decimal('15.00')},
    'claude-haiku-4-5-20251001': {'input': Decimal('0.80'),  'output': Decimal('4.00')},
    'claude-3-5-sonnet-20241022': {'input': Decimal('3.00'), 'output': Decimal('15.00')},
    'claude-3-5-haiku-20241022':  {'input': Decimal('0.80'), 'output': Decimal('4.00')},
}

# Fallback pricing when model is not found in the table
DEFAULT_PRICING = {'input': Decimal('3.00'), 'output': Decimal('15.00')}

PER_MILLION = Decimal('1000000')


def calculate_llm_cost(input_tokens, output_tokens, model):
    """Calculate the USD cost of an LLM API call.

    Args:
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens
        model: Model name string

    Returns:
        Decimal cost in USD
    """
    pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
    input_cost = (Decimal(str(input_tokens)) / PER_MILLION) * pricing['input']
    output_cost = (Decimal(str(output_tokens)) / PER_MILLION) * pricing['output']
    return input_cost + output_cost
