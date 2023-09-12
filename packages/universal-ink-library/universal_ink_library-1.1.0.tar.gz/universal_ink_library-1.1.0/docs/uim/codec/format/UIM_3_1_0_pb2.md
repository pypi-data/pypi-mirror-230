Module uim.codec.format.UIM_3_1_0_pb2
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
    :   Field UIM_3_1_0.BrushPrototype.coordX

    `coordY`
    :   Field UIM_3_1_0.BrushPrototype.coordY

    `coordZ`
    :   Field UIM_3_1_0.BrushPrototype.coordZ

    `indices`
    :   Field UIM_3_1_0.BrushPrototype.indices

    `shapeURI`
    :   Field UIM_3_1_0.BrushPrototype.shapeURI

    `size`
    :   Field UIM_3_1_0.BrushPrototype.size

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
    :   Field UIM_3_1_0.Brushes.rasterBrushes

    `vectorBrushes`
    :   Field UIM_3_1_0.Brushes.vectorBrushes

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
    :   Field UIM_3_1_0.ChannelData.sensorChannelID

    `values`
    :   Field UIM_3_1_0.ChannelData.values

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
    :   Field UIM_3_1_0.Environment.id

    `properties`
    :   Field UIM_3_1_0.Environment.properties

`InkData(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `brushURIs`
    :   Field UIM_3_1_0.InkData.brushURIs

    `properties`
    :   Field UIM_3_1_0.InkData.properties

    `renderModeURIs`
    :   Field UIM_3_1_0.InkData.renderModeURIs

    `strokes`
    :   Field UIM_3_1_0.InkData.strokes

    `transform`
    :   Field UIM_3_1_0.InkData.transform

    `unitScaleFactor`
    :   Field UIM_3_1_0.InkData.unitScaleFactor

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
    :   Field UIM_3_1_0.InkInputProvider.id

    `properties`
    :   Field UIM_3_1_0.InkInputProvider.properties

    `type`
    :   Field UIM_3_1_0.InkInputProvider.type

`InkOperation(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `Add`
    :   A ProtocolMessage

    `Compose`
    :   A ProtocolMessage

    `DESCRIPTOR`
    :

    `Remove`
    :   A ProtocolMessage

    `Select`
    :   A ProtocolMessage

    `Split`
    :   A ProtocolMessage

    `Transform`
    :   A ProtocolMessage

    `Update`
    :   A ProtocolMessage

    `UpdateSelection`
    :   A ProtocolMessage

    ### Instance variables

    `add`
    :   Field UIM_3_1_0.InkOperation.add

    `compose`
    :   Field UIM_3_1_0.InkOperation.compose

    `remove`
    :   Field UIM_3_1_0.InkOperation.remove

    `select`
    :   Field UIM_3_1_0.InkOperation.select

    `split`
    :   Field UIM_3_1_0.InkOperation.split

    `transform`
    :   Field UIM_3_1_0.InkOperation.transform

    `update`
    :   Field UIM_3_1_0.InkOperation.update

    `updateSelection`
    :   Field UIM_3_1_0.InkOperation.updateSelection

`InkPath(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `layout`
    :   Field UIM_3_1_0.InkPath.layout

    `path`
    :   Field UIM_3_1_0.InkPath.path

    `paths`
    :   Field UIM_3_1_0.InkPath.paths

    `pointProps`
    :   Field UIM_3_1_0.InkPath.pointProps

    `type`
    :   Field UIM_3_1_0.InkPath.type

`InkStructure(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `inkTree`
    :   Field UIM_3_1_0.InkStructure.inkTree

    `type`
    :   Field UIM_3_1_0.InkStructure.type

    `views`
    :   Field UIM_3_1_0.InkStructure.views

`InkTool(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `blendMode`
    :   Field UIM_3_1_0.InkTool.blendMode

    `context`
    :   Field UIM_3_1_0.InkTool.context

    `rasterBrush`
    :   Field UIM_3_1_0.InkTool.rasterBrush

    `vectorBrush`
    :   Field UIM_3_1_0.InkTool.vectorBrush

`InkTree(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `name`
    :   Field UIM_3_1_0.InkTree.name

    `tree`
    :   Field UIM_3_1_0.InkTree.tree

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
    :   Field UIM_3_1_0.InputContext.environmentID

    `id`
    :   Field UIM_3_1_0.InputContext.id

    `sensorContextID`
    :   Field UIM_3_1_0.InputContext.sensorContextID

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
    :   Field UIM_3_1_0.InputContextData.environments

    `inkInputProviders`
    :   Field UIM_3_1_0.InputContextData.inkInputProviders

    `inputContexts`
    :   Field UIM_3_1_0.InputContextData.inputContexts

    `inputDevices`
    :   Field UIM_3_1_0.InputContextData.inputDevices

    `sensorContexts`
    :   Field UIM_3_1_0.InputContextData.sensorContexts

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
    :   Field UIM_3_1_0.InputData.inputContextData

    `sensorData`
    :   Field UIM_3_1_0.InputData.sensorData

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
    :   Field UIM_3_1_0.InputDevice.id

    `properties`
    :   Field UIM_3_1_0.InputDevice.properties

`Intersection(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `intervals`
    :   Field UIM_3_1_0.Intersection.intervals

    `path`
    :   Field UIM_3_1_0.Intersection.path

`Interval(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `fromIndex`
    :   Field UIM_3_1_0.Interval.fromIndex

    `fromTValue`
    :   Field UIM_3_1_0.Interval.fromTValue

    `id`
    :   Field UIM_3_1_0.Interval.id

    `toIndex`
    :   Field UIM_3_1_0.Interval.toIndex

    `toTValue`
    :   Field UIM_3_1_0.Interval.toTValue

`Matrix(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `m00`
    :   Field UIM_3_1_0.Matrix.m00

    `m01`
    :   Field UIM_3_1_0.Matrix.m01

    `m02`
    :   Field UIM_3_1_0.Matrix.m02

    `m03`
    :   Field UIM_3_1_0.Matrix.m03

    `m10`
    :   Field UIM_3_1_0.Matrix.m10

    `m11`
    :   Field UIM_3_1_0.Matrix.m11

    `m12`
    :   Field UIM_3_1_0.Matrix.m12

    `m13`
    :   Field UIM_3_1_0.Matrix.m13

    `m20`
    :   Field UIM_3_1_0.Matrix.m20

    `m21`
    :   Field UIM_3_1_0.Matrix.m21

    `m22`
    :   Field UIM_3_1_0.Matrix.m22

    `m23`
    :   Field UIM_3_1_0.Matrix.m23

    `m30`
    :   Field UIM_3_1_0.Matrix.m30

    `m31`
    :   Field UIM_3_1_0.Matrix.m31

    `m32`
    :   Field UIM_3_1_0.Matrix.m32

    `m33`
    :   Field UIM_3_1_0.Matrix.m33

`Node(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `bounds`
    :   Field UIM_3_1_0.Node.bounds

    `depth`
    :   Field UIM_3_1_0.Node.depth

    `groupID`
    :   Field UIM_3_1_0.Node.groupID

    `index`
    :   Field UIM_3_1_0.Node.index

    `interval`
    :   Field UIM_3_1_0.Node.interval

`Path(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `data`
    :   Field UIM_3_1_0.Path.data

`PathPointContext(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `colorMask`
    :   Field UIM_3_1_0.PathPointContext.colorMask

    `dynamics`
    :   Field UIM_3_1_0.PathPointContext.dynamics

    `statics`
    :   Field UIM_3_1_0.PathPointContext.statics

`PathPointProperties(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `color`
    :   Field UIM_3_1_0.PathPointProperties.color

    `offsetX`
    :   Field UIM_3_1_0.PathPointProperties.offsetX

    `offsetY`
    :   Field UIM_3_1_0.PathPointProperties.offsetY

    `offsetZ`
    :   Field UIM_3_1_0.PathPointProperties.offsetZ

    `rotation`
    :   Field UIM_3_1_0.PathPointProperties.rotation

    `scaleX`
    :   Field UIM_3_1_0.PathPointProperties.scaleX

    `scaleY`
    :   Field UIM_3_1_0.PathPointProperties.scaleY

    `scaleZ`
    :   Field UIM_3_1_0.PathPointProperties.scaleZ

    `size`
    :   Field UIM_3_1_0.PathPointProperties.size

`PathPointSettings(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `alpha`
    :   Field UIM_3_1_0.PathPointSettings.alpha

    `blue`
    :   Field UIM_3_1_0.PathPointSettings.blue

    `green`
    :   Field UIM_3_1_0.PathPointSettings.green

    `offsetX`
    :   Field UIM_3_1_0.PathPointSettings.offsetX

    `offsetY`
    :   Field UIM_3_1_0.PathPointSettings.offsetY

    `offsetZ`
    :   Field UIM_3_1_0.PathPointSettings.offsetZ

    `red`
    :   Field UIM_3_1_0.PathPointSettings.red

    `rotation`
    :   Field UIM_3_1_0.PathPointSettings.rotation

    `scaleX`
    :   Field UIM_3_1_0.PathPointSettings.scaleX

    `scaleY`
    :   Field UIM_3_1_0.PathPointSettings.scaleY

    `scaleZ`
    :   Field UIM_3_1_0.PathPointSettings.scaleZ

    `size`
    :   Field UIM_3_1_0.PathPointSettings.size

`Paths(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `data`
    :   Field UIM_3_1_0.Paths.data

`Properties(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `properties`
    :   Field UIM_3_1_0.Properties.properties

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
    :   Field UIM_3_1_0.Property.name

    `value`
    :   Field UIM_3_1_0.Property.value

`PropertySettings(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `altitude`
    :   Field UIM_3_1_0.PropertySettings.altitude

    `dependencies`
    :   Field UIM_3_1_0.PropertySettings.dependencies

    `pressure`
    :   Field UIM_3_1_0.PropertySettings.pressure

    `radiusX`
    :   Field UIM_3_1_0.PropertySettings.radiusX

    `radiusY`
    :   Field UIM_3_1_0.PropertySettings.radiusY

    `resolveURI`
    :   Field UIM_3_1_0.PropertySettings.resolveURI

    `value`
    :   Field UIM_3_1_0.PropertySettings.value

    `velocity`
    :   Field UIM_3_1_0.PropertySettings.velocity

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
    :   Field UIM_3_1_0.Range.max

    `min`
    :   Field UIM_3_1_0.Range.min

    `remapURI`
    :   Field UIM_3_1_0.Range.remapURI

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
    :   Field UIM_3_1_0.RasterBrush.blendMode

    `fillHeight`
    :   Field UIM_3_1_0.RasterBrush.fillHeight

    `fillTexture`
    :   Field UIM_3_1_0.RasterBrush.fillTexture

    `fillTextureURI`
    :   Field UIM_3_1_0.RasterBrush.fillTextureURI

    `fillWidth`
    :   Field UIM_3_1_0.RasterBrush.fillWidth

    `name`
    :   Field UIM_3_1_0.RasterBrush.name

    `randomizeFill`
    :   Field UIM_3_1_0.RasterBrush.randomizeFill

    `rotationMode`
    :   Field UIM_3_1_0.RasterBrush.rotationMode

    `scattering`
    :   Field UIM_3_1_0.RasterBrush.scattering

    `shapeTexture`
    :   Field UIM_3_1_0.RasterBrush.shapeTexture

    `shapeTextureURI`
    :   Field UIM_3_1_0.RasterBrush.shapeTextureURI

    `spacing`
    :   Field UIM_3_1_0.RasterBrush.spacing

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
    :   Field UIM_3_1_0.Rectangle.height

    `width`
    :   Field UIM_3_1_0.Rectangle.width

    `x`
    :   Field UIM_3_1_0.Rectangle.x

    `y`
    :   Field UIM_3_1_0.Rectangle.y

`Segment(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `complete`
    :   Field UIM_3_1_0.Segment.complete

    `ink`
    :   Field UIM_3_1_0.Segment.ink

    `pointerID`
    :   Field UIM_3_1_0.Segment.pointerID

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
    :   Field UIM_3_1_0.SensorChannel.id

    `max`
    :   Field UIM_3_1_0.SensorChannel.max

    `metric`
    :   Field UIM_3_1_0.SensorChannel.metric

    `min`
    :   Field UIM_3_1_0.SensorChannel.min

    `precision`
    :   Field UIM_3_1_0.SensorChannel.precision

    `resolution`
    :   Field UIM_3_1_0.SensorChannel.resolution

    `type`
    :   Field UIM_3_1_0.SensorChannel.type

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
    :   Field UIM_3_1_0.SensorChannelsContext.channels

    `id`
    :   Field UIM_3_1_0.SensorChannelsContext.id

    `inkInputProviderID`
    :   Field UIM_3_1_0.SensorChannelsContext.inkInputProviderID

    `inputDeviceID`
    :   Field UIM_3_1_0.SensorChannelsContext.inputDeviceID

    `latency`
    :   Field UIM_3_1_0.SensorChannelsContext.latency

    `samplingRateHint`
    :   Field UIM_3_1_0.SensorChannelsContext.samplingRateHint

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
    :   Field UIM_3_1_0.SensorContext.id

    `sensorChannelsContext`
    :   Field UIM_3_1_0.SensorContext.sensorChannelsContext

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
    :   Field UIM_3_1_0.SensorData.dataChannels

    `id`
    :   Field UIM_3_1_0.SensorData.id

    `inputContextID`
    :   Field UIM_3_1_0.SensorData.inputContextID

    `state`
    :   Field UIM_3_1_0.SensorData.state

    `timestamp`
    :   Field UIM_3_1_0.SensorData.timestamp

`Stroke(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    `SplineCompressed`
    :   A ProtocolMessage

    `SplineData`
    :   A ProtocolMessage

    ### Instance variables

    `brushURIIndex`
    :   Field UIM_3_1_0.Stroke.brushURIIndex

    `brushURIValue`
    :   Field UIM_3_1_0.Stroke.brushURIValue

    `endParameter`
    :   Field UIM_3_1_0.Stroke.endParameter

    `id`
    :   Field UIM_3_1_0.Stroke.id

    `precisions`
    :   Field UIM_3_1_0.Stroke.precisions

    `propertiesIndex`
    :   Field UIM_3_1_0.Stroke.propertiesIndex

    `propertiesValue`
    :   Field UIM_3_1_0.Stroke.propertiesValue

    `randomSeed`
    :   Field UIM_3_1_0.Stroke.randomSeed

    `renderModeURIIndex`
    :   Field UIM_3_1_0.Stroke.renderModeURIIndex

    `renderModeURIValue`
    :   Field UIM_3_1_0.Stroke.renderModeURIValue

    `sensorDataID`
    :   Field UIM_3_1_0.Stroke.sensorDataID

    `sensorDataMapping`
    :   Field UIM_3_1_0.Stroke.sensorDataMapping

    `sensorDataOffset`
    :   Field UIM_3_1_0.Stroke.sensorDataOffset

    `splineCompressed`
    :   Field UIM_3_1_0.Stroke.splineCompressed

    `splineData`
    :   Field UIM_3_1_0.Stroke.splineData

    `startParameter`
    :   Field UIM_3_1_0.Stroke.startParameter

`StrokesContext(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    ### Instance variables

    `path`
    :   Field UIM_3_1_0.StrokesContext.path

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
    :   Field UIM_3_1_0.Style.brushURI

    `color`
    :   Field UIM_3_1_0.Style.color

    `pointerID`
    :   Field UIM_3_1_0.Style.pointerID

    `randomSeed`
    :   Field UIM_3_1_0.Style.randomSeed

    `renderModeURI`
    :   Field UIM_3_1_0.Style.renderModeURI

`TripleStore(*args, **kwargs)`
:   A ProtocolMessage

    ### Ancestors (in MRO)

    * google.protobuf.pyext._message.CMessage
    * google.protobuf.message.Message

    ### Class variables

    `DESCRIPTOR`
    :

    `SemanticTriple`
    :   A ProtocolMessage

    ### Instance variables

    `statements`
    :   Field UIM_3_1_0.TripleStore.statements

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
    :   Field UIM_3_1_0.VectorBrush.name

    `prototype`
    :   Field UIM_3_1_0.VectorBrush.prototype

    `spacing`
    :   Field UIM_3_1_0.VectorBrush.spacing