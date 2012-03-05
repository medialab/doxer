<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

  <xsl:output media-type="text/html" encoding="UTF-8"/> 
  
  <xsl:variable name="title" select="concat('Solr search results (',response/result/@numFound,' documents)')"/>
  
  <xsl:template match='/'>
    <html>
      <head>
        <!--<title><xsl:value-of select="$title"/></title>-->
        <!--<xsl:call-template name="css"/>-->
      </head>
      <body>
        <!--<h1><xsl:value-of select="$title"/></h1>-->
        <xsl:apply-templates select="response/lst[@name='termVectors']/lst/lst[@name='textengram']/lst"/>
        <!--<xsl:apply-templates select="response/result/doc"/>-->
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="lst">
	  <ul>
	  oui: <xsl:value-of select="@name"/>
	  tf: <xsl:value-of select="./int[@name='tf']"/>
	  df: <xsl:value-of select="./int[@name='df']"/>
	  offsets: <xsl:for-each select="./lst[name='offsets']/int">
	  (s_<xsl:value-of select="@name"/>-e_<xsl:value-of select="@name"/>)
	  </xsl:for-each>
	  
	  </ul>
  </xsl:template>
  
  
  <xsl:template match="doc">
    <xsl:variable name="pos" select="position()"/>
    <div class="doc">
      <table width="100%">
        <xsl:apply-templates>
          <xsl:with-param name="pos"><xsl:value-of select="$pos"/></xsl:with-param>
        </xsl:apply-templates>
      </table>
    </div>
  </xsl:template>

  <xsl:template match="doc/*[@name='score']" priority="100">
    <xsl:param name="pos"></xsl:param>
    <tr>
      <td class="name">
        <xsl:value-of select="@name"/>
      </td>
      <td class="value">
        <xsl:value-of select="."/>

        <xsl:if test="boolean(//lst[@name='explain'])">
          <xsl:element name="a">
            <!-- can't allow whitespace here -->
            <xsl:attribute name="href">javascript:toggle("<xsl:value-of select="concat('exp-',$pos)" />");</xsl:attribute>?</xsl:element>
          <br/>
          <xsl:element name="div">
            <xsl:attribute name="class">exp</xsl:attribute>
            <xsl:attribute name="id">
              <xsl:value-of select="concat('exp-',$pos)" />
            </xsl:attribute>
            <xsl:value-of select="//lst[@name='explain']/str[position()=$pos]"/>
          </xsl:element>
        </xsl:if>
      </td>
    </tr>
  </xsl:template>

  <xsl:template match="doc/arr" priority="100">
    <tr>
      <td class="name">
        <xsl:value-of select="@name"/>
      </td>
      <td class="value">
        <ul>
        <xsl:for-each select="*">
          <li><xsl:value-of select="."/></li>
        </xsl:for-each>
        </ul>
      </td>
    </tr>
  </xsl:template>


  <xsl:template match="doc/*">
    <tr>
      <td class="name">
        <xsl:value-of select="@name"/>
      </td>
      <td class="value">
        <xsl:value-of select="."/>
      </td>
    </tr>
  </xsl:template>

  <xsl:template match="*"/>
  

</xsl:stylesheet>
