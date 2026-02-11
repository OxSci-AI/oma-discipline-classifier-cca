#!/usr/bin/env python3
"""
Prompt Manager for Discipline Classifier Agent

Manages prompt templates loaded from YAML configuration.
Provides centralized prompt management for all LLM interactions.

Supports:
- Discipline classifier prompts (prompts_discipline_classifier.yaml)
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from oxsci_shared_core.logging import logger


# Path constants
PROMPTS_DISCIPLINE_CLASSIFIER_FILE = Path(__file__).parent / "prompts_discipline_classifier.yaml"


class PromptManager:
    """Manages prompt templates loaded from YAML configuration."""

    def __init__(
        self,
        prompts_file: Path = PROMPTS_DISCIPLINE_CLASSIFIER_FILE,
    ):
        self._prompts: Dict[str, Any] = {}
        self._load_prompts(prompts_file)

    def _load_prompts(self, prompts_file: Path) -> None:
        """Load prompts from YAML file."""
        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

        with open(prompts_file, "r", encoding="utf-8") as f:
            self._prompts = yaml.safe_load(f)

        logger.info(f"Loaded prompts from {prompts_file}")

    def get_prompt(self, prompt_key: str, **kwargs: Any) -> str:
        """Get a prompt template and format it with provided parameters.

        Args:
            prompt_key: Key identifying the prompt (e.g., 'paper_content_extraction')
            **kwargs: Parameters to substitute in the template

        Returns:
            Formatted prompt string
        """
        if prompt_key not in self._prompts:
            raise KeyError(f"Prompt '{prompt_key}' not found in configuration")

        prompt_config = self._prompts[prompt_key]
        template = prompt_config.get("template", "")

        if not template:
            raise ValueError(f"No template found for prompt '{prompt_key}'")

        return template.format(**kwargs)

    def get_temperature(self, prompt_key: str) -> float:
        """Get the temperature setting for a given prompt.

        Args:
            prompt_key: Key identifying the prompt

        Returns:
            Temperature value (default 0.3 if not specified)
        """
        if prompt_key not in self._prompts:
            raise KeyError(f"Prompt '{prompt_key}' not found in configuration")

        return self._prompts[prompt_key].get("temperature", 0.3)

    def get_description(self, prompt_key: str) -> str:
        """Get the description for a given prompt.

        Args:
            prompt_key: Key identifying the prompt

        Returns:
            Description string
        """
        if prompt_key not in self._prompts:
            raise KeyError(f"Prompt '{prompt_key}' not found in configuration")

        return self._prompts[prompt_key].get("description", "")

    def get_model(self, prompt_key: str) -> str:
        """Get the recommended model for a given prompt.

        Args:
            prompt_key: Key identifying the prompt

        Returns:
            Model name (default 'sonnet' if not specified)
        """
        if prompt_key not in self._prompts:
            raise KeyError(f"Prompt '{prompt_key}' not found in configuration")

        return self._prompts[prompt_key].get("model", "sonnet")
