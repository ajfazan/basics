
import argparse, math, os, sys

try:
  from osgeo import gdal, ogr, osr
except:
  sys.exit( "[ERROR]: GDAL modules not found..." )

import numpy as np

def isFile( pathname ):

  if not os.path.isfile( pathname ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( pathname ) )
  return pathname

def isDir( pathname ):

  if not os.path.isdir( pathname ):
    raise argparse.ArgumentTypeError( "{0} is not a directory".format( pathname ) )
  return pathname

def openRaster( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    sys.exit( "Exception: Unable to open raster dataset {0}".format( filename ) )

  has_nodata = True
  for k in range( 1, 1 + handle.RasterCount ):
    band = handle.GetRasterBand( k )
    nodata = band.GetNoDataValue()
    has_nodata = ( has_nodata and ( not nodata is None ) )

  if not has_nodata:
    sys.exit( "Exception: Raster dataset {0} has no defined nodata value".format( filename ) )

  return handle

def openVector( filename, mode = 1 ):

  drivers = { ".shp": "ESRI Shapefile", ".geojson": "GeoJSON" }

  ( base, ext ) = os.path.splitext( os.path.basename( filename ) )

  ext = ext.lower()

  if not( ext in drivers.keys() ):
    sys.exit( "Unsupported driver for vector dataset {0}".format( filename ) )

  driver = ogr.GetDriverByName( drivers[ext] )

  handle = driver.Open( filename, mode )

  if handle is None:
    sys.exit( "Exception: Unable to open vector dataset {0}".format( filename ) )

  return handle, base
