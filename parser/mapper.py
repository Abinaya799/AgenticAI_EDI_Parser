from loader import get_profile
from extract_elements_with_rules import extract_elements_with_rules

def parse_invoice(edi_text: str):
    """
    Tokenize and Parse EDI 210 segments into a structured invoice dictionary.
    """
    element_delim = '*'
    segment_delim = '~'
    golden_invoice = []
    warnings = []
    try:
        edi_text = edi_text.replace('\n', '')
        segments = {}
        multi_batch = edi_text.split('ST')
    except Exception as exc:
        raise RuntimeError(f"Failed to tokenize EDI: {exc}") from exc
    for batch in multi_batch[1:]:
        batch_edi = multi_batch[0] + 'ST' + batch
        segments_data = batch_edi.strip().split(segment_delim)
        for seg in segments_data:
            elements = seg.split(element_delim)
            key = elements[0].strip()
            segments.setdefault(key, []).append(elements)
        required_segments = ['ISA', 'GS', 'ST', 'B3', 'SE']
        for req_seg in required_segments:
            if req_seg not in segments:
                raise ValueError(f"Missing required segment: {req_seg}")
        try:
            partner = segments['GS'][0][2].strip()
            edi_version = segments['GS'][0][8].strip()
        except Exception:
            raise ValueError("Failed to extract partner and EDI version from segments")
        profile = get_profile(partner, edi_version)
        golden_invoice_segment, warnings = extract_elements_with_rules(profile, segments, partner, edi_version)
        golden_invoice.append(golden_invoice_segment)
        warnings.append(warnings)
    return golden_invoice, warnings