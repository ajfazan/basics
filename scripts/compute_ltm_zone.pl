#!/usr/bin/perl -w

use POSIX;
use File::Basename;

$longitude = 0;

$argc = @ARGV;
$rem = $argc % 2;

if( ( $argc == 0 ) || ( $rem != 0 ) && ( $rem != 1 ) ) {

  print "\nUsage:\n";
  print sprintf( "\t%s <LONGITUDE> [<POINT_ID>]\n", basename( $0 ) );
  print sprintf( "\t%s <LON_DD> <LON_MM> <LON_SS> [<POINT_ID>]\n", basename( $0 ) );
  exit( -1 );
}

if( $rem == 0 ) {

  $point = pop( @ARGV );
  $argc -= 1;
}

if( $argc == 1 ) {

  ( $longitude ) = @ARGV;

} else {

  ( $lon_dd, $lon_mm, $lon_ss ) = @ARGV;

  $factor1 = abs( $lon_dd );

  $factor2 = $factor1 / $lon_dd;

  $longitude = $factor2 * ( $factor1 + $lon_mm / 60.0 + $lon_ss / 3600.0 );
}

$zone = floor( $longitude + 180 ) % 360 + 1;

if( $rem ) {

  print sprintf( "LTM Zone: %02d\n", $zone );

} else {

  print sprintf( "Point: %s | LTM Zone: %02d\n", $point, $zone );
}
