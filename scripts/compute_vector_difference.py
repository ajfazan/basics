#!/usr/bin/env osgeo_python

from osgeo import ogr, osr
import os, sys

def openDataSource( filename ):

  driver = ogr.GetDriverByName( "ESRI Shapefile" )

  ds = driver.Open( filename, 0 )

  if ds is None:
    print "Unable to open %s", filename
    sys.exit( -1 )

  return ds

def printGeometryInfo( g ):

  print "Geometry name:", g.GetGeometryName()
  print "Geometry count:", g.GetGeometryCount()

def main( argv ):

  ds1 = openDataSource( argv[0] )
  ds2 = openDataSource( argv[1] )

  l1 = ds1.GetLayer()
  l2 = ds2.GetLayer()

  sr1 = l1.GetSpatialRef()
  sr2 = l2.GetSpatialRef()

  wkt1 = sr1.ExportToWkt()
  wkt2 = sr2.ExportToWkt()

  if wkt1 != wkt2:
    print "WARNING: Spatial reference systems differ... Unable to compute result"
    return 0

  geom1_type = l1.GetGeomType()
  geom2_type = l2.GetGeomType()

  if ( geom1_type == ogr.wkbPolygon ) and ( geom2_type == ogr.wkbPolygon ):

    out_driver = ogr.GetDriverByName( "ESRI Shapefile" )

    # Remove the output shapefile if it already exists
    if os.path.exists( argv[2] ):
      try:
        out_driver.DeleteDataSource( argv[2] )
      except:
        print sys.stderr, "Unable to delete existing dataset" + argv[2]
        sys.exit( 1 )

    out_ds = out_driver.CreateDataSource( argv[2] )

    sr = osr.SpatialReference()
    sr.ImportFromWkt( wkt1 )

    layer_name = os.path.splitext( os.path.basename( argv[2] ) )[0]
    out_layer = out_ds.CreateLayer( layer_name, sr, ogr.wkbPolygon )
    out_layer.CreateField( ogr.FieldDefn( "ID", ogr.OFTInteger64 ) )

    r1 = range( l1.GetFeatureCount() )
    r2 = range( l2.GetFeatureCount() )

    fid = 0

    for k1 in r1:

      f1 = l1.GetNextFeature()
      g1 = ogr.Geometry( ogr.wkbPolygon )
      g1 = g1.Union( f1.GetGeometryRef() )

      for k2 in r2:

        f2 = l2.GetNextFeature()
        g2 = ogr.Geometry( ogr.wkbPolygon )
        g2 = g2.Union( f2.GetGeometryRef() )

        g1 = g1.Difference( g2 )

      if ( not g1.IsEmpty() ) and ( g1.GetGeometryType() == ogr.wkbPolygon ):

        # Create the feature and set values
        feature_defn = out_layer.GetLayerDefn()
        feature = ogr.Feature( feature_defn )
        feature.SetGeometry( g1 )
        feature.SetField( "ID", fid )
        out_layer.CreateFeature( feature )

        feature.Destroy()

      l2.ResetReading()

    out_ds.Destroy()

  return 0

if __name__ == "__main__":

  if len( sys.argv ) != 4:
    print "Usage:\n\t%s <DS1> <DS2> <OUT_DS>" % os.path.basename( sys.argv[0] )
    sys.exit( 1 )

  r =  main( sys.argv[1:] )

  sys.exit( r )
