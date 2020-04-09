#!/usr/bin/env osgeo_python

import glob, os, sys

def open_layer( driver, filename, crs ):

  data_set = driver.Open( filename, 0 )

  layer = data_set.GetLayer()

  # assert( layer.GetSpatialRef() == crs )

  n = layer.GetFeatureCount()

  if n > 1:
    print "Warning: Layer '%s' has %d features" % ( filename, n )

  assert( n == 1 )

  return layer

try:
  from osgeo import ogr, osr
except:
  print sys.stderr, "OGR and/or OSR modules not found... Exiting"
  sys.exit( 1 )

source = osr.SpatialReference()
source.ImportFromEPSG( int( sys.argv[3] ) )

outDriver = ogr.GetDriverByName( "ESRI Shapefile" )

# Remove the output shapefile if it already exists
if os.path.exists( sys.argv[2] ):
  try:
    outDriver.DeleteDataSource( sys.argv[2] )
  except:
    print sys.stderr, "Unable to delete existing dataset" + sys.argv[2]
    sys.exit( 1 )

# Create the output shapefile
outDataSource = outDriver.CreateDataSource( sys.argv[2] )
outLayer = outDataSource.CreateLayer( "layer", source, ogr.wkbPolygon )

# Add an ID field
idField = ogr.FieldDefn( "Name", ogr.OFTString )
outLayer.CreateField( idField )

shapes = []

if os.path.isdir( sys.argv[1] ):
  os.chdir( sys.argv[1] )
  shapes = glob.glob( "*.shp" )
elif os.path.isfile( sys.argv[1] ):
  f = open( sys.argv[1], 'r' )
  shapes = f.read().splitlines()

driver = ogr.GetDriverByName( "ESRI Shapefile" )

n = len( shapes )

for i in range( n - 1 ):

  j = i + 1

  tag1 = os.path.splitext( os.path.basename( shapes[i] ) )[0]
  tag2 = os.path.splitext( os.path.basename( shapes[j] ) )[0]

  data_set1 = driver.Open( shapes[i], 0 )
  data_set2 = driver.Open( shapes[j], 0 )

  layer1 = open_layer( driver, shapes[i], source )
  layer2 = open_layer( driver, shapes[j], source )

  geom1_type = layer1.GetGeomType()
  geom2_type = layer2.GetGeomType()

  if ( geom1_type == ogr.wkbPolygon ) and ( geom2_type == ogr.wkbPolygon ):

    k = 0
    tmp1 = ogr.Geometry( ogr.wkbPolygon )
    for f in layer1:
      tmp1 = tmp1.Union( f.GetGeometryRef() )
      k += 1
    assert( k == 1 )
    # print layer1
    # print layer1[0]
    # print tmp1.GetGeometryName()

    k = 0
    tmp2 = ogr.Geometry( ogr.wkbPolygon )
    for f in layer2:
      tmp2 = tmp2.Union( f.GetGeometryRef() )
      k += 1
    assert( k == 1 )
    # print layer2
    # print layer2[0]
    # print tmp2.GetGeometryName()

    result = tmp1.Intersection( tmp2 )

    if ( result.GetGeometryType() == ogr.wkbPolygon ):

      # Create the feature and set values
      featureDefn = outLayer.GetLayerDefn()
      feature = ogr.Feature( featureDefn )
      feature.SetGeometry( result )
      feature.SetField( "Name", tag1 + '+' + tag2 )
      outLayer.CreateFeature( feature )

      feature.Destroy()

outDataSource.Destroy()
