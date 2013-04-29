#!/usr/bin/env python

# gdalogr_catalogue.py
# Purpose: Catalog all raster & vector datasources/layers found in a directory tree
# Usage: python gdalogr_catalogue.py [options] <search path>
# Sends hierarchical XML to stdout
# Requires GDAL/OGR libraries: http://pypi.python.org/pypi/GDAL
# Requires Python > 2.3 for itertools.tee function.

# Author: Tyler Mitchell, Matthew Perry Jan-2008

# CHANGELOG
# JAN-06 - Initial release of ogr_catalog5.py
# 27-DEC-07 - fixed try statement so it fails more gracefully
# 5-JAN-08 - converted to using XML output, pipe to a text file
# 7-JAN-08 - started refactoring, raster output complete
# 8-JAN-08 - added rudimentary vector output
# 16-JAN-08 - renamed outputs entities, added higher level elements/summary stats
# 12-FEB-08 - Added bad hack to output INSERT statements if you add 2nd argument in command "SQL".  e.g. python gdalogr_catalogue.py ../ SQL | grep INSERT - hacked for Markus :)

'''
TODO
# DONE - higher level attributes about process: num of files, dirs search, timestamp
# DONE - filesize, user/owner, moddate/timestamp for entries
- extent values to GML or basic WKT bbox
# DONE - decide on checksum process for determining changes
- decide on process -> datasource linking (timestamp?) for top level relations
- output an overview map showing extents (e.g. mapscript?)

'''
try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import osr
    import ogr

import os, sys, platform
import itertools
import getopt
from string import strip

# Following for xml output
# xmlgen.py script required in same folder
from xmlgen import XMLWriter

# Following for class Mapping()
#from mapscript import *
#from time import time

def startup():
  #directory = sys.argv[1]
  gdal.PushErrorHandler()
  skiplist = ['.svn','.shx','.dbf']
  startpath = options.directory
  pathwalker = os.walk(startpath)
  walkers = itertools.tee(pathwalker)
  counterraster = 0
  countervds = 0

#  walkerlist = list(copy.pathwalker)
  processStats(walkers[1], skiplist, startpath,xmlroot)
  for eachpath in walkers[0]:
    startdir = eachpath[0]
    alldirs = eachpath[1]
    allfiles = eachpath[2]
    for eachdir in alldirs:
      currentdir = os.path.join(startdir,eachdir)
      #print currentdir
      raster,vector = tryopends(currentdir)
      if (not skipfile(currentdir,skiplist) and tryopends(currentdir)):
        raster,vector = tryopends(currentdir)
        if raster:
          counterraster += 1
          print counterraster
          resultsraster,resultsFileStats = processraster(raster,counterraster,currentdir)
          xmlraster = outputraster(resultsraster, counterraster, countervds, resultsFileStats, xmlroot)
        if vector:
 #         resultsFileStats = fileStats(currentdir)
 #         statfileStats = outputFileStats(writer, resultsFileStats)
          countervds += 1
          resultsvds,resultsFileStats = processvds(vector,countervds,currentdir)
          xmlvector = outputvector(resultsvds,counterraster,countervds,resultsFileStats, xmlroot)
    for eachfile in allfiles:
       currentfile = os.path.join(startdir,eachfile)
      #print "Current file" + currentfile
       if (not skipfile(currentfile,skiplist) and tryopends(currentfile)):
        raster, vector = tryopends(currentfile)
        if raster:
          counterraster += 1
          resultsraster,resultsFileStats = processraster(raster, counterraster, currentfile)
          xmlraster = outputraster(resultsraster, counterraster, countervds, resultsFileStats,xmlroot)
        if vector:
          if (not skipfile(vector.GetName(),skiplist)):
 #         resultsFileStats = fileStats(currentfile)
 #         statfileStats = outputFileStats(writer, resultsFileStats)
            countervds += 1
            resultsvds,resultsFileStats = processvds(vector, countervds, currentfile)
            xmlvector = outputvector(resultsvds,counterraster,countervds,resultsFileStats,xmlroot)

