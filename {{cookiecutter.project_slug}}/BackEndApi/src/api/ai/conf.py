"""AI app settings — OpenAI and Anthropic configuration lives here."""
from django.conf import settings


class AISettings:
    @property
    def openai_api_key(self):
        return getattr(settings, 'OPENAI_API_KEY', None)

    @property
    def openai_model(self):
        return getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')

    @property
    def openai_temperature(self):
        return getattr(settings, 'OPENAI_TEMPERATURE', 0.7)

    @property
    def openai_max_tokens(self):
        return getattr(settings, 'OPENAI_MAX_TOKENS', 20000)

    @property
    def anthropic_api_key(self):
        return getattr(settings, 'ANTHROPIC_API_KEY', None)

    @property
    def anthropic_model(self):
        return getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929')

    @property
    def anthropic_max_tokens(self):
        return getattr(settings, 'ANTHROPIC_MAX_TOKENS', 8000)


ai_settings = AISettings()
