#!/usr/bin/env osgeo_python

import argparse, os, sys
import numpy as np

try:
  from osgeo import ogr, osr
except:
  print( sys.stderr, "OGR module not found... Exiting" )
  sys.exit( 1 )

def isFile( pathname ):

  if not os.path.isfile( pathname ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( pathname ) )
  return pathname

def openDataset( filename, drivers ):

  ( base, ext ) = os.path.splitext( os.path.basename( filename ) )

  ext = ext.lower()

  if not( ext in drivers.keys() ):
    print( sys.stderr, "Unsupported input data set: " + filename )
    sys.exit( -1 )

  driver = ogr.GetDriverByName( drivers[ext] )

  dataset = driver.Open( filename, 0 )

  return driver, dataset

def createOutput( filename, drivers ):

  ( base, ext ) = os.path.splitext( os.path.basename( filename ) )

  ext = ext.lower()

  if not( ext in drivers.keys() ):
    print( sys.stderr, "Unsupported output data set: " + filename )
    sys.exit( -1 )

  driver = ogr.GetDriverByName( drivers[ext] )

  output = driver.CreateDataSource( filename )

  return output, base

def removeDuplicates( vertices, ths ):

  ( i, n ) = ( 0, len( vertices ) - 1 )

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

  return vertices

def cleanupGeometry( geom_ref, geom_type, rm_ths ):

  vertices = []

  for k in range( geom_ref.GetPointCount() ):
    vertices.append( geom_ref.GetPoint_2D( k ) )

  n = len( vertices )

  vertices = removeDuplicates( vertices, rm_ths )

  n -= len( vertices )

  geom = ogr.Geometry( geom_type )
  for k in range( len( vertices ) ):
    geom.AddPoint_2D( vertices[k][0], vertices[k][1] )

  return ( geom, n )

def parseFieldValue( field_type, feature, idx ):

  value = None

  if field_type == ogr.OFTInteger:
    value = feature.GetFieldAsInteger( idx )
  elif field_type == ogr.OFTInteger64:
    value = feature.GetFieldAsInteger64( idx )
  elif field_type == ogr.OFTReal:
    value = feature.GetFieldAsDouble( idx )
  elif field_type == ogr.OFTString:
    value = feature.GetFieldAsString( idx )

  return value

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

  src_defn = layer.GetLayerDefn()

  fields = {}

  for f in range( src_defn.GetFieldCount() ):
    field_defn = src_defn.GetFieldDefn( f )

    f_name = field_defn.GetNameRef()
    f_type = field_defn.GetType()

    field = ogr.FieldDefn( f_name, f_type )
    field.SetWidth( field_defn.GetWidth() )
    field.SetPrecision( field_defn.GetPrecision() )
    out_layer.CreateField( field )

    fields[f_name] = f_type

  if args.remove_holes:

    if ( geom_type == ogr.wkbPolygon ):

      for feature in layer:

        geom = feature.GetGeometryRef()

        poly = ogr.Geometry( ogr.wkbPolygon )
        poly.AddGeometry( geom.GetGeometryRef( 0 ) )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( poly )

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )

        out_layer.CreateFeature( out_feature )

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

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )

        out_layer.CreateFeature( out_feature )

  else:

    field = ogr.FieldDefn( "removed", ogr.OFTInteger )
    field.SetWidth( 8 )
    field.SetPrecision( 0 )
    out_layer.CreateField( field )

    ( total, modified, count ) = ( 0, 0, layer.GetFeatureCount() )

    if ( geom_type == ogr.wkbLineString ):

      for feature in layer:

        ( line, n ) = cleanupGeometry( feature.GetGeometryRef(), ogr.wkbLineString, args.ths )

        total += n

        modified += ( n > 0 )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( line )

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )
        out_feature.SetField( "removed", n )

        out_layer.CreateFeature( out_feature )

        out_feature.Destroy()

    elif ( geom_type == ogr.wkbMultiLineString ):

      for feature in layer:

        removed = 0

        src = feature.GetGeometryRef()

        multiline = ogr.Geometry( ogr.wkbMultiLineString )

        for k in range( src.GetGeometryCount() ):

          ( line, n ) = cleanupGeometry( src.GetGeometryRef( k ), ogr.wkbLineString, args.ths )

          total += n
          removed += n

          multiline.AddGeometry( line )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( multiline )

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )
        out_feature.SetField( "removed", removed )

        out_layer.CreateFeature( out_feature )

        out_feature.Destroy()

        modified += ( removed > 0 )

    elif ( geom_type == ogr.wkbPolygon ):

      for feature in layer:

        removed = 0

        src = feature.GetGeometryRef()

        polygon = ogr.Geometry( ogr.wkbPolygon )

        for k in range( src.GetGeometryCount() ):

          ( ring, n ) = cleanupGeometry( src.GetGeometryRef( k ), ogr.wkbLinearRing, args.ths )

          total += n
          removed += n

          polygon.AddGeometry( ring )

        polygon.CloseRings()

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( polygon )

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )
        out_feature.SetField( "removed", removed )

        out_layer.CreateFeature( out_feature )

        modified += ( removed > 0 )

    elif ( geom_type == ogr.wkbMultiPolygon ):

      for feature in layer:

        removed = 0

        ptr = feature.GetGeometryRef()

        multipolygon = ogr.Geometry( ogr.wkbMultiPolygon )

        for i in range( ptr.GetGeometryCount() ):

          src = ptr.GetGeometryRef( i )

          polygon = ogr.Geometry( ogr.wkbPolygon )

          for j in range( src.GetGeometryCount() ):

            ( ring, n ) = cleanupGeometry( src.GetGeometryRef( j ), ogr.wkbLinearRing, args.ths )

            total += n
            removed += n

            polygon.AddGeometry( ring )

          polygon.CloseRings()

          multipolygon.AddGeometry( polygon )

        out_feature = ogr.Feature( feature_defn )
        out_feature.SetGeometry( multipolygon )

        for name in fields.keys():
          idx = feature.GetFieldIndex( name )
          out_feature.SetField( name, parseFieldValue( fields[name], feature, idx ) )
        out_feature.SetField( "removed", removed )

        out_layer.CreateFeature( out_feature )

        modified += ( removed > 0 )

    if modified:
      print( ">> %d duplicate vertice(s) were removed from %d of %d feature(s)" \
           % ( total, modified, count ) )

  ( out_layer, layer ) = ( None, None )

  ( output, dataset ) = ( None, None )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--threshold', nargs = '?', type = float, dest = 'ths', default = 1e-6,
    help = 'specifies a threshold for point comparisons [default = 1e-6]' )

  parser.add_argument( '--remove_holes', action = 'store_true',
    help = 'remove holes from polygons or multi-polygons' )

  parser.add_argument( 'filename', type=isFile )
  parser.add_argument( 'outfile', type=str )

  args = parser.parse_args()

  main( args )
