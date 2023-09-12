Module uim.model.helpers.text_extractor
=======================================

Functions
---------

    
`uim_extract_text_and_semantics(uim_bytes: bytes, hwr_view: str = 'hwr', ner_view: Optional[str] = None) ‑> Tuple[List[dict], List[dict]]`
:   Extracting the text from Universal Ink Model.
    
    Parameters
    ----------
    uim_bytes: `bytes`
        Byte array with RIFF file from Universal Ink Model
    hwr_view: `str`
       HWR view.
    ner_view: `str`
        NER view if needed.
    
    Returns
    -------
    text: `List[dict]`
        List of text lines. Each line has its own dict containing the  bounding box, and all words
    entities.
    
    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.

    
`uim_extract_text_and_semantics_from(ink_model: uim.model.ink.InkModel, hwr_view: str = 'hwr') ‑> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], str]`
:   Extracting the text from Universal Ink Model.
    
    Parameters
    ----------
    ink_model: InkModel -
        Universal Ink Model
    hwr_view: str -
       Name of the HWR view.
    
    Returns
    -------
    words: `List[dict]`
        List of words. Each word has its own dict containing the text, bounding box, and all alternatives.
    entities: `Dict[str, List[dict]]`
        Dictionary of entities. Each entity has its own dict containing the label, instance, and path ids.
    text: `str`
        Text extracted from the Universal Ink Model.
    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.
    
     Examples
    --------