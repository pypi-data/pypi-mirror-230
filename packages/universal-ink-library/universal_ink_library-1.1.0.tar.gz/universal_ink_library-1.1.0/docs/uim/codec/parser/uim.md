Module uim.codec.parser.uim
===========================

Classes
-------

`UIMParser()`
:   Parser for Universal Ink Model data codec.
    
    Examples
    --------
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.ink import InkModel
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse('../ink/uim_3.1.0/5) Cell Structure 1 (3.1 delta).uim')
    
    See also
    --------
    ´WILL2Parser´ - Parser for WILL files

    ### Ancestors (in MRO)

    * uim.codec.parser.base.Parser
    * abc.ABC

    ### Static methods

    `parse_json(path: Any) ‑> uim.model.ink.InkModel`
    :   Parse ink file from either a `Path`, `str`.
        
        Parameters
        ----------
        path: Any
            Location of the JSON file
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream

    ### Methods

    `parse(self, path_or_stream: Any) ‑> uim.model.ink.InkModel`
    :   Parse the Universal Ink Model codec.
        
        Parameters
        ----------
        path_or_stream: Any
            `Path` of file, path as str, stream, or byte array.
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream