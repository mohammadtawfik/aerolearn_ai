"""
Prompt Response Parser
Location: /app/core/prompts/parser.py

Responsible for extracting structured information from LLM responses.
"""

import json
from typing import Optional, Dict

class ResponseParser:
    def parse(self, response_text: str, expected_format: Optional[str] = None) -> Dict:
        """
        Parse an LLM response into structured data.

        Args:
            response_text (str): Output from the language model
            expected_format (str, optional): "json", "qa", "table", etc.

        Returns:
            dict: Structured result (may be empty if unparseable)
        """
        # Try to parse as JSON first if requested
        if expected_format == "json":
            try:
                return json.loads(response_text)
            except Exception:
                # Sometimes the response is not valid JSON
                return {"error": "Failed to parse as JSON", "raw": response_text}

        if expected_format == "qa":
            # Improved QA parsing to handle chained colon-separated values
            lines = response_text.strip().split('\n')
            result = {}
            for line in lines:
                # Skip lines without colons
                if ':' not in line:
                    continue
                    
                # Split all segments on colon
                segments = [seg.strip() for seg in line.split(':')]
                
                # The first segment is the initial key, its value is the next segment
                if len(segments) >= 2:
                    key = segments[0]
                    value = segments[1]
                    result[key] = value
                    
                    # For any additional segments, recursively assign as key with empty value
                    for extra_key in segments[2:]:
                        if extra_key:
                            result[extra_key] = ""
            return result

        # Fallback: return the whole response as 'raw'
        return {"raw": response_text}
