Module uim.model.inkinput.sensordata
====================================

Classes
-------

`ChannelData(sensor_channel_id: uuid.UUID, values: list = None)`
:   List of data items.
    
    Constructs channel data object.
    :param sensor_channel_id: Referencing InkSensorChannel via id.
    :param values: Sample values delta encoded with provided precision.

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `values: list`
    :   Sample values delta encoded with provided precision.
        
        :return: values

`InkState(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   The uim input data state defines the state of the Ink input data.
    WILL 3.0 supports different modes:
     - Writing on a plane,
      - Hovering above a surface,
      - Moving in air (VR/AR/MR) interaction,
      - Only hovering in the air.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `HOVERING`
    :

    `IN_VOLUME`
    :

    `PLANE`
    :

    `START_TRACKING`
    :

    `STOP_TRACKING`
    :

    `VOLUME_HOVERING`
    :

`SensorData(sid: uuid.UUID = None, input_context_id: uuid.UUID = None, state: uim.model.inkinput.sensordata.InkState = None, timestamp: int = None)`
:   SensorData
    ----------
    The SensorData Repository is a data repository, which holds a collection of SensorData instances.
    
    A data-frame structure represents a collection of raw input data sequences, produced by one or more on-board
    device sensors, including data points, re-sampling information, and input sources from fingerprints and metadata.
    
    Remark:
    --------
    Once a SensorData instance is added to the SensorData repository, it is considered immutable.
    
    Constructs a sensor data item.
    :param sid: bytes -
        Sensor data identifier.
    :param input_context_id: bytes -
        Referencing the InputContext via id.
    :param state: InkState -
        The state of the input provider during the capturing of this data frame.
    :param timestamp: int -
        Timestamp for first sample of the stroke, measured in milliseconds.

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `data_channels: List[uim.model.inkinput.sensordata.ChannelData]`
    :   List of the different channels.
        
        :return: list of DataChannel instances

    `input_context_id: uuid.UUID`
    :   Id of the input context.
        
        :return: reference id for the input context

    `state: uim.model.inkinput.sensordata.InkState`
    :   State of the uim sensor sequence.
        
        :return: InkState enum instance

    `timestamp: int`
    :   Timestamp of the first data sample in this sequence.
        
        :return: long timestamp

    ### Methods

    `add_data(self, sensor_channel: uim.model.inkinput.inputdata.SensorChannel, values: List[float])`
    :   Adding data.
        :param sensor_channel: SensorChannel -
            The sensor channel which sourced the data.
        :param values:
            A list of values.
        :raises:
            ValueError: Issue with the parameter

    `add_timestamp_data(self, sensor_channel: uim.model.inkinput.inputdata.SensorChannel, values: List[float])`
    :   Adding timestamp data.
        :param sensor_channel: SensorChannel -
            The sensor channel which sourced the data.
        :param values:
            A list of timestamp values with the configured unit type.
        :raises:
            ValueError: Issue with the parameter

    `get_data_by_id(self, channel_id: uuid.UUID) ‑> uim.model.inkinput.sensordata.ChannelData`
    :   Returns data channel.
        :param channel_id: bytes -
            id of the DataChannel
        :return : data channel