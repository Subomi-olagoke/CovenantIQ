import openai
from app.config import settings
import json
import logging
import re

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    OpenAI API integration for extracting covenant data from loan agreements.
    Uses GPT-4o for comprehensive LMA document analysis.
    """
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def extract_covenants_from_agreement(self, pdf_text: str, loan_title: str) -> dict:
        """
        Extract covenant data from loan agreement using OpenAI API.
        
        Args:
            pdf_text: Extracted text from PDF loan agreement
            loan_title: Title of the loan agreement
            
        Returns:
            Structured dictionary with extracted data
        """
        
        system_prompt = """You are a financial document analysis expert specializing in LMA (Loan Market Association) loan agreements.
Analyze loan agreements to extract ALL covenant information in structured JSON format."""

        user_prompt = f"""Analyze the following loan agreement text and extract ALL covenant information.

Loan Agreement Title: {loan_title}

Document Text:
{pdf_text[:15000]}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "borrower_name": "Company name",
  "loan_amount": 50000000.00,
  "currency": "EUR",
  "origination_date": "YYYY-MM-DD",
  "maturity_date": "YYYY-MM-DD",
  "covenants": [
    {{
      "covenant_type": "financial|information|negative|affirmative",
      "covenant_name": "Descriptive name",
      "description": "Full description",
      "threshold_value": 4.0,
      "threshold_operator": "less_than|greater_than|less_or_equal|greater_or_equal|equal",
      "frequency": "quarterly|semi-annual|annual"
    }}
  ]
}}

RULES:
1. Extract ALL covenants (financial, information, negative, affirmative)
2. For financial covenants, explicitly extract numeric threshold_value and threshold_operator
3. Use ISO date format (YYYY-MM-DD)
4. If a field is not found, use null
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON
            result = json.loads(response_text)
            
            logger.info(f"Successfully extracted {len(result.get('covenants', []))} covenants via OpenAI")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._empty_result()

    def _empty_result(self):
        return {
            "borrower_name": None,
            "loan_amount": None,
            "currency": "EUR",
            "origination_date": None,
            "maturity_date": None,
            "covenants": []
        }

openai_service = OpenAIService()
