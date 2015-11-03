#!/usr/bin/perl -w

use File::Basename;

if( @ARGV != 3 ) {

  print "\nUsage:\n";
  print sprintf( "\t%s <DAY> <MONTH> <YEAR>\n", basename( $0 ) );
  exit( -1 );
}

( $day, $month, $year ) = @ARGV;

@days = ( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );

unless( $year % 4 ) {

  $days[1] += 1;
}

$julian = $day;

for( $m = $month - 2; $m >= 0; $m -= 1 ) {

  $julian += $days[$m];
}

print sprintf( "%02d/%02d/%d = %d\n", $day, $month, $year, $julian );
