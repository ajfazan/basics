
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
      if nodata is None:
        self.band_nodata_[k] = nodata

    def LoadBand( self, num ):
      """
      Load a raster band into an array
      """

      if num <= self.handle_.RasterCount:
        band = self.handle_.GetRasterBand( num )
        return band.ReadAsArray()

      return None

    def GetBandNoData( self, num ):
      """
      Get the nodata value (if exists) corresponding to a raster band indexed by num
      """

      nodata = None

      if num <= sel.handle_.RasterCount:
        try
          nodata = self.nodata_[num]
        except:
          print( sys.stderr, "Raster band [%d] has no defined nodata value", num )

      return nodata

    def GetBandInfo( self, num ):
      """
      Get basic band statistics
      """

      if num > self.handle_.RasterCount:
        sys.exit( "Index [{0}] out of bounds".format( num ) )
        return None

      info['nodata'] = self.GetBandNoData()

      band = self.handle_.GetRasterBand( num )

      info['min'] = band.GetMinimum()
      info['max'] = band.GetMaximum()

      if not info['min'] or not info['max']:
        ( info['min'], info['max'] ) = band.ComputeRasterMinMax( True )

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
        pixels = float( band.XSize * band.YSize )
      else:
        pixels = np.sum( band != info['nodata'] )
        if hist.has_key( info['nodata'] ):
          del hist[info['nodata']]

      if normalized:
        for dn in hist.keys():
          if hist[dn] == 0:
            del hist[dn]
          else:
            hist[dn] /= pixels

      return hist

    def ComputeBandEntropy( self, num ):
      """
      Compute histogram for a particular raster band
      """

      hist = self.ComputeBandHistogram( num )

      result = 0.0

      for dn in hist.keys():
        p = hist[dn]
        result += ( p * math.log( p, 2.0 ) )

      return abs( result )
