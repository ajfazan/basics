#!/usr/bin/env python

from osgeo import gdal, ogr, osr
from scipy.signal import *
from tempfile import gettempdir
import numpy as np
import argparse, math, os, sys

def isFile( p ):

  if not os.path.isfile( p ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( p ) )
  return p

def isDir( p ):

  if not os.path.isdir( p ):
    raise argparse.ArgumentTypeError( "{0} is not a directory".format( p ) )
  return p

def openRaster( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    sys.exit( 'Exception: Unable to open raster dataset {}'.format( filename ) )

  has_nodata = True
  for k in range( 1, 1 + handle.RasterCount ):
    band = handle.GetRasterBand( k )
    nodata = band.GetNoDataValue()
    has_nodata = ( has_nodata and ( not nodata is None ) )

  if not has_nodata:
    sys.exit( 'Exception: Raster dataset {} has no defined nodata value'.format( filename ) )

  return handle

def createTempRaster( filename, crs, geo, array ):

  driver = gdal.GetDriverByName( "GTiff" )

  raster = driver.Create( filename, array.shape[1], array.shape[0], 1, gdal.GDT_Byte )
  raster.SetGeoTransform( geo )
  raster.SetProjection( crs )

  band = raster.GetRasterBand( 1 )
  band.WriteArray( array )
  band.SetNoDataValue( 0 )
  band.FlushCache()

  raster = None

def createLOGFilter( radius, sigma ):

  n = 2 * radius + 1

  g = np.zeros( ( n, n ) )

  k1 = 2.0 * sigma ** 2
  k2 = math.pi * k1

  domain = range( n )

  for y in domain:
    for x in domain:
      alpha = ( ( x - radius ) ** 2 + ( y - radius ) ** 2 ) / k1
      g[y, x] = math.exp( -alpha ) / k2

  l = -np.ones( ( 3,3 ), dtype = float )

  l[1, 1] = 8.0

  return g, l

def main( args ):

  gdal.UseExceptions()

  dem = openRaster( args.filename )

  n = dem.RasterCount
  assert( n == 1 )

  g, l = createLOGFilter( args.radius, args.sigma )

  band = dem.GetRasterBand( 1 )
  null = band.GetNoDataValue()

  array = np.array( band.ReadAsArray(), dtype = np.float64 )

  ## apply Gaussian filter
  filtered = convolve2d( array, g, boundary = 'symm', mode = 'same' )

  ## apply Laplacian filter
  filtered = convolve2d( filtered, l, boundary = 'symm', mode = 'same' )

  filtered *= np.logical_and( filtered >= -25.0, filtered <= 25.0 )

  filtered = np.logical_or( filtered <= -args.cutoff, filtered >= args.cutoff )

  base = os.path.splitext( os.path.basename( args.filename ) )[0]
  output = args.outdir + os.sep + base + ".shp"

  tmp = [ gettempdir() + os.sep + base ]
  tmp.append( tmp[0] )
  tmp.append( tmp[0] )

  tmp[0] += ".tif"
  tmp[1] += ".mask.tif"
  tmp[2] += ".shp"

  crs = dem.GetProjectionRef()
  geo = dem.GetGeoTransform()

  createTempRaster( tmp[0], crs, geo, filtered * ( array != band.GetNoDataValue() ) )
  img0 = openRaster( tmp[0] )
  band = img0.GetRasterBand( 1 )

  createTempRaster( tmp[1], crs, geo, band.ReadAsArray() != band.GetNoDataValue() )
  img1 = openRaster( tmp[1] )
  mask = img1.GetRasterBand( 1 )

  crs = osr.SpatialReference()
  crs.ImportFromWkt( dem.GetProjectionRef() )

  driver = ogr.GetDriverByName( "ESRI Shapefile" )

  ds = driver.CreateDataSource( tmp[2] )
  layer1 = ds.CreateLayer( "temp", crs, ogr.wkbPolygon )

  gdal.Polygonize( band, mask, layer1, -1, [], callback = None )

  result = driver.CreateDataSource( output )
  layer2 = result.CreateLayer( base, crs, ogr.wkbPolygon )

  fidField = ogr.FieldDefn( "FID", ogr.OFTInteger64 )
  fidField.SetWidth( 8 )
  layer2.CreateField( fidField )

  areaField = ogr.FieldDefn( "AREA", ogr.OFTReal )
  areaField.SetWidth( 15 )
  areaField.SetPrecision( 6 )
  layer2.CreateField( areaField )

  feature_defn =layer2.GetLayerDefn()
  fid = 1

  min_area = args.area * math.sqrt( -geo[1] * geo[5] )

  for feature1 in layer1:

    geom = feature1.GetGeometryRef()
    area = geom.GetArea()

    if area >= min_area:
      feature2 = ogr.Feature( feature_defn )
      feature2.SetGeometry( feature1.GetGeometryRef() )
      feature2.SetField( "FID", fid )
      feature2.SetField( "AREA", area )
      layer2.CreateFeature( feature2 )
      fid += 1

  count = layer2.GetFeatureCount()

  if not args.quiet:
    print "%d/%d features before/after cleanup process" % ( layer1.GetFeatureCount(), count )

  ds.Destroy()
  driver.DeleteDataSource( tmp[2] )

  result.Destroy()

  if count == 0 and args.purge:
    driver.DeleteDaSource( output )

  img0 = None
  img1 = None

  os.remove( tmp[0] )
  os.remove( tmp[1] )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--radius', nargs = '?', type = int, dest = 'radius', default = 2,
    help = 'specifies a radius for the Gaussian filter [default = 2]' )

  parser.add_argument( '--sigma', nargs = '?', type = float, dest = 'sigma', default = 1.0,
    help = 'specifies a sigma value for the Gaussian filter [default = 1.0]' )

  parser.add_argument( '--area', nargs = '?', type = int, dest = 'area', default = 50,
    help = 'specifies an area threshold (in pixels) to keep extracted features [default = 50]' )

  parser.add_argument( '--cutoff', nargs = '?', type = float, dest = 'cutoff', default = 0.05,
    help = 'specifies a threshold to threshold the filtered DEM [default = 0.05]' )

  parser.add_argument( '--quiet', action = 'store_true', help = 'suppress progress messages' )

  parser.add_argument( '--purge', action = 'store_true', help = 'remove an empty resulting dataset')

  parser.add_argument( 'filename', type=isFile )
  parser.add_argument( 'outdir', type=isDir )

  args = parser.parse_args()

  main( args )
