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


from osgeo import ogr
from sys import argv

path = argv[1]

if len(argv) < 3:
  print "Syntax:"
  print "ogr_explode.py <input datasource> <output filename>"
  print "Take Z value from point features if they have one, I need"
  print "to add ability to specify a field to take them from."

input = argv[1]
output = argv[2]

outfile = open(output,'w')
outfile.write("x,y,z \n")

ds = ogr.Open(input)
lay = ds.GetLayer(0)
fcnt,rcnt,pcnt=0,0,0

for feat in lay:
  fcnt+=1
  geom = feat.GetGeometryRef()
  for ring in geom:
    rcnt+=1
    points = ring.GetPointCount()
    for p in xrange(points):
      pcnt+=1
      lon, lat, z = ring.GetPoint(p)
      outstr = "%s,%s,%s\n" % (lon,lat,z)
      outfile.write(outstr)

outfile.close()

print "Done Processing: %s" % (input)
print "Results Saved In: %s" % (output)
print "Summary: %s features, %s rings, %s points" % (fcnt,rcnt,pcnt)
