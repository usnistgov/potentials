<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="*" name="citation">
    
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
  </xsl:template>
  
  <xsl:template match="/interatomic-potential">
    <xsl:variable name="entryid" select="id" />
    <div>

      <!-- Show old implementation files buttons -->
      <script src="https://www.ctcms.nist.gov/potentials/site/showFiles.js">//</script>

      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title"><xsl:value-of select="$entryid"/></h3>
        </div>
        <div class="panel-body">
          <!-- Add citations and abstracts -->
          <xsl:for-each select="description/citation">
            <div class="citation">
              <b><xsl:text>Citation: </xsl:text></b><xsl:call-template name="citation" disable-output-escaping="yes"/>
            </div>
            <xsl:if test = "abstract">
              <div class="abstract">
                <b><xsl:text>Abstract: </xsl:text></b><xsl:value-of select="abstract" disable-output-escaping="yes"/>
              </div>
            </xsl:if>
          </xsl:for-each>

          <!-- Add description notes -->
          <xsl:if test = "description/notes/text">
            <br/>
            <div class="description-notes">
              <b><xsl:text>Notes: </xsl:text></b><xsl:value-of select="description/notes/text" disable-output-escaping="yes"/>
            </div>
          </xsl:if>
          <br/>
          
          <!-- Add implementations -->
          <xsl:for-each select="implementation">
            
            <!-- Show content type (and id)-->
            <div class="format">
              <b><xsl:value-of select="type"/></b>
              <xsl:if test="id">
                <a>
                  <xsl:attribute name="href">
                    <xsl:text>https://www.ctcms.nist.gov/potentials/entry/</xsl:text><xsl:value-of select="$entryid"/><xsl:text>/</xsl:text><xsl:value-of select="id"/><xsl:text>.html</xsl:text>
                  </xsl:attribute>
                  <xsl:text> (</xsl:text><xsl:value-of select="id"></xsl:value-of><xsl:text>)</xsl:text>
                </a>
              </xsl:if>
            </div>
            
            <!-- Show implementation notes -->
            <div class="implementation-notes">
              <xsl:if test="id">
                <a>
                  <xsl:attribute name="href">
                    <xsl:text>https://www.ctcms.nist.gov/potentials/entry/</xsl:text><xsl:value-of select="$entryid"/><xsl:text>/</xsl:text><xsl:value-of select="id"/><xsl:text>.html</xsl:text>
                  </xsl:attribute>
                  <b><xsl:text>See Computed Properties</xsl:text></b>
                </a>
                <br/>
              </xsl:if>
              <b><xsl:text>Notes: </xsl:text></b>
              <xsl:value-of select = "notes/text" disable-output-escaping="yes"/>
              <br/>
                
              <!-- List artifact files -->
              <xsl:if test="artifact">
                <b>
                  <xsl:text>File(s): </xsl:text>
                  <xsl:if test="status != 'active'">
                    <xsl:value-of select="status"/>
                  </xsl:if>
                </b>
                <div id="{key}">
                  <!-- Show or hide div based on status -->
                  <xsl:choose>
                    <xsl:when test="status != 'active'">
                      <xsl:attribute name="style">display:none</xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:attribute name="style">display:block</xsl:attribute>
                    </xsl:otherwise>
                  </xsl:choose>

                  <xsl:for-each select = "artifact">
                    <xsl:if test="web-link/label">
                      <xsl:value-of select="web-link/label" disable-output-escaping="yes"/><xsl:text> </xsl:text>
                    </xsl:if>
                    <a href = "{web-link/URL}">
                      <xsl:value-of select="web-link/link-text"/>
                    </a>
                    <br/>
                  </xsl:for-each>
                </div>
              </xsl:if>
              
              <!-- List web links -->
              <xsl:if test="link">
                <b>
                  <xsl:text>Link(s): </xsl:text>
                  <xsl:if test="status != 'active'">
                    <xsl:value-of select="status"/>
                  </xsl:if>
                </b>
                <div id="{key}">
                  <!-- Show or hide div based on status -->
                  <xsl:choose>
                    <xsl:when test="status != 'active'">
                      <xsl:attribute name="style">display:none</xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:attribute name="style">display:block</xsl:attribute>
                    </xsl:otherwise>
                  </xsl:choose>

                  <xsl:for-each select = "link">
                    <xsl:if test="web-link/label">
                      <xsl:value-of select="web-link/label" disable-output-escaping="yes"/><xsl:text> </xsl:text>
                    </xsl:if>
                    <a href = "{web-link/URL}">
                      <xsl:value-of select="web-link/link-text"/>
                    </a>
                    <br/>
                  </xsl:for-each>
                </div>
              </xsl:if>
              
            
              <!-- List parameters -->
              <xsl:if test="parameter">
                <b>
                  <xsl:text>Parameters: </xsl:text>
                  <xsl:if test="status != 'active'">
                    <xsl:value-of select = "status"/>
                  </xsl:if>
                </b>
                <div id="{key}">
                  <!-- Show or hide div based on status -->
                  <xsl:choose>
                    <xsl:when test="status != 'active'">
                      <xsl:attribute name="style">display:none</xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:attribute name="style">display:block</xsl:attribute>
                    </xsl:otherwise>
                  </xsl:choose>

                  <xsl:for-each select = "parameter">
                    <xsl:value-of select="name"/><br/>
                  </xsl:for-each>
                </div>
              </xsl:if>
              <br/>
              
              <!-- Add button if status not active -->
              <xsl:if test="status != 'active'">
                <div id="button-{key}" style= "display:block">
                  <input type="button" value="Click to show" onclick="showFiles('{key}','button-{key}')"/>
                  <br/>
                  <br/>
                </div>
              </xsl:if>
            
            </div>
          </xsl:for-each>
        </div>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>