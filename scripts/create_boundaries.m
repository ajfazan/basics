function create_boundaries( origin, pixels, pixel_size, filename )

  n = size( origin );
  assert( n == size( pixels ) );

  stream = fopen( filename, "w" );

  for k = 1 : n

    x = zeros( 5, 1 );
    y = zeros( 5, 1 );

    x( : ) = origin( k, 1 );
    y( : ) = origin( k, 2 );

    x( 2, 1 ) += pixel_size * pixels( k, 1 );
    x( 3, 1 ) += pixel_size * pixels( k, 1 );

    y( 3, 1 ) -= pixel_size * pixels( k, 2 );
    y( 4, 1 ) -= pixel_size * pixels( k, 2 );

    for t = 1 : 5

      fprintf( stream, "%.4f\t%.4f\n", x( t ), y( t ) );

    endfor

    fprintf( stream, "\n" );

  endfor

  fclose( stream );

endfunction
