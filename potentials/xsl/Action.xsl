<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="action">
    <div>
      <b>
        <xsl:value-of select="type"/>
        <xsl:text> </xsl:text>
      
      <xsl:text>(</xsl:text>
      <xsl:value-of select="date"/>
      <xsl:text>): </xsl:text>
      </b>

      <xsl:value-of select="comment" disable-output-escaping="yes"/>
      <xsl:text> </xsl:text>
      <xsl:if test="potential">
        <ul>
        <xsl:for-each select="potential">
          <li><a href='https://www.ctcms.nist.gov/potentials/entry/{id}'><xsl:value-of select="id"/></a></li>
        </xsl:for-each>
        </ul>
      </xsl:if>
    </div>
  </xsl:template>
</xsl:stylesheet>