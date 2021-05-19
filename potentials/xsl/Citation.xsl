<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/citation">
  <div>

    <div class="citation">
      <b><xsl:text>Citation: </xsl:text></b>
    
      <!-- choose what to display based on document type -->
      <xsl:choose>
      
        <!-- if document type is journal show author,year,title,publication,volume,issue,doi -->
        <xsl:when test = "document-type = 'journal'">
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

            <!-- (YEAR), "Title", <i>Publication</i>, <b>V(I)</b>, -->
            <xsl:text> (</xsl:text><xsl:value-of select="publication-date/year"/><xsl:text>), </xsl:text>
            <xsl:text>"</xsl:text><xsl:value-of select="title" disable-output-escaping="yes"/><xsl:text>", </xsl:text>
            <xsl:if test="publication-name">
              <i><xsl:value-of select="publication-name"/></i><xsl:text>, </xsl:text>
            </xsl:if> 
            <xsl:if test="volume">
              <b>
                <xsl:value-of select="volume"/>
                <xsl:if test = "issue">
                  <xsl:text>(</xsl:text><xsl:value-of select="issue"/><xsl:text>)</xsl:text>
                </xsl:if>
              </b>
              <xsl:text>, </xsl:text>
            </xsl:if>
            <xsl:value-of select="pages"/><xsl:text>. </xsl:text>

            <!-- DOI -->
            <xsl:text>DOI: </xsl:text>
            <a href="https://doi.org/{DOI}" class="external"><xsl:value-of select="DOI"/></a>
            <xsl:text>.</xsl:text>
            <br/>
          </xsl:if>
        </xsl:when>
        
        <!-- if document type is journal show author,year,title -->
        <xsl:when test = "document-type = 'unspecified'">
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

            <!-- (YEAR) "Title". -->
            <xsl:text> (</xsl:text><xsl:value-of select="publication-date/year"/><xsl:text>), </xsl:text>
            <xsl:text>"</xsl:text><xsl:value-of select="title" disable-output-escaping="yes"/><xsl:text>".</xsl:text>
          </xsl:if>
        </xsl:when>

      </xsl:choose>
    </div>
    <xsl:if test = "abstract">
      <div class="abstract">
        <b><xsl:text>Abstract: </xsl:text></b><xsl:value-of select="abstract" disable-output-escaping="yes"/>
      </div>
    </xsl:if>
  </div>
  </xsl:template>
</xsl:stylesheet>