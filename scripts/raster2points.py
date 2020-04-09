#!/usr/bin/env osgeo_python

from osgeo import gdal, ogr, osr
import argparse, math, os, sys
import numpy as np

def isFile( p ):

  if not os.path.isfile( p ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( p ) )
  return p

def openRaster( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    sys.exit( 'Exception: Unable to open raster dataset {}'.format( filename ) )

  return handle

def openVector( filename ):

  drivers = dict()

  drivers['.shp'] = 'ESRI Shapefile'
  drivers['.geojson'] = 'GeoJSON'

  ext = os.path.splitext( os.path.basename( filename ) )
  ext = ext[1].lower()

  driver = ogr.GetDriverByName( drivers[ext] )

  handle = driver.Open( filename, 1 )

  if handle is None:
    sys.exit( 'Exception: Unable to open vector dataset {}'.format( filename ) )

  return handle

def createAffineTransform( params ):

  assert( len( params ) == 6 )

  a = np.array( [ [ params[1], params[2] ], [ params[4], params[5] ] ], dtype = np.float64 )
  b = np.array( [ [ params[0] ], [ params[3] ] ], dtype = np.float64 )

  return ( a, b )

def interpolateValue( px, band, null ):

  assert( len( px ) == 2 )

  ( dx, x ) = math.modf( px[0] )
  ( dy, y ) = math.modf( px[1] )

  i = int( y )
  j = int( x )

  u = i + 1
  v = j + 1

  g = dict()

  t = band[i][j]
  if t != null:
    g[1] = t

  t = band[i][v]
  if t != null:
    g[2] = t

  t = band[u][j]
  if t != null:
    g[3] = t

  t = band[u][v]
  if t != null:
    g[4] = t

  if len( g ) == 4:
    ga = dx * ( g[2] - g[1] ) + g[1]
    gb = dx * ( g[4] - g[3] ) + g[3]
    return ( dy * ( gb - ga ) + ga )

  return null;

def main( args ):

  gdal.UseExceptions()

  raster = openRaster( args.raster_file )
  vector = openVector( args.vector_file )

  layer = vector.GetLayer()

  if layer.GetGeomType() == ogr.wkbPoint:
    band = raster.GetRasterBand( args.band )
    null = band.GetNoDataValue()

    ( a, b ) = createAffineTransform( raster.GetGeoTransform() )

    i = np.linalg.inv( a )

    data = band.ReadAsArray()

    fields = []
    table = layer.GetLayerDefn()

    for k in range( table.GetFieldCount() ):
      fields.append( table.GetFieldDefn( k ).name )

    if not( args.field in fields ):
      field = ogr.FieldDefn( args.field, ogr.OFTReal )
      field.SetWidth( 16 )
      field.SetPrecision( 12 )
      layer.CreateField( field )

    for feature in layer:
      geom = feature.GetGeometryRef()
      point = geom.GetPoint()
      # compute inverse affine transformation for each point
      px = np.matmul( i, np.array( [ [ point[0] ], [ point[1] ] ] ) - b )

      v = interpolateValue( ( px[0][0], px[1][0] ), data, null )

      if v != null:
        # write interpolated value into created or existing field
        feature.SetField( args.field, v )
        layer.SetFeature( feature )

    layer.SyncToDisk()

    band = None

  else:
    print "Geometry type of input layer must be single point"

  raster = None

  vector.Destroy()

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--band', nargs = '?', type = int, default = 1,
    help = 'specified the raster band used to interpolate desired values' )

  parser.add_argument( '--field', nargs = '?', type = str, default = 'Z',
    help = 'specifies the field name where the interpolated results will be written to' )

  parser.add_argument( 'raster_file', type=isFile )
  parser.add_argument( 'vector_file', type=isFile )

  args = parser.parse_args()

  main( args )
