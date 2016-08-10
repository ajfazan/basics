function create_geo_grid( northern_lat,
                          southern_lat,
                          eastern_lon,
                          western_lon, delta_lat, delta_lon, filename )

  assert( northern_lat > southern_lat );
  assert( western_lon  < eastern_lon  );

  stream = fopen( filename, 'w' );

  lat = southern_lat : delta_lat : northern_lat;
  lon = western_lon  : delta_lon : eastern_lon;

  for i = 1 : columns( lat )
    l = lat( i );
    for j = 1 : columns( lon )
      fprintf( stream, '%.12f %.12f\n', l, lon( j ) );
    endfor
  endfor

  fclose( stream );
  
  info = sprintf( '%s.info', filename );
  
  stream = fopen( info, 'w' );

  fprintf( stream, '*** GRID INFO ***\n' );
  fprintf( stream, '\tFilename=%s\n', filename );
  fprintf( stream, '\tUL: (%.12f, %.12f)\n', northern_lat, western_lon );
  fprintf( stream, '\tLR: (%.12f, %.12f)\n', southern_lat, eastern_lon );
  fprintf( stream, '\tCell Size: (%.12f, %.12f)\n', delta_lon, -delta_lat );
  fprintf( stream, '\trows: %d\n', columns( lat ) );
  fprintf( stream, '\tcolumns: %d\n', columns( lon ) );

  fclose( stream );

endfunction
