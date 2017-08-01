function [ d, m, s ] = decimal2dms( angle, tag = 'angle' )

  assert( numel( angle ) == 1 );

  s = sign( angle );
  v = abs( angle );

  d = fix( v );
  m = 60.0 * ( v - d );
  d *= s;

  tmp = fix( m );
  s = 60.0 * ( m - tmp );
  m = tmp;

  printf( '%s = %d %02d %08.5f\n\n', tag, d, m, s );

endfunction
