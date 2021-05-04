<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="*" name="implementation">
    <div>
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
        
        <!-- Content choice -->
        <xsl:choose>
          
          <!-- List artifact files -->
          <xsl:when test="artifact">
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
            </div><br/>
          </xsl:when>
          
          <!-- List web links -->
          <xsl:when test="link">
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
            </div><br/>
          </xsl:when>
          
        
          <!-- List parameters -->
          <xsl:when test="parameter">
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
            </div><br/>
          </xsl:when>

          <!-- Otherwise, do nothing-->
          <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
      
        <!-- Add button if status not active -->
        <xsl:if test="status != 'active'">
          <div id="button-{key}" style= "display:block">
            <input type="button" value="Click to show" onclick="showFiles('{key}','button-{key}')"/>
            <br/>
            <br/>
          </div>
        </xsl:if>
      
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>