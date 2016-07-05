from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

def displayFeatureInfo( feature ):

  geom = feature.geometry()
  print "Feature ID %d" % feature.id()

  if geom.type() == QGis.Point:
    x = geom.asPoint()
    print "Point: " + str( x )
  elif geom.type() == QGis.Line:
    x = geom.asPolyline()
    print "Line: %d points" % len( x )
  elif geom.type() == QGis.Polygon:
    x = geom.asPolygon()
    c = geom.centroid()
    a = geom.area()
    p = geom.length()
    n = 0
    print geom.isMultipart()
    print x
    for ring in x:
      n += len( ring )
    print "Polygon: %d ring(s) with %d points" % ( len( x ), n )
    print "Polygon area: %f" % a
    print "Polygon perimeter %f" % p
    print "Polygon centroid: " + str( c.asPoint() )
  else:
    print "Unknown"

def isSameFeature( f1, f2 ):

  g1 = f1.geometry()
  g2 = f2.geometry()

  if ( g1.type() == QGis.Polygon ) and ( g2.type() == QGis.Polygon ):

    a1 = g1.area()
    a2 = g2.area()

    if a1 == a2:

      p1 = g1.length()
      p2 = g2.length()

      if p1 == p2:

        c1 = g1.centroid()
        c2 = g2.centroid()

        return c1.asPoint() == c2.asPoint()

  return False

def deleteHoles( layer, name ):

  crs = layer.crs()

  result = QgsVectorLayer( 'Polygon?crs=' + crs.authid(), name, "memory" )
  pr = result.dataProvider()

  iterator = layer.getFeatures()

  for feature in iterator:

    geom = feature.geometry()

    if geom.isMultipart():
      mp = geom.asMultiPolygon()
      for p in mp:
        for ring in p[1:]:
          p.remove( ring )
      geom = QgsGeometry.fromMultiPolygon( mp )

    else:
      p = geom.asPolygon()
      for ring in p[1:]:
        p.remove( ring )
      geom = QgsGeometry.fromPolygon( p )

    f = QgsFeature()
    f.setGeometry( geom )
    f.setAttributes( feature.attributes() )
    pr.addFeatures( [f] )

  result.updateExtents()
  return result

def removeInnerRings( layer, name ):

  crs = layer.crs()

  result = QgsVectorLayer( 'Polygon?crs=' + crs.authid(), name, "memory" )
  pr = result.dataProvider()

  iterator = layer.getFeatures()

  for feature in iterator:

    geom = feature.geometry()

    if not geom.isMultipart():

      if geom.type() == QGis.Polygon:

        p = geom.asPolygon()
        if len( p ) == 1: # 1 ring == simple polygon

          # print "Vertices: %d" % len( p[0] )

          l = len( p[0] ) - 1
          i = 0

          while i < l:

            v = p[0][i]

            s = p[0][i+1:-1]

            if v in s:

              j = s.index( v ) + i + 1
              # print "index = %d" % j
              del( p[0][i+1:j+1] )
              l = len( p[0] ) - 1
              # print p[0]

            i += 1

          # print "Vertices: %d" % len( p[0] )
          geom = QgsGeometry.fromPolygon( p )

    f = QgsFeature()
    f.setGeometry( geom )
    f.setAttributes( feature.attributes() )
    pr.addFeatures( [f] )

  result.updateExtents()
  return result

def removeDuplicates( layer, name ):

  crs = layer.crs()

  result = QgsVectorLayer( 'Polygon?crs=' + crs.authid(), name, "memory" )
  pr = result.dataProvider()

  iterator = layer.getFeatures()

  for feature in iterator:

    geom = feature.geometry()

    if geom.type() == QGis.Polygon:

      p = geom.asPolygon()
      if len( p ) == 1: # 1 ring == simple polygon

        # print "Vertices: %d" % len( p[0] )

        l = len( p[0] ) - 1
        i = 0

        while i < l:

          v = p[0][i]

          s = p[0][i+1:-1]

          if v in s:

            j = s.index( v ) + i + 1
            # print "index = %d" % j
            del( p[0][i+1:j+1] )
            l = len( p[0] ) - 1
            # print p[0]

          i += 1

        # print "Vertices: %d" % len( p[0] )
        geom = QgsGeometry.fromPolygon( p )

    f = QgsFeature()
    f.setGeometry( geom )
    f.setAttributes( feature.attributes() )
    pr.addFeatures( [f] )

  result.updateExtents()
  return result
