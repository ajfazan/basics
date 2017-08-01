function zone = utm_zone( lon )

  n = numel( lon );
  assert( or( n == 1, n == 3 ) );

  if( n == 3 )

    assert( lon( 2 ) >= 0.0 );
    assert( lon( 3 ) >= 0.0 );

    n = sign( lon( 1 ) );

    lon = n * ( abs( lon( 1 ) ) + lon( 2 ) / 60.0 + lon( 3 ) / 3600.0 );

  endif

  zone = rem( floor( ( lon + 180 ) / 6 ) + 1, 60 );

endfunction
