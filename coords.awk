function abs( x ) {

  return x < 0.0 ? -x : x
}

{
  dx = $4 - $2
  dy = $5 - $3

  delta = sqrt( dx * dx + dy * dy )

  if( ( abs( dx ) >= THS ) || ( abs( dy ) >= THS ) ) {

    print sprintf( "%8s | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f",
                   $1, $2, $3, $4, $5, dx, dy, delta )
  }
}
