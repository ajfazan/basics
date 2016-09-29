import sys
sys.path.append( "D:/Juliano/Documents/devel/workspace/sandbox/tools/qgis/python/plugins" )

from functions import *

layer = qgis.utils.iface.activeLayer()

result = removeInnerRings( layer, 'result' )

QgsMapLayerRegistry.instance().addMapLayers( [result] )