def processStats(walkerlist, skiplist, startpath, xmlroot):
  from time import asctime
  #walkerList = list(pathwalker)
  dirlist, filelist = [], []
  for entry in walkerlist:
    dirlist += entry[1]
    filelist += entry[2]
 
  xmlcatalog = appendXML(xmlroot, "CatalogueProcess")
  appendXML(xmlcatalog, "SearchPath", startpath)
  appendXML(xmlcatalog, "LaunchPath", os.getcwd())
  appendXML(xmlcatalog, "UserHome", os.getenv("HOME"))
  appendXML(xmlcatalog, "IgnoredStrings", str(skiplist))
  appendXML(xmlcatalog, "DirCount", str(len(dirlist)))
  appendXML(xmlcatalog, "FileCount", str(len(filelist)))
  appendXML(xmlcatalog, "Timestamp", asctime())
  appendXML(xmlcatalog, "OperatingSystem", platform.system())
  
  if options.printSql: 
    processValues = {'SearchPath':startpath,'LaunchPath':os.getcwd(),'UserHome':os.getenv("HOME"),'IgnoredString':" ".join(map(str, skiplist)),'DirCount':int(len(dirlist)),'FileCount':int(len(filelist)),'Timestamp':asctime()}
    print sqlOutput('process',processValues)

def startXML():
  xmlroot = ET.Element("DataCatalogue")
  return xmlroot

def appendXML(elementroot, subelement, subelstring=None):
  newelement = ET.SubElement(elementroot, subelement)
  newelement.text = subelstring
  return newelement

def writeXML(xmlroot):
  xmltree = ET.ElementTree(xmlroot)
  if options.logfile:
    xmltree.write(options.logfile)
  else: 
    print prettify(xmlroot)

def skipfile(filepath, skiplist):
  skipstatus = None
  for skipitem in skiplist:
    if filepath.find(skipitem) > 0: 
      skipstatus = True
      return True
    else:
      skipstatus = False
  return skipstatus
  
def tryopends(filepath):
  dsogr, dsgdal = False, False
  try:
    #print "trying" + filepath
    dsgdal = gdal.OpenShared(filepath)
  except gdal.GDALError:
    dsgdal = False #return False
  try:
    dsogr = ogr.OpenShared(filepath)
  except ogr.OGRError:
    dsogr = False #return False
  return dsgdal, dsogr

def processraster(raster, counterraster, currentpath):
  rastername = raster.GetDescription()
  bandcount = raster.RasterCount
  geotrans = strip(str(raster.GetGeoTransform()),"()")
  driver = raster.GetDriver().LongName
  rasterx = raster.RasterXSize
  rastery = raster.RasterYSize
  wkt = raster.GetProjection()
  #extent = (geotrans[0]), (geotrans[3]), (geotrans[0] + ( geotrans[1] * rasterx )), (geotrans[3] + ( geotrans[5] * rastery ))
  resultsbands = {}
  resultsFileStats = fileStats(currentpath)
  for bandnum in range(bandcount):
    band = raster.GetRasterBand(bandnum+1)
    min, max = band.ComputeRasterMinMax()
    overviews = band.GetOverviewCount()
    resultseachband = {'bandId': str(bandnum+1), 'min': str(min),'max': str(max), 'overviews': str(overviews)}
    resultseachbandShort = {'bandId': bandnum+1, 'min': min,'max': max, 'overviews': str(overviews)}
    resultsbands[str(bandnum+1)] = resultseachband
    if options.printSql: print sqlOutput('band',resultseachbandShort)
  resultsraster = { 'bands': resultsbands, 'rasterId': str(counterraster), 'name': rastername, 'bandcount': str(bandcount), 'geotrans': str(geotrans), 'driver': str(driver), 'rasterX': str(rasterx), 'rasterY': str(rastery), 'projection': wkt}
  resultsrasterShort =  {'rasterId':counterraster, 'name': rastername, 'bandcount': bandcount, 'geotrans': str(geotrans), 'driver': driver, 'rasterX': rasterx, 'rasterY': rastery, 'projection': wkt}
  if options.printSql: print sqlOutput('raster',resultsrasterShort)
  #Mapping(raster,extent,rastername,'RASTER') # mapping test
  return resultsraster, resultsFileStats
  
