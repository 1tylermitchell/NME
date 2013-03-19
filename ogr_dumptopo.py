#!/usr/bin/env python

# ogr_dumptopo.py
# Purpose: Extract node/points from linestring and polygon OGR datasources
# Usage: ogr_dumptopo.py <input datasource> <output filename>
# Input Datasource - first layer in datasource is used
# Output Filename - results are saved in a x,y,fid format
# Requires GDAL/OGR libraries: http://pypi.python.org/pypi/GDAL

# Author: Tyler Mitchell, Nathan Woodrow, Jan-2013

# CHANGELOG
# 30-JAN-2013 - Initial release, based on Nathan's example at http://gis.stackexchange.com/questions/8144/get-all-vertices-of-a-polygon-using-ogr-and-python
# 18-MAR-2013 - Based on my earlier ogr_explode.py but dumps more than just point x/y/z

try:
    from osgeo import ogr
except ImportError:
    import ogr

from osgeo import ogr
from sys import argv

def startup(argv):
  syntax_check(argv)
  input = argv[1]
  output = argv[2]
  output_nodes = argv[2]
  output_edges = argv[3]
  file_nodes = initialise_output(output_nodes,'nodes')
  file_edges = initialise_output(output_edges,'edges')
  fid,edgeid = 0,0
  instatus = check_input(input)
  if instatus == True:
    ds = ogr.Open(input)
    lay = ds.GetLayer(0)
    fcnt,rcnt,pcnt=0,0,0
    return input,output,file_nodes,file_edges,ds,lay,fcnt,rcnt,pcnt,instatus,fid,edgeid
  else:
    print "Invalid Input Datasource"
    return input,output,file_nodes,file_edges,False,False,0,0,0,instatus,fid,edgeid

def syntax_check(argv):
  try:
    input = argv[1]
    output = argv[2]
  except (IndexError):
    print_usage()
  return 

def print_usage():
  print """
  Syntax:
     
    ogr_explode.py <input datasource> <output filename> 
  
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

def initialise_output(output,output_type):
  outfile = open(output,'w')
  if output_type == 'nodes':
    outfile.write("id,x,y,z,fid \n")
  elif output_type == 'edges':
    outfile.write("id,node_from,node_to,origid \n")
  return outfile

def write_output(outfile,outstr):
  outfile.write(outstr)
  return

def close_output(outfile):
  outfile.close()

def print_summary(input,output,fid,fcnt,rcnt,pcnt,lay_geom):
  print """
  Done Processing (%s): %s
  Results Saved In: %s
  Z Value Field: %s
  Summary: %s features, %s rings, %s points """ % (lay_geom,input,output,fid,fcnt,rcnt,pcnt)

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

def process_lines(geom,pcnt,fid,edgeid):
  points = geom.GetPointCount()
  for p in xrange(points):
    prev_pcnt = pcnt
    pcnt+=1
    lon, lat, z = geom.GetPoint(p)
    fid = feat.GetFID()+1
    outstr = "%s,%s,%s,%s,%s\n" % (pcnt,lon,lat,z,fid)
    write_output(file_nodes,outstr) 
    if p <= points:
      edgeid += 1
      outstr_edges = "%s,%s,%s,%s\n" % (edgeid,prev_pcnt,pcnt,fid)
      write_output(file_edges,outstr_edges) 
  return pcnt,edgeid

def process_polygons(geom,rcnt,pcnt,fid):
  for ring in geom:
    rcnt+=1
    points = ring.GetPointCount()
    for p in xrange(points):
      pcnt+=1
      lon, lat, z = ring.GetPoint(p)
      fid = feat.GetFID()+1
      outstr = "%s,%s,%s,%s,%s\n" % (pcnt,lon,lat,z,fid)
      write_output(file_nodes,outstr)
  return rcnt,pcnt

if __name__ == '__main__':
  input,output,file_nodes,file_edges,ds,lay,fcnt,rcnt,pcnt,instatus,fid,edgeid = startup(argv)
  if instatus == True:
    for feat in lay:
      fcnt+=1
      geom = feat.GetGeometryRef()
      lay_geom = check_ftype(lay)
      if lay_geom == 'LINESTRING' or lay_geom == 'POINT':
        pcnt,edgeid = process_lines(geom,pcnt,fid,edgeid)
      elif lay_geom == 'POLYGON':
        rcnt,pcnt = process_polygons(geom,rcnt,pcnt,fid)
      else:
        print "Unexpected Input Geometry Type"
        print "Script expects Linestring or Polygon data"

    print_summary(input,output,fid,fcnt,rcnt,pcnt,lay_geom)
  else:
    print_usage()
    
  close_output(file_nodes)
  close_output(file_edges)

