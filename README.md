Spatialguru Scripts
======================

* **ogr_dumptopo.py** - convert linestrings into nodes and edges CSV lists.  Sample output from natural earth 
   admin boundary lines included.  Nodes output has x,y,z data and an ID.  Edges has ID, node_to and node_from that
   point to node ID.

   > Usage: python ogr_dumptopo.py ne_boundary.gml nodes.csv edges.csv

* **ogr_explode.py** - blast apart those nasty polygons and linestrings into their atomic (point) pieces!  
   The script outputs a CSV file with x,y,z structure for each node in all the input features.
   Option takes 3rd dimension from a named field in the input file.

 > Usage: python ogr_explode.py input.shp output.csv [zfield name]

NME 
====

**network mapping engine - catalogue, project management and more**

At this stage the `nme/cat/gdalogr_catalogue.py` is the only other script in this repository.
It's used to recursively catalogue a tree/folder/directory and find all the GDAL/OGR
readable datasets, layers, and bands in each folder.  The results are written out
to XML.

Contact
========
For more information follow and connect with me on http://twitter.com/spatialguru or 
see more on my blog http://spatialguru.com.  I also publish books on related subjects
at http://locatepress.com (aspiring writers welcome).
