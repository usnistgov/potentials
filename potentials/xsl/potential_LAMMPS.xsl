<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="potential-LAMMPS">
    <div>

      <style>
        .aslist {list-style-type: circle; list-style-position: inside; margin: 10px;}
      </style>

      <h1>LAMMPS potential implementation parameter set</h1>
      <ul>
        <li><b><xsl:text>ID: </xsl:text></b><xsl:value-of select="id"/></li>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li>
          <b><xsl:text>Potential: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="potential/URL">
            <a href="{potential/URL}"><xsl:value-of select="potential/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="potential/id"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
        <li><b>LAMMPS units: </b><xsl:value-of select="units"/></li>
        <li><b>LAMMPS atom_style: </b><xsl:value-of select="atom_style"/></li>
        <li><b>LAMMPS pair_style: </b><xsl:value-of select="pair_style/type"/></li>
        <xsl:if test="atom/element">
          <li>
            <b>Elements: </b>
            <xsl:for-each select="atom/element">
            <xsl:value-of select="."/><xsl:text> </xsl:text>
            </xsl:for-each>
          </li>
        </xsl:if>
        <xsl:if test="atom/symbol">
          <li>
            <b>Symbols: </b>
            <xsl:for-each select="atom/symbol">
            <xsl:value-of select="."/><xsl:text> </xsl:text>
            </xsl:for-each>
          </li>
        </xsl:if>
        <xsl:if test="artifact/web-link">
          <li>
            <b>File(s): </b>
            <ul class="aslist">
              <xsl:for-each select="artifact/web-link">
                <li><a href="{URL}"><xsl:value-of select="link-text"/></a></li>
              </xsl:for-each>
            </ul>
          </li>
        </xsl:if>
      </ul>
    </div>
  </xsl:template>
</xsl:stylesheet>