<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="potential-LAMMPS-KIM">
    <div>

      <style>
        .aslist {list-style-type: circle; list-style-position: inside; margin: 10px;}
      </style>

      <h1>LAMMPS potential implementation parameter set</h1>
      <ul>
        <li><b><xsl:text>ID: </xsl:text></b><xsl:value-of select="id"/></li>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <xsl:if test="potential">
          <li>
            <b><xsl:text>Potential(s): </xsl:text></b>
            <ul class="aslist">
              <xsl:for-each select="potential">
                <li>
                  <xsl:choose>
                    <xsl:when test="URL">
                    <a href="{URL}"><xsl:value-of select="id"/></a>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:value-of select="id"/>
                    </xsl:otherwise>
                  </xsl:choose>
                  <xsl:if test="atom/element">
                    <xsl:text> (</xsl:text>
                    <xsl:for-each select="atom">
                      <xsl:value-of select="element"/>
                      <xsl:if test="position() &lt; last()">
                        <xsl:text> </xsl:text>
                      </xsl:if>
                    </xsl:for-each>
                    <xsl:text>)</xsl:text>
                  </xsl:if>
                </li>
              </xsl:for-each>
            </ul>
          </li>
        </xsl:if>
        <xsl:if test="full-kim-id">
          <li>
            <b>OpenKIM Model ID(s): </b>
            <ul class="aslist">
              <xsl:for-each select="full-kim-id">
                <li>
                  <a href="https://openkim.org/id/{.}"><xsl:value-of select="."/></a>
                </li>
              </xsl:for-each>
            </ul>
          </li>
        </xsl:if>
      </ul>
    </div>
  </xsl:template>
</xsl:stylesheet>