from typing import Dict, Any, List, Optional
from datetime import date
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Literal

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

def validate_invoice(json_list: list[dict]) -> List:
    """
    Validates a dictionary against the GoldenInvoice Pydantic model.
    """
    results: List = []
    print(f"validator json_list: {json_list}")
    for json_data in json_list:
        print(type(json_data))
        try:
            validated_invoice = GoldenInvoice.model_validate(json_data)
            results.append({"is_valid": True, "errors": [], "message": "Validation Successful",
                             "validated_data":validated_invoice.model_dump(mode='json')})
            print("i am in validator")
        except ValidationError as e:
            results.append({"is_valid": False, "errors": e.errors(),
                             "message": f"Validation FAILED: Found {len(e.errors())} error(s).",
                             "validated_data":{}})

    return results