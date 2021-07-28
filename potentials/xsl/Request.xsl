<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="request">
    <div>      
      <!-- <b>system(s): </b> comments (date) -->
      <b>
        <xsl:for-each select = 'system'>
          <xsl:choose>

            <!-- Use chemical formula if given -->
            <xsl:when test="chemical-formula">
              <xsl:value-of select="chemical-formula" disable-output-escaping="yes"/>
            </xsl:when>

            <!-- Otherwise list elements -->
            <xsl:otherwise>
              <xsl:for-each select='element'>
                <xsl:value-of select='text()'/>
                <xsl:if test='position() &lt; last()'>
                  <xsl:text>-</xsl:text>
                </xsl:if>
              </xsl:for-each>
            </xsl:otherwise>
          </xsl:choose>
          
          <!-- add commas between systems -->
          <xsl:if test="position() &lt; last()-1">
            <xsl:text>, </xsl:text>
          </xsl:if>
          
          <!-- add 'and' before last of multiple systems -->
          <xsl:if test="position()=last()-1">
            <xsl:text> and </xsl:text>
          </xsl:if>
          <xsl:text> </xsl:text>  
        </xsl:for-each>
        <xsl:text> </xsl:text>
      </b>
      
      <xsl:if test="comment">
        <xsl:value-of select="comment" disable-output-escaping="yes"/>
      </xsl:if>

      <xsl:text> (</xsl:text>
      <xsl:value-of select="date"/>
      <xsl:text>)</xsl:text>
          
    </div>
  </xsl:template>
</xsl:stylesheet>