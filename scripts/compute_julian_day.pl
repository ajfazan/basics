#!/usr/bin/perl -w

use File::Basename;
# use Test::Unit::TestCase;

if( @ARGV != 3 ) {

  print "\nUsage:\n";
  print sprintf( "\t%s <YEAR> <MONTH> <DAY>\n", basename( $0 ) );
  exit( -1 );
}

( $year, $month, $day ) = @ARGV;

# $self->assert( $month >=  1 );
# $self->assert( $month <= 12 );

@days = ( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );

# $self->assert( $day >= 1 );
# $self->assert( $day <= $days[$month] );

unless( $year % 4 ) {

  $days[1] += 1;
}

$julian = $day;

for( $m = $month - 2; $m >= 0; $m -= 1 ) {

  $julian += $days[$m];
}

print sprintf( "%02d/%02d/%d = %d\n", $day, $month, $year, $julian );
