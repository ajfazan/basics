from functions import *

layer = qgis.utils.iface.activeLayer()

iter = layer.getFeatures()

l = []
for feature in iter:
  l.append( feature )

i = 0

while i < len( l ):

  j = i + 1

  while j < len( l ):

    if isSameFeature( l[i], l[j] ):
      del( l[j] )
    else:
      j += 1

  i += 1

print len( l )

result = QgsVectorLayer( 'Polygon?crs=epsg:31982', 'result', "memory" )

pr = result.dataProvider()

for k in l:
  pr.addFeatures( [k] )

result.updateExtents()
QgsMapLayerRegistry.instance().addMapLayers( [result] )
