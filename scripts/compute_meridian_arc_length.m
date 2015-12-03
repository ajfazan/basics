function s = compute_meridian_arc_length( a, f, lat1, lat2 )

  assert( size( lat1 ) == size( lat2 ) );
  assert( columns( lat1 ) == 3 );
  assert( columns( lat2 ) == 3 );

  n = size( lat1, 1 );

  e2 = f * ( 2.0 - f );

  e4 = e2 ^ 2; e6 = e2 ^ 3; e8 = e2 ^ 4; e10 = e2 ^ 5;

  A = 1.0 + sum( coeffs( 'A' ) * [ e2; e4; e6; e8; e10 ] );

  B = sum( coeffs( 'B' ) * [ e2; e4; e6; e8; e10 ] );

  C = sum( coeffs( 'C' ) * [ e4; e6; e8; e10 ] );

  D = sum( coeffs( 'D' ) * [ e6; e8; e10 ] );

  E = sum( coeffs( 'E' ) * [ e8; e10 ] );

  F = coeffs( 'F' ) * e10;

  s = zeros( n, 1 );
  kappa = ( pi / 180.0 );

  for k = 1 : n

    d = lat1( k, 1 );
    rlat1 = sign( d ) * ( abs( d ) + lat1( k, 2 ) /   60.0
                                   + lat1( k, 3 ) / 3600.0 );

    d = lat2( k, 1 );
    rlat2 = sign( d ) * ( abs( d ) + lat2( k, 2 ) /   60.0
                                   + lat2( k, 3 ) / 3600.0 );

    rlat1 *= kappa;
    rlat2 *= kappa;

    d = [ 2.0; 4.0; 6.0; 8.0; 10.0 ] * [ rlat1 rlat2 ];

    d = sin( d );
    d = d( : , 2 ) - d( : , 1 );

    d = [ B C D E F ] * d;

    d = ( 1.0 ./ [ -2.0 4.0 -6.0 8.0 -10.0 ] ) * d;

    l = abs( a * ( 1.0 - e2 ) * ( A * ( rlat2 - rlat1 ) + sum( d ) ) );
    s( k ) = str2double( sprintf( '%.4f', l ) );

  endfor

endfunction

function c = coeffs( id )

  if( id == 'A' )

    c( 1 ) =     3.0 /     4.0;
    c( 2 ) =    45.0 /    64.0;
    c( 3 ) =   175.0 /   256.0;
    c( 4 ) = 11025.0 / 16384.0;
    c( 5 ) = 43659.0 / 65536.0;

  elseif( id == 'B' )

    c( 1 ) =     3.0 /     4.0;
    c( 2 ) =    15.0 /    16.0;
    c( 3 ) =   525.0 /   512.0;
    c( 4 ) =  2205.0 /  2048.0;
    c( 5 ) = 72765.0 / 65536.0;

  elseif( id == 'C' )

    c( 1 ) =    15.0 /    64.0;
    c( 2 ) =   105.0 /   256.0;
    c( 3 ) =  2205.0 /  4096.0;
    c( 4 ) = 10395.0 / 16394.0;

  elseif( id == 'D' )

    c( 1 ) =    35.0 /    512.0;
    c( 2 ) =   315.0 /   2048.0;
    c( 3 ) = 31185.0 / 131072.0;

  elseif( id == 'E' )

    c( 1 ) =  315.0 / 16384.0;
    c( 2 ) = 3465.0 / 65536.0;

  elseif( id == 'F' )

    c( 1 ) = 639.0 / 131072.0;

  endif

endfunction
