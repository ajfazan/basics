function abs( x ) {

  return x < 0.0 ? -x : x
}

{
  H = $2 - $3

  if( abs( H - $4 ) >= THS ) {

    print sprintf( "%s | %.4f | %.4f | %.4f | %.4f", $1, $2, $3, $4, H )
  }
}
