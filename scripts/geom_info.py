#!/usr/bin/env python

import os, sys

try:
  from osgeo import ogr
except:
  print sys.stderr, "OGR module not found... Exiting"
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

    # count = layer.GetFeatureCount()
    # print "INFO: Merging %d features into a single feature" % ( count )

    # result = ogr.Geometry( ogr.wkbPolygon )

    print "Geometry report for layer ", os.path.basename( sys.argv[1] )

    fid = 0

    for feature in layer:
      geom = feature.GetGeometryRef()
      n = geom.GetGeometryCount()
      print "Feature: %d | Ring(s): %d | Hole(s): %d" % ( fid, n, n - 1 )
      fid += 1
