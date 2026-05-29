"""
Model interfaces for LLM evaluation.

Each provider module (``openai_models``, ``anthropic_models``,
``deepseek_models``, ``local_models``) has heavy optional dependencies
(``openai``, ``anthropic``, ``torch`` ...). We import them lazily so that the
top-level ``deterministic_horizon`` package can be imported with the slim
core requirements only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from deterministic_horizon.models.base import BaseModel, ModelResponse

if TYPE_CHECKING:  # pragma: no cover
    from deterministic_horizon.models.anthropic_models import AnthropicModel
    from deterministic_horizon.models.deepseek_models import DeepSeekModel
    from deterministic_horizon.models.local_models import LocalModel
    from deterministic_horizon.models.openai_models import OpenAIModel


# Lightweight registry: maps a normalised model-name fragment → "module:class"
# Resolved on demand in ``load_model``.
_REGISTRY: dict[str, tuple[str, str]] = {
    # OpenAI
    "gpt-4o": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "gpt-4o-mini": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "gpt-4-turbo": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "o1-preview": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "o1-mini": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "o3-mini": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    "o3": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
    # Anthropic
    "claude-3.5-sonnet": ("deterministic_horizon.models.anthropic_models", "AnthropicModel"),
    "claude-4.5-sonnet": ("deterministic_horizon.models.anthropic_models", "AnthropicModel"),
    "claude-4-opus": ("deterministic_horizon.models.anthropic_models", "AnthropicModel"),
    "claude-4.5-opus": ("deterministic_horizon.models.anthropic_models", "AnthropicModel"),
    # DeepSeek
    "deepseek-r1": ("deterministic_horizon.models.deepseek_models", "DeepSeekModel"),
    "deepseek-v3": ("deterministic_horizon.models.deepseek_models", "DeepSeekModel"),
    # Local / open weight (paper's open-weight suite)
    "llama-3.3-70b": ("deterministic_horizon.models.local_models", "LocalModel"),
    "llama-3.1-8b": ("deterministic_horizon.models.local_models", "LocalModel"),
    "qwen-2.5-72b": ("deterministic_horizon.models.local_models", "LocalModel"),
    "qwen-2.5-7b": ("deterministic_horizon.models.local_models", "LocalModel"),
}


class _LazyRegistry:
    """Dict-like view that resolves provider classes on demand."""

    def __iter__(self):
        return iter(_REGISTRY)

    def keys(self):
        return _REGISTRY.keys()

    def __contains__(self, key) -> bool:
        return key in _REGISTRY

    def __getitem__(self, key: str) -> type[BaseModel]:
        module_path, class_name = _REGISTRY[key]
        import importlib

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def items(self):
        for k in _REGISTRY:
            yield k, self[k]


MODEL_REGISTRY = _LazyRegistry()


def load_model(
    model_name: str,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    **kwargs,
) -> BaseModel:
    """
    Load a model by name. Optional dependencies are imported on demand.
    """
    normalised = model_name.lower().replace("_", "-")
    matched: str | None = None
    for registered in _REGISTRY:
        if registered in normalised or normalised in registered:
            matched = registered
            break

    if matched is None:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown model: {model_name}. Available: {available}")

    cls = MODEL_REGISTRY[matched]
    return cls(model_name=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)


def __getattr__(name: str):
    """Lazily import provider classes (avoids forcing optional deps)."""
    lazy = {
        "OpenAIModel": ("deterministic_horizon.models.openai_models", "OpenAIModel"),
        "AnthropicModel": (
            "deterministic_horizon.models.anthropic_models",
            "AnthropicModel",
        ),
        "DeepSeekModel": (
            "deterministic_horizon.models.deepseek_models",
            "DeepSeekModel",
        ),
        "LocalModel": ("deterministic_horizon.models.local_models", "LocalModel"),
    }
    if name in lazy:
        import importlib

        module_path, class_name = lazy[name]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    raise AttributeError(f"module 'deterministic_horizon.models' has no attribute {name!r}")


__all__ = [
    "BaseModel",
    "ModelResponse",
    "OpenAIModel",
    "AnthropicModel",
    "DeepSeekModel",
    "LocalModel",
    "load_model",
    "MODEL_REGISTRY",
]
