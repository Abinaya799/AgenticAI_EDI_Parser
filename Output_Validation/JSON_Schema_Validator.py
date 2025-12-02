import json
import sys
from typing import Dict, Any, List, Optional
from datetime import date
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Literal # Used for enums and constants

# --- 1. Pydantic Models for Golden Invoice JSON v0.1 ---
# (Models remain the same, providing the validation contract)

# Charges.other[]
class ChargesOtherItem(BaseModel):
    """Defines the structure for items in the 'charges.other' array."""
    code: str
    desc: Optional[str] = None
    amount: float # Uses float for number type
    
    class Config:
        # Ensures no extra fields are allowed in this nested object
        extra = 'forbid' 

# Source
class Source(BaseModel):
    """Defines the structure for the 'source' object."""
    type: Literal["edi210", "pdf", "image", "csv", "api"]
    # min_length=1 enforces minLength constraint from schema
    doc_uri: Optional[str] = Field(None, min_length=1) 

    class Config:
        extra = 'forbid'

# Carrier, Customer, Refs, Parties models are similar and rely on Optional[str]
class Carrier(BaseModel):
    name: Optional[str] = None
    scac: Optional[str] = None
    class Config:
        extra = 'forbid'

class Customer(BaseModel):
    name: Optional[str] = None
    account_id: Optional[str] = None
    class Config:
        extra = 'forbid'

class Refs(BaseModel):
    bol: Optional[str] = None
    pro: Optional[str] = None
    po: Optional[str] = None
    load_id: Optional[str] = None
    class Config:
        extra = 'forbid'

class Parties(BaseModel):
    ship_from: Optional[str] = None
    ship_to: Optional[str] = None
    bill_to: Optional[str] = None
    class Config:
        extra = 'forbid'

# Dates
class Dates(BaseModel):
    """Defines the structure for the 'dates' object."""
    # Using Python's built-in 'date' type automatically validates and coerces
    # ISO 8601 date strings (e.g., "YYYY-MM-DD") to date objects.
    invoice: date
    pickup: Optional[date] = None
    delivery: Optional[date] = None

    class Config:
        extra = 'forbid'

# Charges
class Charges(BaseModel):
    """Defines the structure for the 'charges' object."""
    base_freight: float
    fuel_surcharge: float = 0.0 # Applies schema 'default: 0'
    detention: float = 0.0      # Applies schema 'default: 0'
    other: List[ChargesOtherItem] = Field(default_factory=list) # Applies schema 'default: []'

    class Config:
        extra = 'forbid'

# Metadata
class Metadata(BaseModel):
    """Defines the structure for the 'metadata' object."""
    # Literal enforces the "const: 0.1" rule
    golden_schema_version: Literal["0.1"] = "0.1" 
    parser_version: str
    edi_version: Optional[str] = None
    trading_partner: Optional[str] = None
    # Field min/max apply the schema constraints (minimum: 0, maximum: 1)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0) 

    class Config:
        extra = 'forbid'

# Evidence
class Evidence(BaseModel):
    """Defines the structure for the 'evidence' object."""
    doc_uri: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)

    class Config:
        extra = 'forbid'

# Root Model: GoldenInvoice
class GoldenInvoice(BaseModel):
    """The root model for the Golden Invoice JSON v0.1 schema."""
    # min_length=1 enforces minLength constraint
    invoice_id: str = Field(min_length=1)
    # Literal enforces the enum constraint; default value is 'buy'
    side: Literal["buy", "sell"] = "buy" 
    source: Source
    carrier: Optional[Carrier] = None
    customer: Optional[Customer] = None
    refs: Optional[Refs] = None
    parties: Optional[Parties] = None
    dates: Dates
    # min_length=3, max_length=3 enforces constraints for ISO 4217 code
    currency: str = Field(min_length=3, max_length=3) 
    charges: Charges
    total: float
    metadata: Metadata
    evidence: Optional[Evidence] = None

    class Config:
        # Enforces 'additionalProperties: false' at the top level
        extra = 'forbid' 

# --- 2. Pydantic-based Validation Function ---

def validate_invoice(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a dictionary against the GoldenInvoice Pydantic model.

    Args:
        json_data: The invoice data (as a Python dictionary) to validate.

    Returns:
        A dictionary containing the validation status and any errors found,
        including the successfully parsed object if valid.
    """
    results: Dict[str, Any] = {
        "is_valid": True,
        "errors": [],
        "message": "Validation SUCCESSFUL"
    }

    try:
        # Attempt to parse and validate the data. 
        validated_invoice = GoldenInvoice.model_validate(json_data)
        
        # If successful, return the Pydantic model converted back to a dictionary 
        results["validated_data"] = validated_invoice.model_dump(mode='json')

    except ValidationError as e:
        results["is_valid"] = False
        results["message"] = f"Validation FAILED: Found {len(e.errors())} error(s)."
        
        # Pydantic's error reporting is very detailed
        results["errors"] = e.errors()

    return results

# --- 3. Interactive Console Runner ---

if __name__ == '__main__':
    print("="*70)
    print("GOLDEN INVOICE VALIDATOR (Pydantic)")
    print("="*70)
    print("Paste your JSON invoice data below and press Ctrl+D (or Ctrl+Z on Windows)")
    print("when finished, or press Enter twice to submit a one-line JSON string.")
    print("-" * 70)

    # Read multiline input from user
    input_lines = sys.stdin.readlines()
    json_input_string = "".join(input_lines).strip()

    if not json_input_string:
        print("\nERROR: No input provided. Exiting.")
        sys.exit(1)

    try:
        # Attempt to load the user's string input into a Python dictionary
        input_data = json.loads(json_input_string)
        
    except json.JSONDecodeError as e:
        print("\n" + "="*70)
        print("INPUT ERROR: The text provided is NOT valid JSON format.")
        print(f"Details: {e}")
        print("Please ensure all keys and string values are enclosed in double quotes.")
        print("="*70)
        sys.exit(1)
    
    # Run the validation
    print("\n" + "="*70)
    print("RUNNING VALIDATION AGAINST GOLDEN INVOICE SCHEMA V0.1...")
    print("="*70)
    validation_result = validate_invoice(input_data)

    if validation_result['is_valid']:
        print("✅ Validation SUCCESSFUL!")
        print("\n--- Validated and Coerced Data Output ---")
        # Display the coerced data (showing Pydantic's type conversions)
        print(json.dumps(validation_result["validated_data"], indent=2))
    else:
        print("❌ Validation FAILED!")
        print(f"\n{validation_result['message']}")
        print("\n--- Detailed Validation Errors ---")
        # Display the detailed error report
        print(json.dumps(validation_result["errors"], indent=2))
        
    print("\n" + "="*70)

# The original hardcoded test data has been removed, and the script now waits for user input.