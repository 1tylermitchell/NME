#!/usr/bin/env python

# gdalogr_catalogue.py
# Purpose: Catalog all raster & vector datasources/layers found in a directory tree
# Usage: python gdalogr_catalogue.py <search path>
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


'''
try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import osr
    import ogr

import os, sys
import itertools

# Following for xml output
# xmlgen.py script required in same folder
from xmlgen import XMLWriter

def Usage():
    print 'Usage: gdalogr_catalogue.py directory [SQL]'
    print
    sys.exit(1)

# Argument processing
if len(sys.argv) > 1:
  directory = sys.argv[1]
  if len(sys.argv) > 2:
    if sys.argv[2] == "SQL":
      printSql = True
  else: printSql = False
else:
  Usage()

def startup():
  gdal.PushErrorHandler()
  skiplist = ['.svn','.shx','.dbf']
  startpath = directory
  pathwalker = os.walk(startpath)
  walkers = itertools.tee(pathwalker)
  counterraster = 0
  countervds = 0
  writer = XMLWriter()
  writer.push("DataCatalogue")
#  walkerlist = list(copy.pathwalker)
  processStats(writer, walkers[1], skiplist, startpath)
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
          xmlraster = outputraster(writer, resultsraster, counterraster, countervds, resultsFileStats)
        if vector:
 #         resultsFileStats = fileStats(currentdir)
 #         statfileStats = outputFileStats(writer, resultsFileStats)
          countervds += 1
          resultsvds,resultsFileStats = processvds(vector,countervds,currentdir)
          xmlvector = outputvector(writer, resultsvds,counterraster,countervds,resultsFileStats)
    for eachfile in allfiles:
      currentfile = "/".join([startdir, eachfile])
      #print "Current file" + currentfile
      if (not skipfile(currentfile,skiplist) and tryopends(currentfile)):
        raster, vector = tryopends(currentfile)
        if raster:
          counterraster += 1
          resultsraster,resultsFileStats = processraster(raster, counterraster, currentfile)
          xmlraster = outputraster(writer, resultsraster, counterraster, countervds, resultsFileStats)
        if vector:
          if (not skipfile(vector.GetName(),skiplist)):
 #         resultsFileStats = fileStats(currentfile)
 #         statfileStats = outputFileStats(writer, resultsFileStats)
            countervds += 1
            resultsvds,resultsFileStats = processvds(vector, countervds, currentfile)
            xmlvector = outputvector(writer, resultsvds,counterraster,countervds,resultsFileStats)
  writer.pop()

def processStats(writer, walkerlist, skiplist, startpath):
  from time import asctime
  #walkerList = list(pathwalker)
  dirlist, filelist = [], []
  for entry in walkerlist:
    dirlist += entry[1]
    filelist += entry[2]
  writer.push("CatalogueProcess")
  writer.elem("SearchPath", startpath)
  writer.elem("LaunchPath", os.getcwd())
  writer.elem("UserHome", os.getenv("HOME"))
  writer.elem("IgnoredStrings", str(skiplist))
  writer.elem("DirCount", str(len(dirlist)))
  writer.elem("FileCount", str(len(filelist)))
  writer.elem("Timestamp", asctime())
  writer.pop()
  if printSql: 
    processValues = {'SearchPath':startpath,'LaunchPath':os.getcwd(),'UserHome':os.getenv("HOME"),'IgnoredString':" ".join(map(str, skiplist)),'DirCount':int(len(dirlist)),'FileCount':int(len(filelist)),'Timestamp':asctime()}
    print sqlOutput('process',processValues)

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
  geotrans = raster.GetGeoTransform()
  driver = raster.GetDriver().LongName
  rasterx = raster.RasterXSize
  rastery = raster.RasterYSize
  wkt = raster.GetProjection()
  resultsbands = {}
  resultsFileStats = fileStats(currentpath)
  for bandnum in range(bandcount):
    band = raster.GetRasterBand(bandnum+1)
    min, max = band.ComputeRasterMinMax()
    overviews = band.GetOverviewCount()
    resultseachband = {'bandId': str(bandnum+1), 'min': str(min),'max': str(max), 'overviews': str(overviews)}
    resultseachbandShort = {'bandId': bandnum+1, 'min': min,'max': max, 'overviews': str(overviews)}
    resultsbands[str(bandnum+1)] = resultseachband
    if printSql: print sqlOutput('band',resultseachbandShort)
  resultsraster = { 'bands': resultsbands, 'rasterId': str(counterraster), 'name': rastername, 'bandcount': str(bandcount), 'geotrans': str(geotrans), 'driver': str(driver), 'rasterX': str(rasterx), 'rasterY': str(rastery), 'project': wkt}
  resultsrasterShort =  {'rasterId':counterraster, 'name': rastername, 'bandcount': bandcount, 'geotrans': str(geotrans), 'driver': driver, 'rasterX': rasterx, 'rasterY': rastery, 'project': wkt}
  if printSql: print sqlOutput('raster',resultsrasterShort)
  #Mapping(raster,layerextentraw,layername,layerftype) # mapping test
  return resultsraster, resultsFileStats
  
def outputraster(writer, resultsraster, counterraster, countervds, resultsFileStats):
  writer.push(u"RasterData")
  statfileStats = outputFileStats(writer, resultsFileStats)
  for rasteritem, rastervalue in resultsraster.iteritems(): # for each raster attribute
    if rasteritem <> 'bands':
      writer.elem(unicode(rasteritem), unicode(rastervalue))
    if rasteritem == 'bands':
      for banditem, bandvalue in rastervalue.iteritems(): # for each band
        writer.push(u"RasterBand")
        for banditemdetails, bandvaluedetails in bandvalue.iteritems():
          writer.elem(unicode(banditemdetails), unicode(bandvaluedetails))
        writer.pop()
  writer.pop()
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
    layerfcount = str(layer.GetFeatureCount())
    layerextentraw = layer.GetExtent()
    layerftype = featureTypeName(layer.GetLayerDefn().GetGeomType())

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
    if printSql: print sqlOutput('layer',resultseachlayer)
    #if (layerftype <> 'UNKNOWN'):
    #    Mapping(vector,layerextentraw,layername,layerftype) # mapping test
  resultsvds = { 'datasourceId': str(countervds), 'name': vdsname, 'format': vdsformat, 'layercount': str(vdslayercount) }
  sqlstringvds = "INSERT INTO datasource %s VALUES %s;" % (('datasourceId','name','format','layercount'), (countervds, vdsname, vdsformat, int(vdslayercount)))
  resultsvector = { 'resultsvds': resultsvds, 'resultslayers': resultslayers } 
  if printSql: print sqlOutput('dataset',resultsvds)

  return resultsvector,resultsFileStats

def featureTypeName(inttype):
    # Converts integer feature type to name (e.g. 1 = Point)
    ftype = ''
    if (inttype == ogr.wkbPoint): ftype = 'POINT'
    elif (inttype == ogr.wkbLineString): ftype = 'LINE'
    elif (inttype == ogr.wkbPolygon): ftype = 'POLYGON'
    elif (inttype == 0): ftype = 'UNKNOWN'
    else: print "-----Ftype conversion failure"
    return ftype

def outputvector(writer, resultsvector, counterraster, countervds, resultsFileStats):
  writer.push(u"VectorData")
  statfileStats = outputFileStats(writer, resultsFileStats)
  for vectoritem, vectorvalue in resultsvector.iteritems(): # resultsvector includes two dictionaries
    if vectoritem <> 'resultslayers':
      for vectordsitem, vectordsvalue in vectorvalue.iteritems(): # vectorvalue contains datasource attributes
        writer.elem(unicode(vectordsitem), unicode(vectordsvalue))
    if vectoritem == 'resultslayers':
      for layeritem, layervalue in vectorvalue.iteritems(): # vectorvalue contains a dictionary of the layers
        writer.push(u"VectorLayer")
        for layeritemdetails, layervaluedetails in layervalue.iteritems(): # layervalue contains layer attributes
          writer.elem(unicode(layeritemdetails), unicode(layervaluedetails))
        writer.pop()
  writer.pop()
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

def fileStats(filepath):
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
  md5_key = (full_path, user_name, file_size, time_modified, time_created)
  md5_digest = getMd5HexDigest(md5_key)
  resultsFileStats = {'fullPath': str(full_path), 'userId': str(user_id), 'groupId': str(group_id), 'fileSize': str(file_size), 'timeAccessed': str(time_accessed), 'timeModified': str(time_modified), 'timeCreated': str(time_created), 'fileType': file_type, 'userName': user_name, 'userFullName': user_full_name, 'uniqueDigest': md5_digest}
  return resultsFileStats

def outputFileStats(writer, resultsFileStats):
  writer.push(u"FileStats")
  for statitem, statvalue in resultsFileStats.iteritems():
    writer.elem(unicode(statitem), unicode(statvalue))
  writer.pop()
  return True

def getMd5HexDigest(encodeString):
  import md5
  m = md5.new()
  m.update(str(encodeString))
  return m.hexdigest()

class Mapping:
    def __init__(self,datasource,extent,layername,layerftype):
        from mapscript import *
        from time import time
        map = mapObj()
        map.setSize(400,400)
        #ext = rectObj(-180,-90,180,90)
        ext = rectObj(extent[0],extent[2],extent[1],extent[3]) # some trouble with some bad extents in my test data
        map.extent = ext
        map.units = MS_DD # should be programmatically set
        lay = layerObj(map)
        lay.name = "Autolayer"
        lay.units = MS_DD
        lay.data = datasource.GetName()
        print lay.data
        lay.status = MS_DEFAULT
        cls = classObj(lay)
        sty = styleObj()
        col = colorObj(0,0,0)
        symPoint = symbolObj
        map.setSymbolSet("symbols/symbols.sym")
        if (layerftype == 'POINT'): 
            lay.type = MS_LAYER_POINT
            sty.setSymbolByName = "achteck"
            sty.width = 100
            sty.color = col
        elif (layerftype == 'LINE'): 
            lay.type = MS_LAYER_LINE
            sty.setSymbolByName = "punkt"
            sty.width = 5
            sty.color = col
        elif (layerftype == 'POLYGON'): 
            lay.type = MS_LAYER_POLYGON
            sty.setSymbolByName = "circle"
            sty.width = 10
            sty.outlinecolor = col
        elif (layerftype == 'RASTER'): 
            lay.type = MS_LAYER_RASTER
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
  startup()
  print "</xml>"

