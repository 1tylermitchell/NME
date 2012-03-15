Purpose and Usage
==================

This script, available in my SVN code repository, serves to catalog all raster & vector datasources/layers found in a directory tree.

Using a simple command line request, the script recursively scans all the files and folders for supported spatial data or image formats. The real power behind the script is the `GDAL/OGR <http://gdal.org>` spatial data access library that supports dozens of vector and raster formats.

  Usage: python gdalogr_catalogue.py <search path> 

The (default) results of a search are encoded into hierarchical XML and feed to stdout.

For more information on the purpose and background of this project, please see the discussion at my blog:

`A Case For Low-Level Metadata Collection <http://spatialguru.com/node/83>`
`XML to Describe and Catalogue Datasets <http://spatialguru.com/node/53>`

Dependencies
=================

# The main script is called **gdalogr_catalogue.py**
# GDAL/OGR libraries (Python bindings): http://pypi.python.org/pypi/GDAL
# Python > 2.3 for itertools.tee function
# **xmlgen.py** in the same folder as the main script, or installed (manually), also provided in this repo

Sample Output
==================

Here are snippits of the possible output of the script. Two options are currently available, XML & SQL -- more to come (delimited text) and some are half-baked (SQL).

XML
=====

Until I get an XML schema doc put together, you have to refer this sample XML or a portion of it as displayed here:

  <?xml version="1.0" encoding="utf-8"?>
  <DataCatalogue>
    <CatalogueProcess>
        <SearchPath>../</SearchPath>
        <LaunchPath>/code/nme/cat</LaunchPath>
        <UserHome>/Users/mine</UserHome>
        <IgnoredStrings>['.svn', '.shx', '.dbf']</IgnoredStrings>
        <DirCount>44</DirCount>
        <FileCount>119</FileCount>
        <Timestamp>Tue Feb  5 20:52:34 2008</Timestamp>
    </CatalogueProcess>
    <VectorData>
        <datasourceId>1</datasourceId>
        <name>../data_example/shp</name>
        <layercount>5</layercount>
        <format>ESRI Shapefile</format>
        <VectorLayer>
            <featurecount>1</featurecount>
            <name>buf_hull</name>
            <extent>(-5.2264717603724069, 143.19359180565968, 42.418215273515429, 287.96378357150178)</extent>
            <layerId>1</layerId>
        </VectorLayer>
     </VectorData>
    <RasterData>
        <name>../data_example/img/bg.jpg</name>
        <RasterBand>
            <bandId>1</bandId>
            <max>255.0</max>
            <overviews>0</overviews>
            <min>88.0</min>
        </RasterBand>
        <rasterX>1280</rasterX>
        <rasterY>10</rasterY>
        <driver>JPEG JFIF</driver>
        <project></project>
        <boundcount>3</boundcount>
        <rasterId>1</rasterId>
        <geotrans>(0.0, 1.0, 0.0, 0.0, 0.0, 1.0)</geotrans>
    </RasterData>
  ...

SQL
=====

It is also possible to have the script produce SQL INSERT statements by adding the word SQL as an argument after the search path, but you will then need to filter the results, e.g. grep INSERT, to get them. This is obviously a hack but is already usable if you need it.

Delimited Text
====================

The earlier versions of my vector cataloguing script (ogr_catalog.py) and Matt Perry's raster version (gdal_catalog.py) produced pipe delimited files suitable for importing into a database. This meant having at least four different files to describe what is encoded in the short XML snippit above. I hope to have delimited output support added as an option in future versions. 
