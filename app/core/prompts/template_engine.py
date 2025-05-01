"""
Prompt Template Engine
Location: /app/core/prompts/template_engine.py
Handles template-based prompt generation with support for variables, context, and extensible registration.
"""

import string
from typing import Dict, Optional

class TemplateNotFoundError(Exception):
    pass

class PromptTemplateEngine:
    """
    Handles registration and rendering of prompt templates, variable interpolation, and context merging.
    """

    def __init__(self):
        self._templates = {}

    def register_template(self, name: str, template_str: str):
        """
        Register a new prompt template for later use.
        """
        self._templates[name] = template_str

    def get_template(self, name: str) -> str:
        if name not in self._templates:
            raise TemplateNotFoundError(f"Template '{name}' not registered")
        return self._templates[name]

    def render_template(
        self, 
        name: str, 
        variables: Dict[str, str], 
        context: Optional[Dict] = None
    ) -> str:
        """
        Build a prompt from a template and variables, optionally merging context.

        The template string can use Python format syntax, such as {variable_name}.

        Args:
            name (str): Template name/key
            variables (dict): Variables to substitute in template
            context (dict): Additional contextual data (e.g., memory, summary)

        Returns:
            str: Generated prompt string
        """
        tmpl = self.get_template(name)
        combined = dict(variables or {})
        # Merge context keys if provided (context may contain info like 'history', 'user_profile', etc.)
        if context:
            for k, v in context.items():
                if k not in combined:
                    combined[k] = v
        try:
            return string.Template(tmpl).substitute(combined)
        except KeyError as ke:
            missing = ke.args[0]
            raise ValueError(f"Missing variable for prompt template: '{missing}'") from ke
