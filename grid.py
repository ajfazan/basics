#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  grid.py
#
#  Copyright 2022 ajfazan <ajfazan@DESKTOP-LS9CTJ6>
#
#  This program is free software; you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with this program;
#  if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

def main( args ):

    import math

    xmin = math.floor( float( args[1] ) )
    ymin = math.floor( float( args[4] ) )

    ymax = math.ceil( float( args[2] ) )
    xmax = math.ceil( float( args[3] ) )

    gsd = float( args[5] )

    cols = math.ceil( ( xmax - xmin ) / gsd )
    rows = math.ceil( ( ymax - ymin ) / gsd )

    xmax = xmin + gsd * cols
    ymin = ymax - gsd * rows

    print( ( xmin, int( ymin ), int( xmax ), ymax, gsd ) )

    return 0

if __name__ == '__main__':

    import sys

    sys.exit( main( sys.argv ) )
