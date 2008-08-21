<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
	<html>
	<head>
	<script type="text/javascript" src="mootools.js"></script>
	<script type="text/javascript" src="catalogue.js"></script>
	<link rel="stylesheet" href="catalogue.css" title="tnrg style" type="text/css" />
	</head>
	<body>
		<h1>Project Data Catalogue</h1>
		<xsl:for-each select="project/datasource">			
			
			<div class="datasource">
			<h2 class="toggler">Data Source: <xsl:value-of select="location"/></h2>
			<div class="element">
			Format:<xsl:value-of select="format"/><br />
			Layer Count:<xsl:value-of select="layercount"/><br />
			<xsl:for-each select="layer">
				<div class="layer">
				<h3>Layer Name: <i><xsl:value-of select="name"/></i></h3>
				
				<xsl:choose>
					<xsl:when test="geomtype='None'">
						<div class="error">
							Geomtery Type: <xsl:value-of select="geomtype"/>
						</div>
					</xsl:when>
					<xsl:otherwise>
						Geometry Type: <xsl:value-of select="geomtype"/><br />
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
					Bounding Box Coordinates: <xsl:value-of select="boundingbox"/><br />
				</div>
				<xsl:choose>
					<xsl:when test="spatial_reference='Unknown'">
						<div class="error">
						Spatial Reference: <xsl:value-of select="spatial_reference"/><br />
						</div>
					</xsl:when>
					<xsl:otherwise>
						Spatial Reference: <xsl:value-of select="spatial_reference"/><br />
					</xsl:otherwise>
				</xsl:choose>
				<div class="attributes">
					<table>
						<tr><td><b>Name</b></td> <td><b>Type</b></td> <td><b>Width</b></td></tr>
							<xsl:for-each select="attributes/attribute">
							<tr><td><i><xsl:value-of select="name"/></i></td> <td><xsl:value-of select="type"/></td> <td><xsl:value-of select="width"/></td></tr>
					</xsl:for-each>
					</table>
				</div>
					
				</div>
			</xsl:for-each>	
			</div>
			</div>
		</xsl:for-each>	
	</body>
	</html>
</xsl:template>
</xsl:stylesheet>

		