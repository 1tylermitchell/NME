#!/usr/bin/env python

# ogr_explode.py
# Purpose: Extract node/points from linestring and polygon OGR datasources
# Usage: ogr_explode.py <input datasource> <output filename>
# Input Datasource - first layer in datasource is used
# Output Filename - results are saved in a x,y,z format
# Requires GDAL/OGR libraries: http://pypi.python.org/pypi/GDAL

# Author: Tyler Mitchell, Nathan Woodrow, Jan-2013

# CHANGELOG
# 30-JAN-2013 - Initial release, based on Nathan's example at http://gis.stackexchange.com/questions/8144/get-all-vertices-of-a-polygon-using-ogr-and-python

try:
    from osgeo import ogr
except ImportError:
    import ogr

from osgeo import ogr
from sys import argv

def startup(argv):
  input = argv[1]
  output = argv[2]
  outfile = initialise_output(output)
  zfield = check_zfield(argv)
  instatus = check_input(input)
  if instatus == True:
    ds = ogr.Open(input)
    lay = ds.GetLayer(0)
    fcnt,rcnt,pcnt=0,0,0
    return input,output,outfile,ds,lay,fcnt,rcnt,pcnt,instatus,zfield
  else:
    print "Invalid Input Datasource"
    return input,output,outfile,False,False,0,0,0,instatus,zfield

def syntax_check(argv):
  if len(argv) < 3:
    print_usage()
  return

def print_usage():
  print """
  Syntax:
     
    ogr_explode.py <input datasource> <output filename> [zfield name]
  
  Takes Z value from point features if they have one, or optionally from
  a specified field name.  Order matters :) 
  """
  return
   

def check_input(input):
  try:
    ds = ogr.Open(input)
    lay = ds.GetLayer(0)
    return True
  except (AttributeError):
    return False

def check_zfield(argv):
  if len(argv) > 2:
    zfield = argv[3]
    return zfield
  else:
    return None

def initialise_output(output):
  outfile = open(output,'w')
  outfile.write("x,y,z \n")
  return outfile

def write_output(outfile,outstr):
  outfile.write(outstr)
  return

def close_output(outfile):
  outfile.close()

def print_summary(input,output,fcnt,rcnt,pcnt,lay_geom):
  print """
  Done Processing (%s): %s
  Results Saved In: %s
  Summary: %s features, %s rings, %s points """ % (lay_geom,input,output,fcnt,rcnt,pcnt)

def check_ftype(lay):
  lay_type = lay.GetGeomType()
  if lay_type == 1:
    lay_geom = 'POINT'
  elif lay_type == 2:
    lay_geom = 'LINESTRING'
  elif lay_type == 3:
    lay_geom = 'POLYGON'
  else:
    lay_geom = None
 
  return lay_geom

def process_lines(geom,pcnt,zfield):
  points = geom.GetPointCount()
  for p in xrange(points):
    pcnt+=1
    lon, lat, z = geom.GetPoint(p)
    zval = get_zval(feat,zfield)
    if zval != None:
      z = zval
    outstr = "%s,%s,%s\n" % (lon,lat,z)
    write_output(outfile,outstr) 
  return pcnt

def process_polygons(geom,rcnt,pcnt,zfield):
  for ring in geom:
    rcnt+=1
    points = ring.GetPointCount()
    for p in xrange(points):
      pcnt+=1
      lon, lat, z = ring.GetPoint(p)
      zval = get_zval(feat,zfield)
      if zval != None:
        z = zval
      outstr = "%s,%s,%s\n" % (lon,lat,z)
      write_output(outfile,outstr)
  return rcnt,pcnt

def get_zval(feat,zfield):
  if zfield in feat.keys():
    zfield_val = feat.GetFieldAsString(zfield)
  else:
    zfield_val = None
  return zfield_val

if __name__ == '__main__':
  input,output,outfile,ds,lay,fcnt,rcnt,pcnt,instatus,zfield = startup(argv)
  if instatus == True:
    for feat in lay:
      fcnt+=1
      geom = feat.GetGeometryRef()
      lay_geom = check_ftype(lay)
      if lay_geom == 'LINESTRING' or lay_geom == 'POINT':
        pcnt = process_lines(geom,pcnt,zfield)
      elif lay_geom == 'POLYGON':
        rcnt,pcnt = process_polygons(geom,rcnt,pcnt,zfield)
      else:
        print "Unexpected Input Geometry Type"
        print "Script expects Linestring or Polygon data"

    print_summary(input,output,fcnt,rcnt,pcnt,lay_geom)
  else:
    print_usage()
    
  close_output(outfile)

