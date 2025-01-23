1. :MusicType->bf:Place
    1-1. :WindAndDrumMusic->bf:Place
2. :MusicType->:FolkMusician
    expectedExtractedEntities: {ctm:MusicType ctm:FolkMusician}{:representativeFolkMusician}     
3. :MusicType->mo:Instrument
    3.1. :NationalInstrumentalMusic->mo:Instrument
        expectedExtractedEntities: {ctm:MusicType mo:Instrument}{ctm:musicTypePrincipalInstrument}
4. :MusicType->:SpecialIndependentResource
    e.g.,朝鲜族民歌、潮尔在我馆是否有对应的特藏资源收录？
        expectedExtractedEntities: {ctm:MusicType ctm:SpecialIndependentResource}{ctm:relatesWork}
        However, this question is a little ambiguous since "潮尔" is the rdfs:label of instances of both `mo:Instrument` and `ctm:MusicType`
3. :MusicType<-:SpecialIndependentResource->bf:Place
*. :MusicType->:PieceWithPerformance->mo:Instrument
    expectedExtractedEntities: {ctm:MusicType ctm:PieceWithPerformance mo:Instrument}{bf:instrument ctm:representativePiece ctm:samplePieceWithPerformance} # This involves both objectProperty and dataProperty


4. :FolkMusician->:MusicType

*. mo:Instrument->:MusicType
    expectedExtractedEntities: {mo:Instrument ctm:NationalInstrumentalMusic}{ctm:instrumentRepresentativeMusicType}
*. mo:Instrument->dbpedia-owl:EthnicGroup - see below
    e.g.,
*. mo:Instrument->:MusicType->dbpedia-owl:EthnicGroup - see below

2. dbpedia-owl:EthnicGroup->:MusicType->bf:Place
6. bf:Place->:MusicType->mo:Instrument->dbpedia-owl:EthnicGroup