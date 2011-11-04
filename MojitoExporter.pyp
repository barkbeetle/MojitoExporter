import sys
import os
import c4d

pluginPath = os.path.dirname(__file__)
if pluginPath not in sys.path:
    sys.path.insert(0, pluginPath)

import mojito.export

pluginResource = c4d.plugins.GeResource()
pluginResource.Init(pluginPath)

pluginId = 1027817
pluginName = "Mojito (*.moj)"
fileEnding = "moj"

if not c4d.plugins.RegisterSceneSaverPlugin(pluginId, pluginName, mojito.export.MojitoExporter, c4d.PLUGINFLAG_SCENEFILTER_DIALOGCONTROL, "", fileEnding, pluginResource):
	print("MojitoExport could not be loaded!")

