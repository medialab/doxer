<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	  
	  <!-- MANAGE HTML PARTS -->

<xsl:template match="w">
	<xsl:element name="span" xmlns="http://www.w3.org/1999/xhtml">
		<xsl:attribute name="class">
			<xsl:text>pos_</xsl:text><xsl:value-of select="interp[@type='#ttpos']"/>
			<xsl:text> lem_</xsl:text><xsl:value-of select="interp[@type='#ttlemma']"/>
		</xsl:attribute>
		<xsl:value-of select="form"/>
	</xsl:element><xsl:text> 
	</xsl:text>
</xsl:template>

<xsl:template match="/">
	<html xmlns="http://www.w3.org/1999/xhtml">
  	<head>
		<!--<title>Transcription</title>-->
		<link rel="stylesheet" href="/dexter/media/xml/mlab.css"/>
  	</head>
  	<body>
  		<xsl:for-each select="TEI/textunit">
			<div>
				<xsl:for-each select="*">
					<xsl:apply-templates select="." />
				</xsl:for-each>
  			</div>
  		</xsl:for-each>
  	</body>
	</html>
</xsl:template>

</xsl:stylesheet>
