<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/citation">
  <div>

    <!-- authors (year), "title", editors (Ed.) <i>Publication</i>, (edition ed.), series, chapter <b>V(I)</b> pages, organization, publisher, address.-->

    <div class="citation">
      <b><xsl:text>Citation: </xsl:text></b>
    
      <xsl:if test = "author">   
        <!-- Authors -->
        <xsl:for-each select="author">
          <xsl:value-of select="given-name"/>
          <xsl:text> </xsl:text>
          <xsl:value-of select="surname"/>
          <!-- add commas to all but last person -->
          <xsl:if test="position() &lt; last()-1">
            <xsl:text>, </xsl:text>
          </xsl:if>
          <!-- add 'and' to last person -->
          <xsl:if test="position()=last()-1">
            <xsl:text>, and </xsl:text>
          </xsl:if>
        </xsl:for-each>
      </xsl:if>

      <xsl:if test = "publication-date/year">
        <xsl:text> (</xsl:text><xsl:value-of select="publication-date/year"/><xsl:text>)</xsl:text>
      </xsl:if>
      
      <xsl:if test = "title">
        <xsl:text>, "</xsl:text><xsl:value-of select="title" disable-output-escaping="yes"/><xsl:text>"</xsl:text>
      </xsl:if>
      
      <xsl:if test = "editor">   
        <!-- Editors -->
        <xsl:for-each select="editor">
          <xsl:value-of select="given-name"/>
          <xsl:text> </xsl:text>
          <xsl:value-of select="surname"/>
          <!-- add commas to all but last person -->
          <xsl:if test="position() &lt; last()-1">
            <xsl:text>, </xsl:text>
          </xsl:if>
          <!-- add 'and' to last person -->
          <xsl:if test="position()=last()-1">
            <xsl:text>, and </xsl:text>
          </xsl:if>
        </xsl:for-each>
        <xsl:text> (Ed.)</xsl:text>
      </xsl:if>

      <xsl:if test="publication-name">
        <xsl:text>, </xsl:text><i><xsl:value-of select="publication-name"/></i>
      </xsl:if> 
      
      <xsl:if test="edition">
        <xsl:text> (</xsl:text><xsl:value-of select="edition"/><xsl:text> ed.)</xsl:text>
      </xsl:if> 

      <xsl:if test="series">
        <xsl:text>, </xsl:text><xsl:value-of select="series"/>
      </xsl:if>
      
      <xsl:if test="volume">
        <xsl:text> </xsl:text>  
        <b>
          <xsl:value-of select="volume"/>
          <xsl:if test = "issue">
            <xsl:text>(</xsl:text><xsl:value-of select="issue"/><xsl:text>)</xsl:text>
          </xsl:if>
        </b>
      </xsl:if>
      
      <xsl:if test="pages">
        <xsl:text>, </xsl:text><xsl:value-of select="pages"/>
      </xsl:if>

      <xsl:if test="publisher-organization">
        <xsl:text>, </xsl:text><xsl:value-of select="publisher-organization"/>
      </xsl:if>

      <xsl:if test="publisher-name">
        <xsl:text>, </xsl:text><xsl:value-of select="publisher-name"/>
      </xsl:if> 

      <xsl:if test="publisher-address">
        <xsl:text>, </xsl:text><xsl:value-of select="publisher-address"/>
      </xsl:if> 

      <xsl:text>. </xsl:text>

      <!-- DOI -->
       <xsl:if test="DOI">
        <xsl:text>DOI: </xsl:text>
        <a href="https://doi.org/{DOI}" class="external"><xsl:value-of select="DOI"/></a>
        <xsl:text>.</xsl:text>
      </xsl:if> 
      
      <br/>
        
    </div>
    <xsl:if test = "abstract">
      <div class="abstract">
        <b><xsl:text>Abstract: </xsl:text></b><xsl:value-of select="abstract" disable-output-escaping="yes"/>
      </div>
    </xsl:if>
  </div>
  </xsl:template>
</xsl:stylesheet>