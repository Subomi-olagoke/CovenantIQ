import anthropic
from app.config import settings
import json
import re
import logging

logger = logging.getLogger(__name__)

class ClaudeService:
    """
    Claude API integration for extracting covenant data from loan agreements.
    Uses detailed prompt engineering for comprehensive LMA document analysis.
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def extract_covenants_from_agreement(self, pdf_text: str, loan_title: str) -> dict:
        """
        Extract covenant data from loan agreement using Claude API.
        
        Args:
            pdf_text: Extracted text from PDF loan agreement
            loan_title: Title of the loan agreement
            
        Returns:
            Structured dictionary with:
            - borrower_name
            - loan_amount
            - currency
            - origination_date
            - maturity_date
            - covenants: List of covenant objects
        """
        
        prompt = f"""You are a financial document analysis expert specializing in LMA (Loan Market Association) loan agreements.

Analyze the following loan agreement text and extract ALL covenant information in a structured JSON format.

Loan Agreement Title: {loan_title}

Document Text:
{pdf_text[:15000]}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "borrower_name": "Company name",
  "loan_amount": 50000000.00,
  "currency": "EUR",
  "origination_date": "2024-01-15",
  "maturity_date": "2029-01-15",
  "covenants": [
    {{
      "covenant_type": "financial|information|negative|affirmative",
      "covenant_name": "Descriptive name",
      "description": "Full covenant description from agreement",
      "threshold_value": 4.0,
      "threshold_operator": "less_than|greater_than|less_or_equal|greater_or_equal|equal",
      "frequency": "quarterly|semi-annual|annual"
    }}
  ]
}}

IMPORTANT RULES:
1. Extract ALL covenants (financial ratios, information requirements, negative covenants, affirmative covenants)
2. For financial covenants, always extract threshold_value and threshold_operator
3. Use ISO date format (YYYY-MM-DD)
4. Return ONLY valid JSON, no markdown formatting
5. If a field is not found, use null
6. Common financial covenants to look for:
   - Debt/EBITDA Ratio (Leverage Ratio)
   - Interest Coverage Ratio
   - Debt Service Coverage Ratio
   - Current Ratio
   - Total Debt to Total Assets
   - Minimum EBITDA
   - Maximum Capital Expenditure
   
Return the JSON now:"""

        try:
            message = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4000,
                temperature=0,  # Deterministic output for financial data
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Remove markdown code fences if present
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                # Also try without json specifier
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            # Parse JSON
            result = json.loads(response_text.strip())
            
            logger.info(f"Successfully extracted {len(result.get('covenants', []))} covenants from loan agreement")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return {
                "borrower_name": None,
                "loan_amount": None,
                "currency": "EUR",
                "origination_date": None,
                "maturity_date": None,
                "covenants": []
            }
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {
                "borrower_name": None,
                "loan_amount": None,
                "currency": "EUR",
                "origination_date": None,
                "maturity_date": None,
                "covenants": []
            }

claude_service = ClaudeService()
