#!/usr/bin/env python3

from osgeo import gdal, osr

import numpy as np

import argparse, math, os, sys

gdal.UseExceptions()

def unique( l ):

  n = len( l )

  for k in range( n - 1, 0, -1 ):
    if l[k] == l[0]:
      del l[k]

  return list( l )

def openImage( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    print( "Unable to open image %s" % filename )
    sys.exit( 1 )

  return handle

def main( args ):

  channels = []; pixels = []; transforms = []; projections = []; ntypes = []

  for f in args.files:
    img = openImage( f )
    assert( img.RasterCount == 1 ) # input image must be singleband
    band = img.GetRasterBand( 1 )
    array = np.array( band.ReadAsArray(), dtype = np.float64 )
    channels.append( array )

    ntypes.append( band.DataType )
    pixels.append( [ img.RasterXSize, img.RasterYSize ] )

    transforms.append( img.GetGeoTransform() )
    projections.append( img.GetProjectionRef() )

    img = None

  ntypes = unique( ntypes )
  pixels = unique( pixels )

  assert( len( ntypes ) == 1 )
  assert( len( pixels ) == 1 )

  ( cols, rows ) = ( pixels[0][0], pixels[0][1] )
  mask = np.ones( ( rows, cols ) )

  for band in channels:
    mask = np.logical_and( mask, band != args.nodata )

  back = np.logical_not( mask )

  for k in range( len( channels ) ):
    channels[k] *= mask
    channels[k][back] = args.nodata

  transforms = unique( transforms )
  projections = unique( projections )

  if ( ( len( transforms ) == 1 ) and ( len( projections ) == 1 ) ):

    ( cols, rows ) = ( pixels[0][0], pixels[0][1] )

    ( ulx, uly, xsize, ysize ) = ( transforms[0][0], \
                                   transforms[0][3], \
                                   transforms[0][1], \
                                   transforms[0][5]  )

    driver = gdal.GetDriverByName( 'GTiff' )
    opts = [ "TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES" ]
    outRaster = driver.Create( args.outfile, cols, rows, len( channels ), ntypes[0], options=opts )
    outRaster.SetGeoTransform( ( ulx, xsize, 0, uly, 0, ysize ) )

    for k in range( len( channels ) ):
      outband = outRaster.GetRasterBand( k + 1 )
      outband.WriteArray( channels[k] )
      outband.SetNoDataValue( args.nodata )
      outband.FlushCache()

    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt( projections[0] )
    outRaster.SetProjection( outRasterSRS.ExportToWkt() )

    outRaster = None

  else:
    print( "WARNING: Metadata of input imagery differ: No output will be generated" )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--outfile', type = str, dest = 'outfile',
    help = 'specifies the output filename for the resulting raster file' )

  parser.add_argument( '--nodata', nargs = '?', type = float, dest = 'nodata', default = 0.0,
    help = 'specifies a background value for the resulting raster file [default = 0.0]' )

  parser.add_argument( '--set-nodata', nargs = '+', type = float, dest = 'values',
    help = 'specifies one or more gray values to be replaced by nodata values' )

  parser.add_argument( 'files', nargs = '+', type = str )

  if len( sys.argv ) == 1:
    parser.print_usage()
    sys.exit( 0 )

  args = parser.parse_args()

  main( args )
