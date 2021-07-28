<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="faq">
    <div>
      <b>
        <xsl:text>Question: </xsl:text>
        <xsl:value-of select="question" disable-output-escaping="yes"/>
      </b>
      <br/>
      <xsl:text>Answer: </xsl:text>
      <xsl:value-of select="answer" disable-output-escaping="yes"/>
    </div>
  </xsl:template>
</xsl:stylesheet>