def outputraster(resultsraster, counterraster, countervds, resultsFileStats, xmlroot):
  xmlraster = appendXML(xmlroot, "RasterData")

  statfileStats = outputFileStats(resultsFileStats, xmlraster)
  for rasteritem, rastervalue in resultsraster.iteritems(): # for each raster attribute
    if rasteritem <> 'bands':
      appendXML(xmlraster, rasteritem, rastervalue)
    if rasteritem == 'bands':
      for banditem, bandvalue in rastervalue.iteritems(): # for each band
	xmlband = appendXML(xmlraster, "RasterBand")
        for banditemdetails, bandvaluedetails in bandvalue.iteritems():
	  appendXML(xmlband, banditemdetails, bandvaluedetails)
  return True

def processvds(vector, countervds,currentpath):
  vdsname = vector.GetName()
  vdsformat = vector.GetDriver().GetName()
  vdslayercount = vector.GetLayerCount()
  resultslayers = {}
  resultsFileStats = fileStats(currentpath)
  for layernum in range(vdslayercount): #process all layers
    layer = vector.GetLayer(layernum)
    layername = layer.GetName()
    spatialref = layer.GetSpatialRef()
    layerfcount = str(layer.GetFeatureCount())
    layerextentraw = strip(str(layer.GetExtent()),"()")
    layerftype = featureTypeName(layer.GetLayerDefn().GetGeomType())
    if layerftype == 'NONE':
      layerextentraw = 0

    # the following throws all the attributes into dictionaries of attributes, 
    # some of which are other dictionaries
    # resultseachlayer = 1 layer attributes
    # resultslayers = dict. of all layers and their attributes
    # resultsvds = datasource attributes
    # resultsvector = dict of datasource attributes, plus a dict of all layers
    # Note all get saved as strings, which isn't what you'd want for SQL output
    resultseachlayer = {'layerId': str(layernum+1), 'name': layername, 'featuretype': str(layerftype), 'featurecount': str(layerfcount), 'extent': layerextentraw}
    resultslayers[str(layernum+1)] = resultseachlayer
    sqlstringvlay = "INSERT INTO layer %s VALUES %s;" % (('layerId','datasourceId','name','featurecount','extent'), (layernum+1,countervds,layername,int(layerfcount),layerextentraw))
    if options.printSql: print sqlOutput('layer',resultseachlayer)
    #if (layerftype <> 'UNKNOWN'):
    #    Mapping(vector,layerextentraw,layername,layerftype) # mapping test
  resultsvds = { 'datasourceId': str(countervds), 'name': vdsname, 'format': vdsformat, 'layercount': str(vdslayercount), 'projection': str(spatialref)}
  sqlstringvds = "INSERT INTO datasource %s VALUES %s;" % (('datasourceId','name','format','layercount'), (countervds, vdsname, vdsformat, int(vdslayercount)))
  resultsvector = { 'resultsvds': resultsvds, 'resultslayers': resultslayers } 
  if options.printSql: print sqlOutput('dataset',resultsvds)

  return resultsvector,resultsFileStats

def featureTypeName(inttype):
    # Converts integer feature type to name (e.g. 1 = Point)
    ftype = ''
    if (inttype == ogr.wkbPoint): ftype = 'POINT'
    elif (inttype == ogr.wkbLineString): ftype = 'LINE'
    elif (inttype == ogr.wkbPolygon): ftype = 'POLYGON'
    elif (inttype == 0): ftype = 'UNKNOWN'
    elif (inttype == 100): ftype = 'NONE'
    elif (inttype == -2147483645): ftype = '3D POLYGON'
    elif (inttype == -2147483646): ftype = '3D LINESTRING'
    elif (inttype == -2147483647): ftype = '3D POINT'
    else: print "-----Ftype conversion failure"
    #print str(int(inttype)) + "---" + ftype
    return ftype

