#!/usr/bin/perl -w

use File::Basename;

if( @ARGV != 2 ) {

  print "\nUsage:\n";
  print sprintf( "\t%s <JULIAN_DAY> <YEAR>\n", basename( $0 ) );
  exit( -1 );
}

( $julian, $year ) = @ARGV;

@days = ( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );

unless( $year % 4 ) {

  $days[1] += 1;
}

$month = 0;

while( $julian >= $days[$month] ) {

  $julian -= $days[$month];
  $month += 1;
}

print sprintf( "%02d/%02d/%d\n", $julian, $month + 1, $year );
