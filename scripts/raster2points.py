#!/usr/bin/env python

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

  a = np.array( [ [ params[1], params[2] ], [ params[4], params[5] ] ] )
  b = np.array( [ [ params[0] ], [ params[3] ] ] )

  return ( a, b )

def main( args ):

  gdal.UseExceptions()

  raster = openRaster( args.raster_file )
  vector = openVector( args.vector_file )

  band = raster.GetRasterBand( args.band )
  null = band.GetNoDataValue()

  ( a, b ) = createAffineTransform( raster.GetGeoTransform() )

  i = np.linalg.inv( a )

  data = band.ReadAsArray()

  layer = vector.GetLayer()
  for feature in layer:
    geom = feature.GetGeometryRef()
    point = geom.GetPoint()
    # compute inverse affine transformation for each point
    px = np.matmul( i, np.array( [ [ point[0] ], [ point[1] ] ] ) - b )

    print ( px[0][0], px[1][0] )

    # print point
    # print feature.GetField( "ALT_ORTO" )

    # retrieve values from data
    # compute interpolated value
    # write value into created or existing field

  layer.ResetReading()

  # print ( h.RasterYSize, h.RasterXSize )
  # print h.RasterCount
  # print null

  band = None
  raster = None
  vector = None

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--band', nargs = '?', type = int, default = 1,
    help = 'specified the raster band used to interpolate desired values')

  parser.add_argument( '--field', nargs = '?', type = str, default = 'Z',
    help = 'specifies the field name where the interpolated results will be written to' )

  parser.add_argument( 'raster_file', type=isFile )
  parser.add_argument( 'vector_file', type=isFile )

  args = parser.parse_args()

  main( args )
