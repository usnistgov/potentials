<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  <xsl:template match="parameter">
    <div>  
      <xsl:value-of select="name"/>
      <xsl:if test="value">
        <xsl:text> </xsl:text><xsl:value-of select="value"/>
      </xsl:if>
      <xsl:if test="unit">
        <xsl:text> </xsl:text><xsl:value-of select="unit"/>
      </xsl:if>
    </div>
  </xsl:template>
</xsl:stylesheet>