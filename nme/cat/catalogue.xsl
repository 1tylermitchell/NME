<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
	<html>
	<head>
	<script type="text/javascript" src="js/mootools.js"></script>
	<script type="text/javascript" src="js/catalogue.js"></script>
	<link rel="stylesheet" href="css/catalogue.css" title="tnrg style" type="text/css" />
	</head>
	<body>
		<h1>Project Data Catalogue</h1>
        <h2>Catalogue Details</h2>

            <xsl:for-each select="DataCatalogue/CatalogueProcess">

            <div class="datasource">
            <h3 class="toggler">Search Path: <xsl:value-of select="SearchPath"/></h3>
            <div class="element">
            Launch Path: <xsl:value-of select="LaunchPath"/><br />
            User Home: <xsl:value-of select="UserHome"/><br />
            Ignored Strings: <xsl:value-of select="IgnoredStrings"/><br />
            Dir Count: <xsl:value-of select="DirCount"/><br />
            File Count: <xsl:value-of select="FileCount"/><br />
            Timestamp: <xsl:value-of select="Timestamp"/><br />
            Operating System: <xsl:value-of select="OperatingSystem"/><br />
            </div>
            </div>
        </xsl:for-each>

        <h2>Raster Data</h2>
            <xsl:for-each select="DataCatalogue/RasterData">
			
			<div class="datasource">
			<h2 class="toggler">Data Source: <xsl:value-of select="FileStats/fullPath"/></h2>
			
             <div class="element">
			 Format: <xsl:value-of select="driver"/><br />
			 Band Count: <xsl:value-of select="bandcount"/><br />
             		 Dimensions (X Y): <xsl:value-of select="rasterX"/> x <xsl:value-of select="rasterY"/><br />
        		 Projection: <xsl:value-of select="projection"/><br />

			  <xsl:for-each select="RasterBand">
				<div class="layer">
				<h3>Layer Name: <i><xsl:value-of select="bandId"/></i></h3>
                Min:<xsl:value-of select="min"/><br />
                Max:<xsl:value-of select="max"/><br />
                 <xsl:choose>
                    <xsl:when test="overviews='0'">
                        <div class="error">
                            Overviews: None<br />
                        </div>
                    </xsl:when>
                    <xsl:otherwise>
                        Overviews: Yes<br />
                    </xsl:otherwise>
                 </xsl:choose>
			    </div>
			  </xsl:for-each>	

			 </div>
			</div>
		    </xsl:for-each>	
		
            <h2>Vector Data</h2>

            <xsl:for-each select="DataCatalogue/VectorData">
			
			<div class="datasource">
			<h2 class="toggler">Data Source: <xsl:value-of select="datasourceId"/> - <xsl:value-of select="name"/></h2>
			 <div class="element">
			 Format: <xsl:value-of select="format"/><br />
			 Layer Count: <xsl:value-of select="layercount"/><br />
			 <xsl:for-each select="VectorLayer">
				<div class="layer">
				 <h3>Layer <xsl:value-of select="layerId"/> - <i><xsl:value-of select="name"/></i></h3>
				
				 <xsl:choose>
					<xsl:when test="featuretype='NONE'">
						<div class="error">
							Geometry Type: <xsl:value-of select="featuretype"/>
						</div>
					</xsl:when>
					<xsl:otherwise>
						Geometry Type: <xsl:value-of select="featuretype"/><br />
					</xsl:otherwise>
				 </xsl:choose>
				
				 <xsl:choose>
					<xsl:when test="featurecount&lt;2">
						<div class="error">
							Features: <xsl:value-of select="featurecount"/>
						</div>
					</xsl:when>
					<xsl:otherwise>
						Features: <xsl:value-of select="featurecount"/><br />
					</xsl:otherwise>
				 </xsl:choose>
				 <div class="bbox">
					Bounding Box Coordinates: <xsl:value-of select="extent"/><br />
				 </div>
				 <xsl:choose>
					<xsl:when test="projection='Unknown'">
						<div class="error">
						Spatial Reference: <xsl:value-of select="projection"/><br />
						</div>
					</xsl:when>
					<xsl:otherwise>
						Spatial Reference: <xsl:value-of select="projection"/><br />
					</xsl:otherwise>
				 </xsl:choose>
					
				</div>
			</xsl:for-each>	
			</div>
			</div>
		</xsl:for-each>	
	</body>
	</html>
</xsl:template>
</xsl:stylesheet>

