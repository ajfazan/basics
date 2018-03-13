#!/usr/bin/perl -w

use POSIX;
use File::Basename;

$longitude = 0;

$argc = @ARGV;

if( ( $argc != 1 ) && ( $argc != 3 ) ) {

  print "\nUsage:\n";
  print sprintf( "\t%s <LONGITUDE>\n", basename( $0 ) );
  print sprintf( "\t%s <LON_DD> <LON_MM> <LON_SS>\n", basename( $0 ) );
  exit( -1 );

}

if( $argc == 1 ) {

  ( $longitude ) = @ARGV;

} else {

  ( $lon_dd, $lon_mm, $lon_ss ) = @ARGV;

  $factor1 = abs( $lon_dd );

  $factor2 = $factor1 / $lon_dd;

  $longitude = $factor2 * ( $factor1 + $lon_mm / 60.0 + $lon_ss / 3600.0 );
}

$zone = floor( ( $longitude + 180 ) / 6 ) % 60 + 1;

print sprintf( "zone = %02d\n", $zone );
