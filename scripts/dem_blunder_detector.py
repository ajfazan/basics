#!/usr/bin/env python

from osgeo import gdal, ogr, osr
from scipy.signal import *
from tempfile import gettempdir
import numpy as np
import argparse, math, os, sys

def openImage( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    print "Unable to open image %s" % filename
    sys.exit( 1 )

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

  # ~ f = np.zeros( ( n, n ) )

  # ~ domain = range( n )

  # ~ sigma /= 100.0
  # ~ sigma *= radius
  # ~ var = sigma ** 2
  # ~ k = -1.0 / ( math.pi * var * var )
  # ~ var *= 2.0

  # ~ for y in domain:
    # ~ for x in domain:
      # ~ alpha = ( ( x - radius ) ** 2 + ( y - radius ) ** 2 ) / var
      # ~ f[y,x] = k * ( 1.0 - alpha ) * math.exp( -alpha )

  # ~ f = np.zeros( ( 1, n ) )

  # ~ for k in range( radius ):
    # ~ f[0, k] = -( 1 + k )
    # ~ f[0, n - k - 1] = f[0, k]

  # ~ f[0, radius] = abs( np.sum( f ) )

  # ~ f = np.matmul( np.transpose( f ), f )

  # ~ f *= ( sigma / np.std( f ) )

  f = -np.ones( ( 3,3 ), dtype = float )

  f[1, 1] = 8.0

  return f

def main( args ):

  gdal.UseExceptions()

  dem = openImage( args.filename )

  n = dem.RasterCount
  assert( n == 1 )

  log = createLOGFilter( args.radius, args.sigma )

  band = dem.GetRasterBand( 1 )
  null = band.GetNoDataValue()

  array = np.array( band.ReadAsArray(), dtype = np.float64 )

  filtered = convolve2d( array, log, boundary = 'symm', mode = 'same' )

  filtered *= np.logical_and( filtered >= -25.0, filtered <= 25.0 )

  filtered = np.logical_or( filtered <= -args.cutoff, filtered >= args.cutoff )

  base = os.path.splitext( os.path.basename( args.filename ) )[0]
  output = args.outdir + os.sep + base + ".shp"

  tmp = [ gettempdir() + os.sep + base ]
  tmp.append( tmp[0] )
  tmp.append( tmp[0] )

  tmp[0] += ".f.tif"
  tmp[1] += ".m.tif"
  tmp[2] += ".a.shp"

  crs = dem.GetProjectionRef()
  geo = dem.GetGeoTransform()

  createTempRaster( tmp[0], crs, geo, filtered * ( array != band.GetNoDataValue() ) )
  img0 = openImage( tmp[0] )
  band = img0.GetRasterBand( 1 )

  createTempRaster( tmp[1], crs, geo, band.ReadAsArray() != band.GetNoDataValue() )
  img1 = openImage( tmp[1] )
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

  ds.Destroy()
  driver.DeleteDataSource( tmp[2] )

  result.Destroy()

  img0 = None
  img1 = None

  os.remove( tmp[0] )
  os.remove( tmp[1] )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--radius', nargs = '?', type = int  , dest = 'radius', default = 3,
    help = 'specifies a radius for the Laplace filter [default = 3]' )

  # parser.add_argument( '--sigma' , nargs = '?', type = float, dest = 'sigma' , default = 50.0,
  #   help = 'specifies a sigma value for the Laplace filter as a % of the radius [default = 50]' )

  parser.add_argument( '--sigma' , nargs = '?', type = float, dest = 'sigma' , default = 1.0,
    help = 'specifies a sigma value for the Laplace filter [default = 1.0]' )

  parser.add_argument( '--area', nargs = '?', type = int, dest = 'area', default = 50,
    help = 'specifies an area threshold (in pixels) to keep extracted features [default = 50]' )

  parser.add_argument( '--cutoff', nargs = '?', type = float, dest = 'cutoff', default = 0.05,
    help = 'specifies a threshold to threshold the filtered DEM [default = 0.05]' )

  parser.add_argument( 'filename' )
  parser.add_argument( 'outdir' )

  args = parser.parse_args()

  # print args.radius
  # print args.sigma
  # print args.area
  # print args.cutoff
  # print args.filename
  # print args.outdir

  main( args )