def outputvector(resultsvector, counterraster, countervds, resultsFileStats,xmlroot):
  xmlvector = appendXML(xmlroot, "VectorData")
  statfileStats = outputFileStats(resultsFileStats, xmlvector)
  for vectoritem, vectorvalue in resultsvector.iteritems(): # resultsvector includes two dictionaries
    if vectoritem <> 'resultslayers':
      for vectordsitem, vectordsvalue in vectorvalue.iteritems(): # vectorvalue contains datasource attributes
	appendXML(xmlvector, vectordsitem, vectordsvalue)

    if vectoritem == 'resultslayers':
      for layeritem, layervalue in vectorvalue.iteritems(): # vectorvalue contains a dictionary of the layers
        xmlvectorlayer = appendXML(xmlvector, "VectorLayer")

        for layeritemdetails, layervaluedetails in layervalue.iteritems(): # layervalue contains layer attributes
	  appendXML(xmlvectorlayer, layeritemdetails, layervaluedetails)
  return True

def sqlOutput(tableName, valueDict):
     sqlStatement = "INSERT INTO %s %s VALUES %s;" % (tableName, tuple((valueDict.keys())),tuple(valueDict.values()))
     print sqlStatement

def sqlCreateTables():
    processColumns = "SearchPath VARCHAR, LaunchPath VARCHAR, UserHome  VARCHAR, IgnoredString VARCHAR, DirCount  INTEGER, FileCount INTEGER, Timestamp VARCHAR"
    tables = ('process',) #,'dataset','layer','raster','band')

    for table in tables:
        sqlStatement = "CREATE TABLE %s (%s);" % (table, processColumns)
        print sqlStatement

### TODO functions below...

def xmlDtdOutput():
  import zipfiles
  # output dtd that corresponds to the xml, or is it schema?

def checkZip(currentfile):
  import zipfiles
  # check if it can read zips

def openZip(currentfile):
  import zipfiles
  # extract files and catalogue them

def convertSize(size):
  import math
  # convert file sizes to human-readable values with appropriate units
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size,1024)))
  p = math.pow(1024,i)
  s = round(size/p,2)
  if (s > 0):
      return '%s %s' % (s,size_name[i])
  else:
      return '0B'

def fileStats(filepath):
  from time  import gmtime, strftime
  mode, ino, dev, nlink, user_id, group_id, file_size, time_accessed, time_modified, time_created = os.stat(filepath)
  if os.path.isfile(filepath):
    file_type = "File"
  else: 
    file_type = "Directory"
  try:
    import pwd # not available on all platforms
    userinfo = pwd.getpwuid(user_id)
  except (ImportError, KeyError):
    user_name = "N/A"
    user_full_name = "N/A"
  else:
    user_name = userinfo[0]
    user_full_name = userinfo[4]
  full_path = os.path.abspath(filepath)
  #full_path.replace('//','/')
  #if platform.system() == 'Windows':
  #  full_path.replace('/','\\')
  md5_key = (full_path, user_name, file_size, time_modified, time_created)
#  md5_digest = getMd5HexDigest(md5_key)
  md5_digest = getMd5hash(md5_key)

  resultsFileStats = {'fullPath': str(full_path), 'userId': str(user_id), 'groupId': str(group_id), 'fileSize': convertSize(file_size), 'timeAccessed': strftime('%a %d %b %Y %H:%M %Z',gmtime(time_accessed)), 'timeModified': strftime('%a %d %b %Y %H:%M %Z',gmtime(time_modified)), 'timeCreated': strftime('%a %d %b %Y %H:%M %Z',gmtime(time_created)), 'fileType': file_type, 'userName': user_name, 'userFullName': user_full_name, 'uniqueDigest': md5_digest}
  return resultsFileStats

