# Start with :MusicType
*. :MusicType->bf:Place
    *.1. :WindAndDrumMusic->bf:Place
*. :MusicType->:FolkMusician
    expectedExtractedEntities: {ctm:MusicType ctm:FolkMusician}{:representativeFolkMusician}     
*. :MusicType->mo:Instrument
    *.1. :NationalInstrumentalMusic->mo:Instrument
        expectedExtractedEntities: {ctm:MusicType mo:Instrument}{ctm:musicTypePrincipalInstrument}
*. :MusicType->:SpecialIndependentResource
    e.g.,朝鲜族民歌、潮尔在我馆是否有对应的特藏资源收录？
        expectedExtractedEntities: {ctm:MusicType ctm:SpecialIndependentResource}{ctm:relatesWork}
        However, this question is a little ambiguous since "潮尔" is the rdfs:label of instances of both `mo:Instrument` and `ctm:MusicType`. So a clearer question should be like 朝鲜族民歌、潮尔（作为音乐类型_乐种）在我馆是否有对应的特藏资源收录？
    *.1 :MusicType->:SpecialIndependentResource->mo:Instrument
        e.g.,福建南音在我馆是否有特藏资源收录，若有，这些资源涉及什么乐器？

6. :MusicType->:PieceWithPerformance->mo:Instrument
    expectedExtractedEntities: {ctm:MusicType ctm:PieceWithPerformance mo:Instrument}{bf:instrument ctm:representativePiece ctm:samplePieceWithPerformance} # This involves both objectProperty and dataProperty

# Start with :FolkMusician
4. :FolkMusician->:MusicType

# Start with mo:Instrument
*. mo:Instrument->:MusicType
    expectedExtractedEntities: {mo:Instrument ctm:NationalInstrumentalMusic}{ctm:instrumentRepresentativeMusicType}
*. mo:Instrument->dbpedia-owl:EthnicGroup - see below
    e.g.,
*. mo:Instrument->:MusicType->dbpedia-owl:EthnicGroup - see below

# Start with :SpecialIndependentResource
*. e.g.,《越南闲愁》涉及到什么音乐类型(乐种)、乐器、民族？
    --it doesn't clarify whether it's "or (union of)" or it's "and (intersection of)"
5. :MusicType<-:SpecialIndependentResource->bf:Place

# Start with dbpedia-owl:EthnicGroup
2. dbpedia-owl:EthnicGroup->:MusicType->bf:Place

# Start with bf:Place
6. bf:Place->:MusicType->mo:Instrument->dbpedia-owl:EthnicGroup