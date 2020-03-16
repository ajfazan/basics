function [ dx, dy, dz ] = compute_displacements( lat, lon, dh )

  sin_lat = sin( lat );
  cos_lat = cos( lat );

  sin_lon = sin( lon );
  cos_lon = cos( lon );

  dx = dh * cos_lat * cos_lon;
  dy = dh * cos_lat * sin_lon;
  dz = dh * sin_lat;

endfunction
