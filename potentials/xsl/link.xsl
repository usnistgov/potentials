<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  <xsl:template match="link">
    <div>
      <xsl:if test="web-link/label">
        <xsl:value-of select="web-link/label" disable-output-escaping="yes"/><xsl:text> </xsl:text>
      </xsl:if>
      <a href = "{web-link/URL}">
        <xsl:value-of select="web-link/link-text"/>
      </a>
    </div>
  </xsl:template>
</xsl:stylesheet>