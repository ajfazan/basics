#!/usr/bin/env python

import os
import sys

try:
  from osgeo import ogr

except:
  print sys.stderr, "OGR not found... Exiting"
  sys.exit( 1 )

driver = ogr.GetDriverByName( "ESRI Shapefile" )

data = driver.Open( sys.argv[1], 0 )

if data is None:
  print sys.stderr, "Unable to open %s" % ( os.path.basename( sys.argv[1] ) )
  sys.exit( 1 )
else:
  layer = data.GetLayer()

  geom_type = layer.GetGeomType()

  if geom_type == ogr.wkbPolygon or geom_type == ogr.wkbMultiPolygon:


    count = layer.GetFeatureCount()
    print "INFO: Merging %d features into a single feature" % ( count )

    result = ogr.Geometry( ogr.wkbPolygon )

    for feature in layer:
      result = result.Union( feature.GetGeometryRef() )

    outDriver = ogr.GetDriverByName( "ESRI Shapefile" )

    # Remove output shapefile if it already exists
    if os.path.exists( sys.argv[2] ):
        outDriver.DeleteDataSource( sys.argv[2] )

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource( sys.argv[2] )
    outLayer = outDataSource.CreateLayer( "single", layer.GetSpatialRef(), \
                                          geom_type=ogr.wkbPolygon )

    # Add an ID field
    idField = ogr.FieldDefn( "id", ogr.OFTInteger )
    outLayer.CreateField( idField )

    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()
    feature = ogr.Feature( featureDefn )
    feature.SetGeometry( result )
    feature.SetField( "id", 0 )
    outLayer.CreateFeature( feature )

    feature.Destroy()
    outDataSource.Destroy()
