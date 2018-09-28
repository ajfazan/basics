#!/usr/bin/env python

from osgeo import gdal, osr

import numpy as np

import math, os, sys

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
    print "Unable to open image %s" % filename
    sys.exit( 1 )

  return handle

def main( argv ):

  out = argv[0]

  nodata = float( argv[1] )

  channels = []; pixels = []; transforms = []; projections = []; ntypes = []

  for f in argv[2:]:
    img = openImage( f )
    assert( img.RasterCount == 1 ) # image must be single-band
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

  transforms = unique( transforms )
  projections = unique( projections )

  if ( len( ntypes ) == 1 ) and \
     ( len( pixels ) == 1 ) and ( len( transforms ) == 1 ) and ( len( projections ) == 1 ):

    ( cols, rows ) = ( pixels[0][0], pixels[0][1] )
    m = np.ones( ( rows, cols ) )
    r = range( len( channels ) )

    for k in r:
      m *= ( channels[k] != nodata )

    ( ulx, uly, xsize, ysize ) = ( transforms[0][0], \
                                   transforms[0][3], \
                                   transforms[0][1], \
                                   transforms[0][5]  )

    driver = gdal.GetDriverByName( 'GTiff' )
    opts = [ "TILED=YES", "COMPRESS=LZW" ]
    outRaster = driver.Create( out, cols, rows, len( r ), ntypes[0], options=opts )
    outRaster.SetGeoTransform( ( ulx, xsize, 0, uly, 0, ysize ) )

    for k in r:
      channels[k] *= m
      outband = outRaster.GetRasterBand( k + 1 )
      outband.WriteArray( channels[k] )
      outband.SetNoDataValue( nodata )
      outband.FlushCache()

    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt( projections[0] )
    outRaster.SetProjection( outRasterSRS.ExportToWkt() )

    outRaster = None

  else:
    print "WARNING: Metadata of input imagery differ: No output will be generated"

  return 0

if __name__ == "__main__":

  if len( sys.argv ) < 4:
    print "Usage:"
    print "\t%s <OUT> <NODATA> <IMG1> <IMG2> [<IMG3>] ..." % os.path.basename( sys.argv[0] )
    sys.exit( -1 )

  main( sys.argv[1:] )
