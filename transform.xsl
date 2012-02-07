<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output indent="yes" method="xml"/>
    <xsl:template match="/">
        <dumb>
            <xsl:apply-templates select="//head"/>
        <desc>
            <xsl:apply-templates select="//body"/>
        </desc>
        </dumb>
    </xsl:template>
    <xsl:template match="//head">
        <xsl:apply-templates select="//persName"></xsl:apply-templates>
    </xsl:template>
    <xsl:template match="persName">
        <xsl:if test="string(@lang)!='greek'">
            <name>
            <xsl:message> found </xsl:message>
            <xsl:variable name="apos">'</xsl:variable>
            <!-- the addName could be expanded easily: M. => Marcus, C. => Gaius, etc.-->
            <xsl:value-of select="normalize-space(concat(translate(surname,$apos,''),' ',translate(foreName,$apos,''),' ',translate(addName,$apos,'')))"/>
            </name>
        </xsl:if>
       
    </xsl:template>
    <xsl:template match="//head/label/persName">
        <name>
        <xsl:message> found </xsl:message>
        <xsl:variable name="apos">'</xsl:variable>
        <xsl:value-of select="normalize-space(concat(translate(surname,$apos,''),' ',translate(foreName,$apos,''),' ',translate(addName,$apos,'')))"/>
        </name>
    </xsl:template>
    <xsl:template match="body">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>
</xsl:stylesheet>
