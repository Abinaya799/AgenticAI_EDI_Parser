from fastapi import APIRouter, Body
from parser.tokenizer import tokenize_edi
from parser.mapper import parse_invoice
from ..schema.validator import validate_against_schema

router = APIRouter()

@router.post("/parse")
def parse_edi(edi_data: str = Body(..., media_type="text/plain")):
    segments = tokenize_edi(edi_data)          
    parsed = parse_invoice(segments)           
    validate_against_schema(parsed)            
    return parsed
