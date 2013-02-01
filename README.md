NME
===

``network mapping engine - catalogue, project management and more``

* ogr_explode.py - blast apart those nasty polygons and linestrings into their atomic (point) pieces!  
   The script outputs a CSV file with x,y,z structure for each node in all the input features.
   Option takes 3rd dimension from a named field in the input file.

 > Usage: python ogr_explode.py input.shp output.csv [zfield name]
