<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/dislocation">
  <div>
    <xsl:text>atomman parameters for a </xsl:text>
    <xsl:value-of select="system-family"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="Burgers-vector"/>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="calculation-parameter/slip_hkl"/>
    <xsl:text>) </xsl:text>
    <xsl:value-of select="character"/>
    <xsl:text> dislocation.</xsl:text>
    <ul>
      <xsl:if test = "calculation-parameter/slip_hkl">
        <li>
          <xsl:text>slip_hkl = "</xsl:text>
          <xsl:value-of select="calculation-parameter/slip_hkl"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/ξ_uvw">
        <li>
          <xsl:text>ξ_uvw = "</xsl:text>
          <xsl:value-of select="calculation-parameter/ξ_uvw"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/burgers">
        <li>
          <xsl:text>burgers = "</xsl:text>
          <xsl:value-of select="calculation-parameter/burgers"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/m">
        <li>
          <xsl:text>m = "</xsl:text>
          <xsl:value-of select="calculation-parameter/m"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/n">
        <li>
          <xsl:text>n = "</xsl:text>
          <xsl:value-of select="calculation-parameter/n"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/shift">
        <li>
          <xsl:text>shift = "</xsl:text>
          <xsl:value-of select="calculation-parameter/shift"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/shiftscale">
        <li>
          <xsl:text>shiftscale = "</xsl:text>
          <xsl:value-of select="calculation-parameter/shiftscale"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
      <xsl:if test = "calculation-parameter/shiftindex">
        <li>
          <xsl:text>shiftindex = "</xsl:text>
          <xsl:value-of select="calculation-parameter/shiftindex"/>
          <xsl:text>"</xsl:text>
        </li>
      </xsl:if>
    </ul>
  </div>
  </xsl:template>
</xsl:stylesheet>