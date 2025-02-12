# Start with :MusicType
*. :MusicType->bf:Place
    *.1. :WindAndDrumMusic->bf:Place
*. :MusicType->dbpedia-owl:EthnicGroup
    e.g.,喊傣亮、四簧口弦琴曲、御神歌、“宫廷筵宴乐-缅甸乐”、加美兰、扎平各是哪些民族的？(translated as: Which ethnic groups do Hǎn Dǎi Liàng, four-reed jaw harp music, Sacred Shinto Hymns(ぎょしんか), 'Imperial Banquet Music – Burmese Music,' Gamelan, and Zhāpíng belong to?)
    expectedExtractedEntities: {ctm:MusicType dbpedia-owl:EthnicGroup}{ctm:ethnicGroup}
*. :MusicType->:FolkMusician
    expectedExtractedEntities: {ctm:MusicType ctm:FolkMusician}{:representativeFolkMusician}     
*. :MusicType->mo:Instrument
    *.1. :NationalInstrumentalMusic->mo:Instrument
        expectedExtractedEntities: {ctm:MusicType mo:Instrument}{ctm:musicTypePrincipalInstrument}
*. :MusicType->:SpecialIndependentResource
    e.g.,朝鲜族民歌、潮尔在我馆是否有对应的特藏资源收录？[translated as: Does our library have any special collection resources on Korean folk songs and Tsuur(Chao'er)?]
        expectedExtractedEntities: {ctm:MusicType ctm:SpecialIndependentResource}{ctm:relatesWork}
        However, this question is a little ambiguous since "潮尔" is the rdfs:label of instances of both `mo:Instrument` and `ctm:MusicType`. So a clearer question should be like 朝鲜族民歌、潮尔（作为音乐类型_乐种）在我馆是否有对应的特藏资源收录？[translated as: Does our library have any special collection resources on Korean folk songs and Tsuur(Chao'er, a music type)?]
    *.1 :MusicType->:SpecialIndependentResource->mo:Instrument
        e.g.,福建南音在我馆是否有特藏资源收录，若有，这些资源涉及什么乐器？(translated as: Does our library have any special collection resources on Fujian Nanyin? If so, which instruments are covered in these resources?)
        expectedExtractedEntities: {ctm:MusicType ctm:SpecialIndependentResource mo:Instrument}{ctm:relatesWork}
*. :MusicType->:PieceWithPerformance->mo:Instrument
    expectedExtractedEntities: {ctm:MusicType ctm:PieceWithPerformance mo:Instrument}{bf:instrument ctm:representativePiece ctm:samplePieceWithPerformance} # This involves both objectProperty and dataProperty

# Start with mo:Instrument
*. mo:Instrument->:MusicType
    expectedExtractedEntities: {mo:Instrument ctm:NationalInstrumentalMusic}{ctm:instrumentRepresentativeMusicType}
*. mo:Instrument->dbpedia-owl:EthnicGroup
    e.g.,鼻箫这件乐器是哪个民族的？潮尔又是哪个民族的？(translated as: Which ethnic group does the nose flute belong to? And which ethnic group does Tsuur belong to?)
    expectedExtractedEntities: {mo:Instrument mo:MusicType dbpedia-owl:EthnicGroup}{ctm:ethnicGroup}
    
*. mo:Instrument->:MusicType->dbpedia-owl:EthnicGroup - see below

# Start with :SpecialIndependentResource
*. :SpecialIndependentResource->:MusicType,:mo:Instrument,:dbpedia-owl:EthnicGroup
    e.g.,《越南闲愁》涉及到什么音乐类型(乐种)、乐器、民族？(translated as: What music types, instruments, and ethnic groups are involved in "Vietnamese Idle Sorrow"?)
    --it doesn't clarify whether it's "or (union of)" or it's "and (intersection of)"
    expectedExtractedEntities: {:SpecialIndependentResource :MusicType mo:Instrument dbpedia-owl:EthnicGroup}{:relatesMusicType :relatesInstrument :ethnicGroup}
*. :MusicType<-:SpecialIndependentResource->bf:Place
    e.g.,我馆有什么特藏资源涉及甘美兰音乐，该资源涉及的地域在哪？[or make it more complicated: 我馆有什么特藏独立资源_作品涉及甘美兰音乐，该资源是在哪里（涉及的地域）采录到的？](translated as: What special collection resources does our library have related to Gamelan music, and which places do these resources cover?)""We haven't tried generating SPARQL based on the assembled ontology snippet""
    expectedExtractedEntities: {:SpecialIndependentResource :MusicType bf:Place}{:relatesMusicType :relatesPlace}

# Start with bf:Place
*. bf:Place->:MusicType->mo:Instrument->dbpedia-owl:EthnicGroup
    e.g.,云南省有哪些音乐类型_乐种，这些乐种可能用到什么乐器，这些乐器又可能涉及哪些族群？(translated as: What music types exist in Yunnan Province? What instruments are commonly used in these music types, and which ethnic groups are associated with these instruments?)""We haven't tried generating SPARQL based on the assembled ontology snippet""
    expectedExtractedEntities: {bf:Place ctm:MusicType mo:Instrument dbpedia-owl:EthnicGroup}{ctm:placeHasMusicTypeOrInstrument ctm:musicType_Instrument ctm:ethnicGroup}

# Start with dbpedia-owl:EthnicGroup
*. dbpedia-owl:EthnicGroup->:MusicType->bf:Place
    e.g.,蒙古族有哪些音乐类型_乐种，这些乐种的分布地域各是什么？(translated as: What music types exist in Mongolian culture, and what are the regional distributions of these types?)""We haven't tried verifying the completeness of the extracted entities from ontology""
    expectedExtractedEntities: {bf:Place ctm:MusicType dbpedia-owl:EthnicGroup}{bf:place ctm:representativeMusicType}

# Start with :FolkMusician
*. :FolkMusician->:MusicType
    e.g.,民间乐人李燕生擅长什么乐种？(translated as: What music types is the folk musician Li Yansheng skilled in?)
    expectedExtractedEntities: {ctm:FolkMusician ctm:MusicType}{ctm:goodAtPerformingMusic}