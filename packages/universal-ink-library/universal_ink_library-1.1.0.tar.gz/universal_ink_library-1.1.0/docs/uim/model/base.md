Module uim.model.base
=====================

Classes
-------

`HashIdentifier(identifier: uuid.UUID = None)`
:   MD5-hash based Unique Identifier Generation Algorithm
    -----------------------------------------------------
    The described algorithm allows generation of unique identifiers based on a tag (encoded as string value) and
    a collection of components.
    
    The supported component types are:
        - Integer number
        - Floating-point number
        - String
    
    List of properties defined as key-value pairs; the key and value of a pair are considered to be of type string.
    The described method takes a tag value and a list of components as arguments and generates a unique MD5 hash as
    an 8-byte array.
    
    Parameters
    ----------
    identifier: `UUID`
        Identifier

    ### Ancestors (in MRO)

    * uim.model.base.Identifier
    * abc.ABC

    ### Descendants

    * uim.model.inkdata.strokes.PathPointProperties
    * uim.model.inkinput.inputdata.Environment
    * uim.model.inkinput.inputdata.InkInputProvider
    * uim.model.inkinput.inputdata.InputContext
    * uim.model.inkinput.inputdata.InputDevice
    * uim.model.inkinput.inputdata.SensorChannel
    * uim.model.inkinput.inputdata.SensorChannelsContext
    * uim.model.inkinput.inputdata.SensorContext

    ### Class variables

    `SEPARATOR: str`
    :

`IdentifiableMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Different ID encoding methods

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `MD5`
    :

    `UUID`
    :

`Identifier(identifier: uuid.UUID, method: uim.model.base.IdentifiableMethod = IdentifiableMethod.MD5)`
:   Internal UIM 128bit Identifier (UimID)
    --------------------------------------
    UimID is a 128-bit number used internally by the implementations.
    
    It can be parsed from strings in the following formats:
    
    Simple Hexadecimal String Representation (S-Form)
    -------------------------------------------------
    The representation of a UimID value is the hex-decimal string representation of the 128-bit number,
    assuming that it's encoded using Big Endian byte ordering.
    
    For example: fa70390871c84d91b83c9b56549043ca
    
    Hyphenated Hexadecimal String Representation (H-Form)
    -----------------------------------------------------
    This representation of a UimID value has the following codec: <part1>-<part2>-<part3>-<part4>-<part5>
    
    Assuming that the UimID 128-bit value is encoded using Big Endian byte ordering, it is split into 5 groups of
    bytes and each group is formatted as hexadecimal number.
    
    ---------------------------------------------------------------------------
    |       |  Part 1    | Part 2 | Part 3 | Part 4 | Part 5                  |
    ---------------------------------------------------------------------------
    | Bytes | 0, 1, 2, 3 | 4, 5   | 6,7    | 8, 9   | 10, 11, 12, 13, 14, 15  |
    ---------------------------------------------------------------------------
    
    -----------------------------------------------------------------------------
    | S  | 32 digits: 00000000000000000000000000000000                          |
    |    | E.g., fa70390871c84d91b83c9b56549043ca                               |
    -----------------------------------------------------------------------------
    | H  | 32 digits separated by hyphens: 00000000-0000-0000-0000-000000000000 |
    |    | E.g.,  fa703908-71c8-4d91-b83c-9b56549043ca                          |
    -----------------------------------------------------------------------------
    
    The identifier's string representation varies based on the domain:
     - For MD5 hashes - "N" form
     - For Ink Model Internals (Strokes, Nodes, Group Nodes etc.) - "D" form

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.model.base.HashIdentifier
    * uim.model.base.UUIDIdentifier

    ### Class variables

    `SEPARATOR: str`
    :

    ### Static methods

    `from_bytes(from_bytes: bytes) ‑> uuid.UUID`
    :   Convert bytes array to UUID.
        
        Parameters
        ----------
        from_bytes: `bytes`
            Byte array encoding the UUID
        
        Returns
        -------
        uuid: `UUID`
            Valid UUID
        
        Raises
        ------
        InkModelException
            Bytes cannot be converted to UUID

    `str_to_uimid(uuid_str: str) ‑> uuid.UUID`
    :   Convert from string to UimID (UUID).
        
        Parameters
        ----------
        uuid_str: `str`
            UimID as s-form
        
        Returns
        -------
        uuid: `UUID`
            UUID from string
        
        Raises
        ------
        FormatException
            If UUID string is not valid.

    `uimid_to_h_form(uimid: uuid.UUID) ‑> str`
    :   Convert Uim-ID in h-form.
        
        Parameters
        ----------
        uimid: `UUID`
            UUID
        
        Returns
        -------
        h_form: str
            h-form of UimID
        
        Raises
        ------
        FormatException
            If UUID string is not valid.

    `uimid_to_s_form(uimid: uuid.UUID) ‑> str`
    :   Convert Uim-ID in s-form.
        
        Parameters
        ----------
        uimid: `UUID`
            UUID
        
        Returns
        -------
        s_form: `str`
            s-form of UimID

    ### Instance variables

    `id: uuid.UUID`
    :   Identifier of object. (`UUID`, read-only)

    `id_h_form: str`
    :   Hyphenated Hexadecimal String Representation (H-Form) (`str`, read-only)
        
        Examples
        --------
        32 digits separated by hyphens: 00000000-0000-0000-0000-000000000000, e.g., fa703908-71c8-4d91-b83c-9b56549043ca

    `id_s_form`
    :   Simple Hexadecimal String Representation (S-Form). (`str`, read-only)
        
        Examples
        --------
         32 digits: 00000000000000000000000000000000, e.g., fa70390871c84d91b83c9b56549043ca

`InkModelException(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`UUIDIdentifier(identifier: uuid.UUID)`
:   UUID Identifier.
    
    Parameters
    ----------
    identifier: `UUID`
        Identifier

    ### Ancestors (in MRO)

    * uim.model.base.Identifier
    * abc.ABC

    ### Descendants

    * uim.model.inkdata.strokes.Stroke
    * uim.model.inkinput.sensordata.ChannelData
    * uim.model.inkinput.sensordata.SensorData
    * uim.model.semantics.node.InkNode

    ### Class variables

    `SEPARATOR: str`
    :

    ### Static methods

    `id_generator() ‑> uuid.UUID`
    :   UUID generator function.
        
        Returns
        -------
        random: UUID
            Random generated UUID