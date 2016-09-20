#!/usr/bin/env python

import os
import sys

try:
  from osgeo import ogr

except:
  print sys.stderr, "OGR not found... Exiting"
  sys.exit( 1 )

driver = ogr.GetDriverByName( "ESRI Shapefile" )

data_set = driver.Open( sys.argv[1], 0 )

if data_set is None:
  print sys.stderr, "Unable to open %s" % ( os.path.basename( sys.argv[1] ) )
  sys.exit( 1 )
else:
  layer = data_set.GetLayer()

  geom_type = layer.GetGeomType()

  if ( geom_type == ogr.wkbPolygon ) or ( geom_type == ogr.wkbMultiPolygon ):

    count = layer.GetFeatureCount()
    print "INFO: Merging %d features into a single feature" % ( count )

    result = ogr.Geometry( ogr.wkbPolygon )

    for feature in layer:
      result = result.Union( feature.GetGeometryRef() )

    if result.GetGeometryType() == ogr.wkbPolygon:
      print "Resulting region is a single polygon"

    if ( len( sys.argv ) == 4 ) and ( sys.argv[3] == "simple" ):
      simple = ogr.Geometry( ogr.wkbPolygon )
      simple.AddGeometry( result.GetGeometryRef( 0 ) )
      result = simple

    print "Resulting polygon has %d ring(s)" % ( result.GetGeometryCount() )

    outDriver = ogr.GetDriverByName( "ESRI Shapefile" )

    # Remove output shapefile if it already exists
    if os.path.exists( sys.argv[2] ):
      try:
        outDriver.DeleteDataSource( sys.argv[2] )
      except:
        print sys.stderr, "Unable to delete existing dataset"
        sys.exit( 1 )

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource( sys.argv[2] )
    outLayer = outDataSource.CreateLayer( "single", layer.GetSpatialRef(), \
                                          geom_type=ogr.wkbPolygon )

    # Add an ID field
    idField = ogr.FieldDefn( "ID", ogr.OFTInteger )
    outLayer.CreateField( idField )

    # Add a VERTICES fiedl
    verticesField = ogr.FieldDefn( "VERTICES", ogr.OFTInteger )
    outLayer.CreateField( verticesField )

    # Add an AREA field
    areaField = ogr.FieldDefn( "AREA", ogr.OFTReal )
    areaField.SetWidth( 25 )
    areaField.SetPrecision( 9 )
    outLayer.CreateField( areaField )

    # Add a PERIMETER field
    perimeterField = ogr.FieldDefn( "PERIMETER", ogr.OFTReal )
    perimeterField.SetWidth( 25 )
    perimeterField.SetPrecision( 9 )
    outLayer.CreateField( perimeterField )

    vertices = 0
    for k in range( 0, result.GetGeometryCount() ):
      vertices += result.GetGeometryRef( k ).GetPointCount() - 1

    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()
    feature = ogr.Feature( featureDefn )
    feature.SetGeometry( result )
    feature.SetField( "ID", 0 )
    feature.SetField( "VERTICES", vertices )
    feature.SetField( "AREA", result.GetArea() )
    feature.SetField( "PERIMETER", result.Boundary().Length() )
    outLayer.CreateFeature( feature )

    feature.Destroy()
    outDataSource.Destroy()
