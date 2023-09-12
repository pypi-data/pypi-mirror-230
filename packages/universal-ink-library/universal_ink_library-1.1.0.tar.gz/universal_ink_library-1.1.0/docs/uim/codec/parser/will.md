Module uim.codec.parser.will
============================

Classes
-------

`Path(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `compositeOperation`
    :   Field WacomInkFormat.Path.compositeOperation

    `data`
    :   Field WacomInkFormat.Path.data

    `decimalPrecision`
    :   Field WacomInkFormat.Path.decimalPrecision

    `endParameter`
    :   Field WacomInkFormat.Path.endParameter

    `id`
    :   Field WacomInkFormat.Path.id

    `startParameter`
    :   Field WacomInkFormat.Path.startParameter

    `strokeColor`
    :   Field WacomInkFormat.Path.strokeColor

    `strokePaint`
    :   Field WacomInkFormat.Path.strokePaint

    `strokeParticlesRandomSeed`
    :   Field WacomInkFormat.Path.strokeParticlesRandomSeed

    `strokeWidth`
    :   Field WacomInkFormat.Path.strokeWidth

`WILL2Parser()`
:   Parser for Wacom Ink Layer Language - Data and File format.
    
    Examples
    --------
    >>> from uim.codec.parser.will import WILL2Parser
    >>> from uim.model.ink import InkModel
    >>> parser: WILL2Parser = WILL2Parser()
    >>> ink_model: InkModel = parser.parse('../ink/will/apple.will')
    
    See also
    --------
    ´UIMParser´ - Parser for UIM files

    ### Ancestors (in MRO)

    * uim.codec.parser.base.Parser
    * abc.ABC

    ### Class variables

    `APPLICATION: str`
    :   Application property tag.

    `APP_VERSION: str`
    :   App version property tag.

    `BRUSH: Dict[str, Any]`
    :   Default brush configuration.

    `DEFAULT_APPLICATION_NAME: str`
    :

    `DEFAULT_APPLICATION_VERSION: float`
    :

    `DEFAULT_DATETIME_FORMAT: str`
    :

    `DEFAULT_DECIMAL_PRECISION: int`
    :

    `DEFAULT_PATH_WIDTH: int`
    :

    `DEFAULT_TIME_STEP: float`
    :   Sampling rate of 120 Hz roughly 8 ms.

    `DEFAULT_WRITE_FORMAT: str`
    :

    `INK_DEVICE_BAMBOO_SLATE: str`
    :

    `INK_DEVICE_BAMBOO_SPARK: str`
    :

    `NODE_URI_PREFIX: str`
    :

    `SOURCE_OVER: int`
    :

    ### Static methods

    `unpack_will(filename_or_stream: Any, target_dir_name=None)`
    :   Unpack the WILL file codec (OPC).
        
        Parameters
        ----------
        filename_or_stream: Any
            File or stream
        target_dir_name: str
            Target directory for unpacking

    ### Methods

    `parse(self, path_or_stream: Any) ‑> uim.model.ink.InkModel`
    :   Parse the content of a WILL data or file format encoded ink file to the Universal Ink memory model.
        
        Parameters
        ----------
        path_or_stream: Any
            `Path` of file, path as str, stream, or byte array.
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream