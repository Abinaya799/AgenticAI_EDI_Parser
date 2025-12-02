from parser.loader import get_profile

def parse_invoice(segments : dict):
    """
    Parse EDI 210 segments into a structured invoice dictionary.
    """
    
    partner = segments['ISA'][0][6].strip()
    edi_version = segments['ISA'][0][12].strip()
    profile = get_profile(partner, edi_version)

    invoice = {
        "partner": partner,
        "edi_version": edi_version,
        "segments": segments,
    }

    return invoice