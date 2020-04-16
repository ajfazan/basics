#!/usr/bin/env osgeo_python

from geo import *

def main( args ):

  dataset = raster( args.filename )

  bands = dataset.GetBandList()

  for num in bands:
    e = dataset.ComputeBandEntropy( num )
    print( "[%d]: %.12f" % ( num, e ) )

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( 'filename', type=isFile )

  args = parser.parse_args()

  main( args )
