function beta = dms2decimal( alpha )

  assert( isvector( alpha ) );

  assert( numel( alpha ) == 3 );

  d = alpha( 1 );
  m = alpha( 2 );
  s = alpha( 3 );

  assert( m >= 0.0 );
  assert( s >= 0.0 );

  beta = sign( d ) * ( abs( d ) + m / 60.0 + s / 3600.0 );

endfunction
