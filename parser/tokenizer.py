def tokenize_edi(edi_text: str):
    """ Tokenize EDI text into segments and elements. """
    
    element_delim = '*'
    segment_delim = '~'
    
    edi_text = edi_text.replace('\n', '')
    segments = {}
    segments_data = edi_text.strip().split(segment_delim)
    for seg in segments_data:
        elements = seg.split(element_delim)
        key = elements[0].strip()
        segments.setdefault(key, []).append(elements)
    return segments
