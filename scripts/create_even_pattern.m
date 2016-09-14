function create_even_pattern( l, u, delta, filename )

stream = fopen( filename, 'w' );

for y = l : delta : u
  for x = l : delta: u
    fprintf( stream, '%.3f  %.3f\n', x, y )
  endfor
endfor

fclose( stream );
