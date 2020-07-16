
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

  @staticmethod
  def histogram_bins_iterator( data_type ):

    typename = gdal.GetDataTypeName( data_type )

    if typename == 'Byte':
      ( first, last ) = ( 0, 256 )
    elif typename == 'Int16':
      ( first, last ) = ( -32768, 32768 )
    elif typename == 'UInt16':
      ( first, last ) = ( 0, 65536 )

    while first <= last:
      yield first
      first += 1

  def GetBand( self, num, load = False ):
    """
    Get handle to a raster band, or (optionally) load a raster band into an array
    """

    if num <= self.handle_.RasterCount:
      band = self.handle_.GetRasterBand( num )
      if load == True:
        band = band.ReadAsArray()
      return band

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

  def ComputeBandHistogram( self, num, normalized = False ):
    """
    Compute histogram for a particular raster band
    """

    band = self.GetBand( num )
    buckets = list( raster.histogram_bins_iterator( band.DataType ) )
    band = band.ReadAsArray()
    hist = np.histogram( band, bins = buckets )

    assert( buckets == hist[1].tolist() )

    hist = dict( zip( hist[1].tolist(), hist[0].tolist() ) )

    nodata = self.GetBandNoData( num )

    if nodata is None:
      pixels = float( band.Xsize * band.Ysize )
    else:
      pixels = float( np.sum( band != nodata ) )
      if nodata in hist.keys():
        del hist[nodata]

    assert( pixels == sum( hist.values() ) )

    if normalized:
      for dn in list( hist.keys() ):
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

    p = np.array( list( hist.values() ) )

    return -np.sum( p * np.log2( p ) )
