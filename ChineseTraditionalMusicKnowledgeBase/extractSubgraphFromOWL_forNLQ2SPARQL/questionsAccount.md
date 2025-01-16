1. :MusicType->bf:Place
    1-1. :WindAndDrumMusic->bf:Place
*. :MusicType->:FolkMusician
    expectedExtractedEntities: {ctm:MusicType ctm:FolkMusician}{:representativeFolkMusician}     
    4. :FolkMusician->:MusicType
5. :MusicType->mo:Instrument
    *. :NationalInstrumentalMusic->mo:Instrument
        expectedExtractedEntities: {ctm:MusicType mo:Instrument}{ctm:musicTypePrincipalInstrument}
*. :MusicType->:PieceWithPerformance->mo:Instrument
3. :MusicType<-:SpecialIndependentResource->bf:Place

*. mo:Instrument->:MusicType
*. mo:Instrument->dbpedia-owl:EthnicGroup - see below
*. mo:Instrument->:MusicType->dbpedia-owl:EthnicGroup - see below

2. dbpedia-owl:EthnicGroup->:MusicType->bf:Place
6. bf:Place->:MusicType->mo:Instrument->dbpedia-owl:EthnicGroup