def outputFileStats(resultsFileStats, xmlroot):
  xmlfilestats = appendXML(xmlroot, "FileStats")
  for statitem, statvalue in resultsFileStats.iteritems():
    appendXML(xmlfilestats, statitem, statvalue)
  return True

def outputXml(root,newelement):
  SubElement(root,newelement)
  return 
  
def getMd5HexDigest(encodeString):
  import md5
  m = md5.new()
  m.update(str(encodeString))
  return m.hexdigest()

def getMd5hash(encodeString):
  import hashlib
  m = hashlib.md5()
  m.update(str(encodeString))
  return m.hexdigest()

class Mapping:
    def __init__(self,datasource,extent,layername,layerftype):
        #from mapscript import *
	import mapscript
        from time import time
        tmap = mapscript.mapObj()
	print "checkpoint 1"
        map.setSize(400,400)
        #ext = rectObj(-180,-90,180,90)
        ext = mapscript.rectObj(extent[0],extent[2],extent[1],extent[3]) # some trouble with some bad extents in my test data
        map.extent = ext
        map.units = mapscript.MS_DD # should be programmatically set
        lay = mapscript.layerObj(map)
        lay.name = "Autolayer"
        lay.units = mapscript.MS_DD
        if (layerftype == 'RASTER'):
		lay.data = datasource.GetDescription()
	else:
		lay.data = datasource.GetName()
        print lay.data
        lay.status = mapscript.MS_DEFAULT
        cls = mapscript.classObj(lay)
        sty = mapscript.styleObj()
        col = mapscript.colorObj(0,0,0)
#        symPoint = mapscript.symbolObj
        map.setSymbolSet("symbols/symbols_basic.sym")
        if (layerftype == 'POINT'): 
            lay.type = mapscript.MS_LAYER_POINT
            sty.setSymbolByName = "achteck"
            sty.width = 100
            sty.color = col
        elif (layerftype == 'LINE'): 
            lay.type = mapscript.MS_LAYER_LINE
            sty.setSymbolByName = "punkt"
            sty.width = 5
            sty.color = col
        elif (layerftype == 'POLYGON'): 
            lay.type = mapscript.MS_LAYER_POLYGON
            sty.setSymbolByName = "circle"
            sty.width = 10
            sty.outlinecolor = col
        elif (layerftype == 'RASTER'): 
            lay.type = mapscript.MS_LAYER_RASTER
            sty.setSymbolByName = "squares"
            sty.size = 10
            sty.color = col
        #sty.setSymbolByName(map,symname)
        #sty.size = symsize
        cls.insertStyle(sty)
        try:
            img = map.draw()
            img.save(str(time()) + "auto.gif")
            map.save(str(time()) + "auto.map")
        except MapServerError:
            return None
        # add layer
        # assign datasource to layer
        # add basic styling
        # apply styling to layer
        # open output image
        # write, close, cleanup


if __name__ == '__main__':
  from optparse import OptionParser, OptionGroup
  parser = OptionParser()
  parser.set_usage("Usage: %prog [options] directory")
  parser.add_option("-d","--dir", action="store", type="string", dest="directory", help="Top level folder to start scanning from")
  parser.add_option("-f","--file", action="store", type="string", dest="logfile", help="Output log file (not written to stdout)" )
  group = OptionGroup(parser, "Hack Options", "May not function without advanced knowledge")
  group.add_option("-s","--sql", action="store_true", dest="printSql", help="Output results in SQL INSERT statements instead of XML")
  group.add_option("-p","--pretty", action="store_true", dest="pretty", help="Print easy to read XML to stdout")
  parser.add_option_group(group)
  (options, args) = parser.parse_args()

  # Argument processing
  if len(sys.argv) == 2:
    options.directory = sys.argv[1]
  if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

  from xml.etree.ElementTree import Element, SubElement
  import xml.etree.ElementTree as ET

  from ElementTree_pretty import prettify
  xmlroot = startXML()
  startup()
  writeXML(xmlroot)
  if options.pretty: print prettify(xmlroot)

