import anthropic
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def extract_covenants_from_text(self, text: str) -> list:
        """
        Extract covenants from loan agreement text using Claude API.
        
        Args:
            text: Extracted text from PDF loan agreement
            
        Returns:
            List of covenant dictionaries
        """
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""Extract all loan covenants from this loan agreement text.
                    
Return ONLY valid JSON array with no markdown formatting or code fences:
[
  {{
    "covenant_type": "financial|non-financial|reporting",
    "covenant_name": "string",
    "description": "string",
    "threshold_value": number or null,
    "threshold_operator": ">|<|>=|<=|=" or null,
    "measurement_frequency": "quarterly|annually|monthly|semi-annually"
  }}
]

Guidelines:
- covenant_type: "financial" for ratios/metrics, "non-financial" for actions/restrictions, "reporting" for disclosure requirements
- covenant_name: Short descriptive name (e.g., "Debt to EBITDA Ratio")
- description: Full text from agreement describing the covenant
- threshold_value: Numeric threshold if applicable (e.g., 4.0 for "must not exceed 4.0x")
- threshold_operator: Direction of threshold (>, <, >=, <=, =)
- measurement_frequency: How often measured

Loan Agreement Text:
{text[:15000]}
"""
                }]
            )
            
            response_text = message.content[0].text
            
            # Remove markdown code fences if present
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            covenants = json.loads(clean_json)
            
            logger.info(f"Successfully extracted {len(covenants)} covenants from text")
            return covenants
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error extracting covenants with Claude: {e}")
            return []

claude_service = ClaudeService()
