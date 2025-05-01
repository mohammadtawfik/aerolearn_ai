"""
AeroLearn AI Prompt Engineering Orchestrator

This module provides the main entry point for prompt generation, context-aware assembly,
optimization, and response parsing within AeroLearn AI.

Location: /app/core/ai/prompt_engineering.py
"""

from app.core.prompts.template_engine import PromptTemplateEngine
from app.core.prompts.optimizers import PromptOptimizer
from app.core.prompts.parser import ResponseParser

class PromptEngineering:
    """
    Main class handling prompt engineering workflow:
      - Template selection and variable substitution
      - Context merging
      - Prompt optimization (iterative improvement)
      - Response parsing
    """

    def __init__(self, optimizer=None, parser=None):
        self.template_engine = PromptTemplateEngine()
        self.optimizer = optimizer or PromptOptimizer()
        self.parser = parser or ResponseParser()

    def generate_prompt(
        self, 
        template_name: str, 
        variables: dict, 
        context: dict = None, 
        optimize: bool = True
    ) -> str:
        """
        Generate a full prompt string ready for large language model input.

        Args:
            template_name (str): Name/key of the prompt template to use
            variables (dict): Variables to fill into the template
            context (dict, optional): Dynamic memory or conversation context
            optimize (bool): Apply prompt optimization loop

        Returns:
            str: Final prompt string for model
        """
        prompt = self.template_engine.render_template(template_name, variables, context)
        if optimize:
            prompt = self.optimizer.optimize(prompt, context=context)
        return prompt

    def parse_response(self, prompt: str, llm_response: str, expected_format: str = None) -> dict:
        """
        Parse a model response, extracting structured information.

        Args:
            prompt (str): The original prompt sent to the model
            llm_response (str): The raw model output
            expected_format (str, optional): Optional hint (e.g., "json", "qa")

        Returns:
            dict: Parsed response content
        """
        return self.parser.parse(llm_response, expected_format=expected_format)

# Convenience singleton for project-wide use
prompt_engineering = PromptEngineering()