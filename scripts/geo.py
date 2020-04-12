
from core import *

class raster:

  def __init__( self, filename ):
    """
    Constructor
    """
    self.handle_ = gdal.Open( filename )

    if self.handle_ is None:
      sys.exit( "Exception: Unable to open raster dataset {0}".format( filename ) )

    self.band_nodata_ = {}

    for k in range( 1, 1 + self.handle_.RasterCount ):
      band = self.handle_.GetRasterBand( k )
      nodata = band.GetNoDataValue()
      if not( nodata is None ):
        self.band_nodata_[k] = nodata

  def LoadBand( self, num ):
    """
    Load a raster band into an array
    """

    if num <= self.handle_.RasterCount:
      band = self.handle_.GetRasterBand( num )
      return band.ReadAsArray()

    return None

  def GetBandCount( self ):
    """
    Get the number of bands in a raster dataset
    """

    return self.handle_.RasterCount

  def GetBandList( self ):
    """
    Get a list of indices for all bands in a raster dataset
    """

    return list( range( 1, self.handle_.RasterCount + 1 ) )

  def GetBandNoData( self, num ):
    """
    Get the nodata value (if exists) corresponding to a raster band indexed by num
    """

    nodata = None

    if num <= self.handle_.RasterCount:
      try:
        nodata = self.band_nodata_[num]
      except:
        print( sys.stderr, "Raster band [%d] has no defined nodata value" % num )

    return nodata

  def GetBandInfo( self, num ):
    """
    Get basic band statistics
    """

    if num > self.handle_.RasterCount:
      sys.exit( "Index [{0}] out of bounds".format( num ) )
      return None

    info = {}

    info['nodata'] = self.GetBandNoData( num )

    band = self.handle_.GetRasterBand( num )

    min_dn = band.GetMinimum()
    max_dn = band.GetMaximum()

    if not min_dn or not max_dn:
      ( min_dn, max_dn ) = band.ComputeRasterMinMax( True )

    info['min'] = int( min_dn )
    info['max'] = int( max_dn )

    return info

  def ComputeBandHistogram( self, num, normalized = False ):
    """
    Compute histogram for a particular raster band
    """

    hist = {}

    band = self.LoadBand( num )
    info = self.GetBandInfo( num )

    for dn in range( info['min'], info['max'] + 1 ):
      hist[dn] = np.sum( band == dn )

    pixels = 0.0

    if info['nodata'] is None:
      pixels = float( band.Xsize * band.Ysize )
    else:
      pixels = float( np.sum( band != info['nodata'] ) )
      if hist.has_key( info['nodata'] ):
        del hist[info['nodata']]

    assert( pixels == sum( hist.values() ) )

    if normalized:
      for dn in hist.keys():
        if hist[dn] == 0:
          del hist[dn]
        else:
          hist[dn] /= pixels

    return hist

  def ComputeBandEntropy( self, num ):
    """
    Compute entropy for a particular raster band
    """

    hist = self.ComputeBandHistogram( num, True )

    result = 0.0
    for p in hist.values():
      result += ( p * math.log( p, 2.0 ) )

    return abs( result )
