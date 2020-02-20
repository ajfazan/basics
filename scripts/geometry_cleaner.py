#!/usr/bin/env python

import argparse, os, sys
import numpy as np

try:
  from osgeo import ogr, osr
except:
  print sys.stderr, "OGR module not found... Exiting"
  sys.exit( 1 )

def isFile( pathname ):

  if not os.path.isfile( pathname ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( pathname ) )
  return pathname

def openDataset( filename, drivers ):

  ( base, ext ) = os.path.splitext( os.path.basename( filename ) )

  ext = ext.lower()

  if not( ext in drivers.keys() ):
    print sys.stderr, "Unsupported input data set: " + filename
    sys.exit( -1 )

  driver = ogr.GetDriverByName( drivers[ext] )

  dataset = driver.Open( filename, 0 )

  return driver, dataset

def createOutput( filename, drivers ):

  ( base, ext ) = os.path.splitext( os.path.basename( filename ) )

  ext = ext.lower()

  if not( ext in drivers.keys() ):
    print sys.stderr, "Unsupported output data set: " + filename
    sys.exit( -1 )

  driver = ogr.GetDriverByName( drivers[ext] )

  output = driver.CreateDataSource( filename )

  return output, base

def removeDuplicates( vertices, ths ):

  ( i, n ) = ( 0, len( vertices ) - 1 )

  temp = n + 1 # for debugging purposes

  while i < n:

    # r = range( i + 1, n )

    # a = np.array( vertices[i], dtype=np.float64 )

    # for j in r:

      # b = np.array( vertices[j], dtype=np.float64 )

      # if np.sum( np.fabs( a - b ) < ths ) > 0: # vertices[i] == vertices[j]

        # del vertices[j]
        # n -= 1
        # r = range( i + 1, n )

    # i += 1

    a = np.array( vertices[i], dtype=np.float64 )

    j = i + 1

    b = np.array( vertices[j], dtype=np.float64 )

    while np.sum( np.fabs( a - b ) < ths ) > 0: # vertices[i] == vertices[j]

      del vertices[j]
      n -= 1

      if ( j > n ):
        break
      else:
        b = np.array( vertices[j], dtype=np.float64 )

    i += 1

  print ( temp, len( vertices) ) # for debugging purposes

  return vertices

def main( args ):

  drivers = { ".shp": "ESRI Shapefile", ".geojson": "GeoJSON" }

  ( driver, dataset ) = openDataset( args.filename, drivers )

  layer = dataset.GetLayer()

  geom_type = layer.GetGeomType()

  ( output, layer_name ) = createOutput( args.outfile, drivers )

  crs = osr.SpatialReference()
  crs.ImportFromWkt( layer.GetSpatialRef().ExportToWkt() )

  out_layer = output.CreateLayer( layer_name, crs, geom_type )
  feature_defn = out_layer.GetLayerDefn()

  # Add an FID field
  pkey = ogr.FieldDefn( "FID", ogr.OFTInteger64 )
  pkey.SetWidth( 8 )
  out_layer.CreateField( pkey )

  fid = 1

  if args.remove_holes:

    if ( geom_type == ogr.wkbPolygon ):

      for feature in layer:

        geom = feature.GetGeometryRef()

        poly = ogr.Geometry( ogr.wkbPolygon )
        poly.AddGeometry( geom.GetGeometryRef( 0 ) )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( poly )
        out_feature.SetField( "FID", fid )

        out_layer.CreateFeature( out_feature )

        fid += 1

    elif ( geom_type == ogr.wkbMultiPolygon ):

      for feature in layer:

        src = feature.GetGeometryRef()

        multi = ogr.Geometry( ogr.wkbMultiPolygon )

        for k in range( src.GetGeometryCount() ):
          ptr = src.GetGeometryRef( k )
          poly = ogr.Geometry( ogr.wkbPolygon )
          poly.AddGeometry( ptr.GetGeometryRef( 0 ) )
          multi.AddGeometry( poly )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( multi )
        out_feature.SetField( "FID", fid )

        out_layer.CreateFeature( out_feature )

        fid += 1

  else:

    if ( geom_type == ogr.wkbLineString ):

      for feature in layer:

        src = feature.GetGeometryRef()

        vertices = []
        for k in range( src.GetPointCount() ):
          vertices.append( src.GetPoint_2D( k ) )

        vertices = removeDuplicates( vertices, args.ths )

        line = ogr.Geometry( ogr.wkbLineString )
        for k in range( len( vertices ) ):
          line.AddPoint_2D( vertices[k][0], vertices[k][1] )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( line )
        out_feature.SetField( "FID", fid )

        out_layer.CreateFeature( out_feature )

        out_feature.Destroy()

        fid += 1

    elif ( geom_type == ogr.wkbMultiLineString ):

      for feature in layer:

        src = feature.GetGeometryRef()

        geom = ogr.Geometry( ogr.wkbMultiLineString )

        for k in range( src.GetGeometryCount() ):

          ptr = src.GetGeometryRef( k )

          vertices = []
          for k in range( ptr.GetPointCount() ):
            vertices.append( ptr.GetPoint_2D( k ) )

          vertices = removeDuplicates( vertices, args.ths )

          line = ogr.Geometry( ogr.wkbLineString )
          for k in range( len( vertices ) ):
            line.AddPoint_2D( vertices[k][0], vertices[k][1] )

          geom.AddGeometry( line )

        feature_defn = out_layer.GetLayerDefn()
        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( geom )
        out_feature.SetField( "FID", fid )

        out_layer.CreateFeature( out_feature )

        out_feature.Destroy()

        fid += 1

  ( out_layer, layer ) = ( None, None )

  ( output, dataset ) = ( None, None )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--threshold', nargs = '?', type = float, dest = 'ths', default = 1e-6,
    help = 'specifies a threshold for point comparisons [default = 1e-6]' )

  parser.add_argument( '--remove_holes', action = 'store_true',
    help = 'remove holes from polygons or multi-polygons')

  parser.add_argument( 'filename', type=isFile )
  parser.add_argument( 'outfile', type=str )

  args = parser.parse_args()

  main( args )
