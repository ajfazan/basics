#!/usr/bin/env python

import os, sys

try:
  from osgeo import ogr, osr
except:
  print sys.stderr, "OGR module not found... Exiting"
  sys.exit( 1 )

driver = ogr.GetDriverByName( "ESRI Shapefile" )

data_set = driver.Open( sys.argv[1], 0 )

if data_set is None:

  print sys.stderr, "Unable to open %s" % ( os.path.basename( sys.argv[1] ) )
  sys.exit( 1 )

else:

  outDriver = ogr.GetDriverByName( "ESRI Shapefile" )

  # Remove the output shapefile if it already exists
  if os.path.exists( sys.argv[2] ):

    try:
      outDriver.DeleteDataSource( sys.argv[2] )
    except:
      print sys.stderr, "Unable to delete existing dataset" + sys.argv[2]
      sys.exit( 1 )

  layer = data_set.GetLayer()

  geom_type = layer.GetGeomType()

  if ( geom_type == ogr.wkbPolygon ):

    # Create the output dataset
    outDataSource = outDriver.CreateDataSource( sys.argv[2] )

    crs = osr.SpatialReference()
    crs.ImportFromWkt( layer.GetSpatialRef().ExportToWkt() )

    outLayer = outDataSource.CreateLayer( "layer", crs, ogr.wkbPolygon )

    # Add an FID field
    fidField = ogr.FieldDefn( "FID", ogr.OFTInteger64 )
    fidField.SetWidth( 16 )
    outLayer.CreateField( fidField )

    fid = 1

    for feature in layer:

      geom = feature.GetGeometryRef()

      poly = ogr.Geometry( ogr.wkbPolygon )
      poly.AddGeometry( geom.GetGeometryRef( 0 ) )

      # Create the feature and set values
      featureDefn = outLayer.GetLayerDefn()
      outFeature = ogr.Feature( featureDefn )
      outFeature.SetGeometry( poly )
      outFeature.SetField( "FID", fid )
      outLayer.CreateFeature( outFeature )

      fid += 1

      outFeature.Destroy()

    outDataSource.Destroy()
