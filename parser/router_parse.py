from fastapi import APIRouter, Body, HTTPException, status
from mapper import parse_invoice
from validator import validate_invoice
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/parse")
def parse_edi(edi_text: str = Body(..., media_type="text/plain")):
    """ Parse EDI text and return structured invoice data. """
    if not isinstance(edi_text, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request: edi_text must be a string"
        )
    try:       
        parsed,warnings = parse_invoice(edi_text)
        results = validate_invoice(parsed) 
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))     
         
    return JSONResponse(content={"results": results,"warnings": warnings })
