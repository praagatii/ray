from ray.reasoning.providers.test_provider import TestProvider

try:
    from ray.reasoning.providers.ollama_provider import OllamaProvider
except Exception:
    OllamaProvider = None

from ray import config


def get_provider():
    provider_name = config.MODEL_PROVIDER

    if provider_name == "ollama" and OllamaProvider is not None:
        try:
            provider = OllamaProvider()
            return provider
        except Exception:
            print("Warning: Ollama unavailable, falling back to TestProvider.")

    return TestProvider()
