Module uim.codec.format.UIM_3_0_0_pb2
=====================================
Generated protocol buffer code.

Classes
-------

`BrushPrototype(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `coordX`
    :   Field WacomInkFormat3.BrushPrototype.coordX

    `coordY`
    :   Field WacomInkFormat3.BrushPrototype.coordY

    `coordZ`
    :   Field WacomInkFormat3.BrushPrototype.coordZ

    `indices`
    :   Field WacomInkFormat3.BrushPrototype.indices

    `shapeURI`
    :   Field WacomInkFormat3.BrushPrototype.shapeURI

    `size`
    :   Field WacomInkFormat3.BrushPrototype.size

`Brushes(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `rasterBrushes`
    :   Field WacomInkFormat3.Brushes.rasterBrushes

    `vectorBrushes`
    :   Field WacomInkFormat3.Brushes.vectorBrushes

`ChannelData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `sensorChannelID`
    :   Field WacomInkFormat3.ChannelData.sensorChannelID

    `values`
    :   Field WacomInkFormat3.ChannelData.values

`Environment(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `id`
    :   Field WacomInkFormat3.Environment.id

    `properties`
    :   Field WacomInkFormat3.Environment.properties

`Float32(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `value`
    :   Field WacomInkFormat3.Float32.value

`InkData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `strokes`
    :   Field WacomInkFormat3.InkData.strokes

`InkInputProvider(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `id`
    :   Field WacomInkFormat3.InkInputProvider.id

    `properties`
    :   Field WacomInkFormat3.InkInputProvider.properties

    `type`
    :   Field WacomInkFormat3.InkInputProvider.type

`InkObject(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `brushes`
    :   Field WacomInkFormat3.InkObject.brushes

    `inkData`
    :   Field WacomInkFormat3.InkObject.inkData

    `inkTree`
    :   Field WacomInkFormat3.InkObject.inkTree

    `inputData`
    :   Field WacomInkFormat3.InkObject.inputData

    `knowledgeGraph`
    :   Field WacomInkFormat3.InkObject.knowledgeGraph

    `properties`
    :   Field WacomInkFormat3.InkObject.properties

    `transform`
    :   Field WacomInkFormat3.InkObject.transform

    `views`
    :   Field WacomInkFormat3.InkObject.views

`InputContext(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `environmentID`
    :   Field WacomInkFormat3.InputContext.environmentID

    `id`
    :   Field WacomInkFormat3.InputContext.id

    `sensorContextID`
    :   Field WacomInkFormat3.InputContext.sensorContextID

`InputContextData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `environments`
    :   Field WacomInkFormat3.InputContextData.environments

    `inkInputProviders`
    :   Field WacomInkFormat3.InputContextData.inkInputProviders

    `inputContexts`
    :   Field WacomInkFormat3.InputContextData.inputContexts

    `inputDevices`
    :   Field WacomInkFormat3.InputContextData.inputDevices

    `sensorContexts`
    :   Field WacomInkFormat3.InputContextData.sensorContexts

`InputData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `inputContextData`
    :   Field WacomInkFormat3.InputData.inputContextData

    `sensorData`
    :   Field WacomInkFormat3.InputData.sensorData

`InputDevice(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `id`
    :   Field WacomInkFormat3.InputDevice.id

    `properties`
    :   Field WacomInkFormat3.InputDevice.properties

`Matrix4(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `m00`
    :   Field WacomInkFormat3.Matrix4.m00

    `m01`
    :   Field WacomInkFormat3.Matrix4.m01

    `m02`
    :   Field WacomInkFormat3.Matrix4.m02

    `m03`
    :   Field WacomInkFormat3.Matrix4.m03

    `m10`
    :   Field WacomInkFormat3.Matrix4.m10

    `m11`
    :   Field WacomInkFormat3.Matrix4.m11

    `m12`
    :   Field WacomInkFormat3.Matrix4.m12

    `m13`
    :   Field WacomInkFormat3.Matrix4.m13

    `m20`
    :   Field WacomInkFormat3.Matrix4.m20

    `m21`
    :   Field WacomInkFormat3.Matrix4.m21

    `m22`
    :   Field WacomInkFormat3.Matrix4.m22

    `m23`
    :   Field WacomInkFormat3.Matrix4.m23

    `m30`
    :   Field WacomInkFormat3.Matrix4.m30

    `m31`
    :   Field WacomInkFormat3.Matrix4.m31

    `m32`
    :   Field WacomInkFormat3.Matrix4.m32

    `m33`
    :   Field WacomInkFormat3.Matrix4.m33

`Node(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `chunkFromIndex`
    :   Field WacomInkFormat3.Node.chunkFromIndex

    `chunkToIndex`
    :   Field WacomInkFormat3.Node.chunkToIndex

    `depth`
    :   Field WacomInkFormat3.Node.depth

    `groupBoundingBox`
    :   Field WacomInkFormat3.Node.groupBoundingBox

    `id`
    :   Field WacomInkFormat3.Node.id

    `index`
    :   Field WacomInkFormat3.Node.index

    `type`
    :   Field WacomInkFormat3.Node.type

`PathPointProperties(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `alpha`
    :   Field WacomInkFormat3.PathPointProperties.alpha

    `blue`
    :   Field WacomInkFormat3.PathPointProperties.blue

    `green`
    :   Field WacomInkFormat3.PathPointProperties.green

    `offsetX`
    :   Field WacomInkFormat3.PathPointProperties.offsetX

    `offsetY`
    :   Field WacomInkFormat3.PathPointProperties.offsetY

    `offsetZ`
    :   Field WacomInkFormat3.PathPointProperties.offsetZ

    `red`
    :   Field WacomInkFormat3.PathPointProperties.red

    `rotation`
    :   Field WacomInkFormat3.PathPointProperties.rotation

    `scaleX`
    :   Field WacomInkFormat3.PathPointProperties.scaleX

    `scaleY`
    :   Field WacomInkFormat3.PathPointProperties.scaleY

    `scaleZ`
    :   Field WacomInkFormat3.PathPointProperties.scaleZ

    `size`
    :   Field WacomInkFormat3.PathPointProperties.size

`Property(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `name`
    :   Field WacomInkFormat3.Property.name

    `value`
    :   Field WacomInkFormat3.Property.value

`Range(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `max`
    :   Field WacomInkFormat3.Range.max

    `min`
    :   Field WacomInkFormat3.Range.min

    `remapURI`
    :   Field WacomInkFormat3.Range.remapURI

`RasterBrush(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `blendMode`
    :   Field WacomInkFormat3.RasterBrush.blendMode

    `fillHeight`
    :   Field WacomInkFormat3.RasterBrush.fillHeight

    `fillTexture`
    :   Field WacomInkFormat3.RasterBrush.fillTexture

    `fillTextureURI`
    :   Field WacomInkFormat3.RasterBrush.fillTextureURI

    `fillWidth`
    :   Field WacomInkFormat3.RasterBrush.fillWidth

    `name`
    :   Field WacomInkFormat3.RasterBrush.name

    `randomizeFill`
    :   Field WacomInkFormat3.RasterBrush.randomizeFill

    `rotationMode`
    :   Field WacomInkFormat3.RasterBrush.rotationMode

    `scattering`
    :   Field WacomInkFormat3.RasterBrush.scattering

    `shapeTexture`
    :   Field WacomInkFormat3.RasterBrush.shapeTexture

    `shapeTextureURI`
    :   Field WacomInkFormat3.RasterBrush.shapeTextureURI

    `spacing`
    :   Field WacomInkFormat3.RasterBrush.spacing

`Rectangle(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `height`
    :   Field WacomInkFormat3.Rectangle.height

    `width`
    :   Field WacomInkFormat3.Rectangle.width

    `x`
    :   Field WacomInkFormat3.Rectangle.x

    `y`
    :   Field WacomInkFormat3.Rectangle.y

`SemanticTriple(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `object`
    :   Field WacomInkFormat3.SemanticTriple.object

    `predicate`
    :   Field WacomInkFormat3.SemanticTriple.predicate

    `subject`
    :   Field WacomInkFormat3.SemanticTriple.subject

`SensorChannel(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `id`
    :   Field WacomInkFormat3.SensorChannel.id

    `max`
    :   Field WacomInkFormat3.SensorChannel.max

    `metric`
    :   Field WacomInkFormat3.SensorChannel.metric

    `min`
    :   Field WacomInkFormat3.SensorChannel.min

    `precision`
    :   Field WacomInkFormat3.SensorChannel.precision

    `resolution`
    :   Field WacomInkFormat3.SensorChannel.resolution

    `type`
    :   Field WacomInkFormat3.SensorChannel.type

`SensorChannelsContext(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `channels`
    :   Field WacomInkFormat3.SensorChannelsContext.channels

    `id`
    :   Field WacomInkFormat3.SensorChannelsContext.id

    `inkInputProviderID`
    :   Field WacomInkFormat3.SensorChannelsContext.inkInputProviderID

    `inputDeviceID`
    :   Field WacomInkFormat3.SensorChannelsContext.inputDeviceID

    `latency`
    :   Field WacomInkFormat3.SensorChannelsContext.latency

    `samplingRateHint`
    :   Field WacomInkFormat3.SensorChannelsContext.samplingRateHint

`SensorContext(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `id`
    :   Field WacomInkFormat3.SensorContext.id

    `sensorChannelsContext`
    :   Field WacomInkFormat3.SensorContext.sensorChannelsContext

`SensorData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `dataChannels`
    :   Field WacomInkFormat3.SensorData.dataChannels

    `id`
    :   Field WacomInkFormat3.SensorData.id

    `inputContextID`
    :   Field WacomInkFormat3.SensorData.inputContextID

    `state`
    :   Field WacomInkFormat3.SensorData.state

    `timestamp`
    :   Field WacomInkFormat3.SensorData.timestamp

`Stroke(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `alpha`
    :   Field WacomInkFormat3.Stroke.alpha

    `blue`
    :   Field WacomInkFormat3.Stroke.blue

    `endParameter`
    :   Field WacomInkFormat3.Stroke.endParameter

    `green`
    :   Field WacomInkFormat3.Stroke.green

    `id`
    :   Field WacomInkFormat3.Stroke.id

    `offsetX`
    :   Field WacomInkFormat3.Stroke.offsetX

    `offsetY`
    :   Field WacomInkFormat3.Stroke.offsetY

    `offsetZ`
    :   Field WacomInkFormat3.Stroke.offsetZ

    `red`
    :   Field WacomInkFormat3.Stroke.red

    `rotation`
    :   Field WacomInkFormat3.Stroke.rotation

    `scaleX`
    :   Field WacomInkFormat3.Stroke.scaleX

    `scaleY`
    :   Field WacomInkFormat3.Stroke.scaleY

    `scaleZ`
    :   Field WacomInkFormat3.Stroke.scaleZ

    `sensorDataID`
    :   Field WacomInkFormat3.Stroke.sensorDataID

    `sensorDataMapping`
    :   Field WacomInkFormat3.Stroke.sensorDataMapping

    `sensorDataOffset`
    :   Field WacomInkFormat3.Stroke.sensorDataOffset

    `size`
    :   Field WacomInkFormat3.Stroke.size

    `splineX`
    :   Field WacomInkFormat3.Stroke.splineX

    `splineY`
    :   Field WacomInkFormat3.Stroke.splineY

    `splineZ`
    :   Field WacomInkFormat3.Stroke.splineZ

    `startParameter`
    :   Field WacomInkFormat3.Stroke.startParameter

    `style`
    :   Field WacomInkFormat3.Stroke.style

`Style(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `brushURI`
    :   Field WacomInkFormat3.Style.brushURI

    `particlesRandomSeed`
    :   Field WacomInkFormat3.Style.particlesRandomSeed

    `properties`
    :   Field WacomInkFormat3.Style.properties

    `renderModeURI`
    :   Field WacomInkFormat3.Style.renderModeURI

`TripleStore(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `statements`
    :   Field WacomInkFormat3.TripleStore.statements

`Uint32(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `value`
    :   Field WacomInkFormat3.Uint32.value

`VectorBrush(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `name`
    :   Field WacomInkFormat3.VectorBrush.name

    `prototype`
    :   Field WacomInkFormat3.VectorBrush.prototype

    `spacing`
    :   Field WacomInkFormat3.VectorBrush.spacing

`View(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `name`
    :   Field WacomInkFormat3.View.name

    `tree`
    :   Field WacomInkFormat3.View.tree