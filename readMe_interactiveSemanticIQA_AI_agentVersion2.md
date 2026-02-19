# Interactive Semantic Intelligent QA Agent version 2 
- URL: http://101.201.37.120/ (When running the workflow, there is some issue, to be repaired soon. Please check back later.)

- You may try the AI agent by entering your questions in the input box.
Example questions:
    1. 东不拉这种乐器分布在哪里？
    2. 东不拉分布在哪里？
    3. 东不拉分布在哪里，其所分布的地域还有哪些弹弦类乐器？
    4. 苗族有哪些民间乐人，他们擅长什么乐种？那么这些乐种又会涉及什么乐器，它们的霍萨声学分类情况又如何？
    5. 支脉和语族有什么关系？
    6. 有哪些民族既属于中国音乐体系，又属于其他音乐体系？
    7. 福建南音是否涉及我馆的某些特藏资源，若有，这些资源有可能涉及什么乐器？
    8. 我国东南地区的少数民族有哪些音乐类型_乐种，这些乐种的分布地域各是什么，而这些分布地域又还有哪些其他的乐器？
    9. 有哪些乐人擅长哪些音乐类型(乐种)？请返回给我不超过20条数据，并按照擅长乐种的数目做降序列出，即擅长乐种数量最多的排在最前面。
    10. 我想看看乐器中，哪些是涉及新疆维吾尔自治区（地域）或中国的大西北地区的，尤其是它的弹拨乐器（也可以考虑从霍萨分类法的角度来考察）。
    11. 属于藏缅语族的民族的乐器和属于壮侗语族的民族的乐器在声学特征（如霍萨分类方面）上可能有什么差异？


# Chinese Traditonal Music Culture Knowledge Base (中华传统音乐文化知识库：平台试用地址)
- main/home page: http://101.201.37.120:8080/mcdemo/home
- SPARQL query page: http://101.201.37.120:8080/mcdemo/sparql

# SPARQL endpoint (终端) from open link virtuoso
http://101.201.37.120:8890/sparql
 
# Query Examples (for the paper _"Interactive Semantic Intelligent Question-Answering Agent (Enhanced Version 2.0) for an Interoperable Chinese Traditional Music Linked Data Platform"_)
## 3.1.1 > (4) Hybrid query scope across T‑Box and A‑Box (to be added soon)
```sparql
# to be added soon
```

## 针对论文《知识图谱+大模型：中华传统音乐文化知识库关联数据“互操作”平台—智能体与“知识地图”前导性研究——兼论音乐数字人文潜学科群新方向》
### 三、 > （二） > 问题：“北省石家庄市及与其相邻2步长（毗邻关系）范围内的其他城市（含下辖县区级行政单位）有什么乐种？这些乐种中，哪些又能关联到中国音乐学院图书馆的特藏资源？“
```sparql
define input:inference 'urn:owl.ccmusicrules0913' # 用于Open Link Virtuoso中激活推理机
PREFIX bf: <http://id.loc.gov/ontologies/bibframe/>
PREFIX ctm: <https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX places: <http://purl.org/ontology/places#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# 注意：激活下方的变量?distance，则可显示相应的边列表关系是第几步长范围内的
SELECT distinct ?source ?sourceLabel ?target ?targetLabel ?relationType #?distance
WHERE {
  # Identify 石家庄市 as our starting point
  ?shijiazhuang rdfs:label "石家庄市" .
  ?shijiazhuang a places:City .
  
  {
    # Part 1: City-to-City connections 城市间的毗邻关系
    {
      # Direct neighbors (1 step)
      ?shijiazhuang gn:neighbour ?target .
      BIND(?shijiazhuang AS ?source)
      BIND(1 AS ?distance)
      BIND(gn:neighbour AS ?relationType)
    } 
    UNION 
    {
      # 2 steps away
      ?shijiazhuang gn:neighbour ?intermediate1 .
      ?intermediate1 gn:neighbour ?target .
      FILTER(?target != ?shijiazhuang)  # Avoid cycles back to origin
      BIND(?intermediate1 AS ?source)
      BIND(2 AS ?distance)
      BIND(gn:neighbour AS ?relationType)
    }
    
    # Get readable labels for cities
    ?source rdfs:label ?sourceLabel .
    ?target rdfs:label ?targetLabel .
  }
  
  UNION
  
  {
    # Part 2: County-to-City relationships 县、区级行政单位到市级行政单位的信息
   {
   # Direct parent-child relationship - counties of Shijiazhuang
    ?county gn:parentADM2 ?shijiazhuang .
    ?county a places:County .
    ?county rdfs:label ?sourceLabel .
    ?shijiazhuang rdfs:label ?targetLabel .
    BIND(?county AS ?source)
    BIND(?shijiazhuang AS ?target)
    BIND(gn:parentADM2 AS ?relationType)
  }
  UNION
  {
    # Counties of neighboring cities
    ?shijiazhuang gn:neighbour ?neighborCity .
    ?neighborCity a places:City .
    ?county gn:parentADM2 ?neighborCity .
    ?county a places:County .
    ?county rdfs:label ?sourceLabel .
    ?neighborCity rdfs:label ?targetLabel .
    BIND(?county AS ?source)
    BIND(?neighborCity AS ?target)
    BIND(gn:parentADM2 AS ?relationType)
  }
  UNION
  {
    # Counties of cities 2 steps away
    ?shijiazhuang gn:neighbour ?intermediate1 .
    ?intermediate1 gn:neighbour ?distantCity .
    FILTER(?distantCity != ?shijiazhuang)
    ?distantCity a places:City .
    ?county gn:parentADM2 ?distantCity .
    ?county a places:County .
    ?county rdfs:label ?sourceLabel .
    ?distantCity rdfs:label ?targetLabel .
    BIND(?county AS ?source)
    BIND(?distantCity AS ?target)
    BIND(gn:parentADM2 AS ?relationType)
  }
}
  
  UNION
  
   {
   # Part 3: MusicType-to-County relationships 乐种及其分布地域（仅以县区级行政单位为例）
   {
    # Music types related to counties in Shijiazhuang
    ?county gn:parentADM2 ?shijiazhuang .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?musicType rdfs:label ?sourceLabel .
    ?county rdfs:label ?targetLabel .
    BIND(?musicType AS ?source)
    BIND(?county AS ?target)
    BIND(bf:place AS ?relationType)
    FILTER(LANG(?sourceLabel) != "py")
  }
  UNION
  {
    # Music types related to counties in neighboring cities
    ?shijiazhuang gn:neighbour ?neighborCity .
    ?neighborCity a places:City .
    ?county gn:parentADM2 ?neighborCity .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?musicType rdfs:label ?sourceLabel .
    ?county rdfs:label ?targetLabel .
    BIND(?musicType AS ?source)
    BIND(?county AS ?target)
    BIND(bf:place AS ?relationType)
    FILTER(LANG(?sourceLabel) != "py")
  }
  UNION
  {
    # Music types related to counties in cities 2 steps away
    ?shijiazhuang gn:neighbour ?intermediate1 .
    ?intermediate1 gn:neighbour ?distantCity .
    FILTER(?distantCity != ?shijiazhuang)
    ?distantCity a places:City .
    ?county gn:parentADM2 ?distantCity .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?musicType rdfs:label ?sourceLabel .
    ?county rdfs:label ?targetLabel .
    BIND(?musicType AS ?source)
    BIND(?county AS ?target)
    BIND(bf:place AS ?relationType)
    FILTER(LANG(?sourceLabel) != "py")
  }
  }
  
  UNION
  
    {
    # Part 4: SpecialIndependentResource-to-MusicType relationships 特藏独立资源及其涉及的乐种
  {
    # specialResources related to musicTypes in Shijiazhuang counties
    ?county gn:parentADM2 ?shijiazhuang .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?specialResource a ctm:SpecialIndependentResource .
    ?specialResource ctm:relatesMusicType ?musicType .
    ?specialResource rdfs:label ?sourceLabel .
    ?musicType rdfs:label ?targetLabel .
    BIND(?specialResource AS ?source)
    BIND(?musicType AS ?target)
    BIND(ctm:relatesMusicType AS ?relationType)
    FILTER(LANG(?targetLabel) != "py")
  }
  UNION
  {
    # specialResources related to musicTypes in neighboring cities' counties
    ?shijiazhuang gn:neighbour ?neighborCity .
    ?neighborCity a places:City .
    ?county gn:parentADM2 ?neighborCity .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?specialResource a ctm:SpecialIndependentResource .
    ?specialResource ctm:relatesMusicType ?musicType .
    ?specialResource rdfs:label ?sourceLabel .
    ?musicType rdfs:label ?targetLabel .
    BIND(?specialResource AS ?source)
    BIND(?musicType AS ?target)
    BIND(ctm:relatesMusicType AS ?relationType)
    FILTER(LANG(?targetLabel) != "py")
  }
  UNION
  {
    # specialResources related to musicTypes in counties of cities 2 steps away
    ?shijiazhuang gn:neighbour ?intermediate1 .
    ?intermediate1 gn:neighbour ?distantCity .
    FILTER(?distantCity != ?shijiazhuang)
    ?distantCity a places:City .
    ?county gn:parentADM2 ?distantCity .
    ?county a places:County .
    ?musicType bf:place ?county .
    ?specialResource a ctm:SpecialIndependentResource .
    ?specialResource ctm:relatesMusicType ?musicType .
    ?specialResource rdfs:label ?sourceLabel .
    ?musicType rdfs:label ?targetLabel .
    BIND(?specialResource AS ?source)
    BIND(?musicType AS ?target)
    BIND(ctm:relatesMusicType AS ?relationType)
    FILTER(LANG(?targetLabel) != "py")
  }
  }
}
```

### 三、 > （三） > 问题：“湖北省荆门市（市中心为东宝区）方圆75公里内有哪些乐种，其中，哪些在我们图书馆有收藏？“
```sparql
define input:inference 'urn:owl.ccmusicrules0913' # 用于激活推理机
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX ctm: <https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#>
PREFIX bf: <http://id.loc.gov/ontologies/bibframe/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select distinct ?OtherCity ?otherCityLab ?OtherCounty ?coordin ?otherCounLab ?distan ?MTForCity ?mTFCityLab ?mTFCounty ?mTFCounLab ?Reso # ?resouL # ?MusicType2 
where {
  # （1）找到荆门市中心的东宝区的坐标，以及东宝区可能存在的音乐类型(乐种)：
  ?CenterCounty rdfs:label "东宝区" ;
                           wdt:P625 ?centerCoordinateLocation .
   # optional { ?MusicType1 bf:place ?CenterCounty ; a ctm:MusicType } # [随后事实发现，并没有音乐类型(乐种)是直接关联东宝区的]
  # （2）规定好备选的其他县区级行政单位的坐标，以及其所隶属的市级行政单位，以及隶属于该县区级行政单位的乡镇级行政单位：
  ?OtherCounty wdt:P625 ?coordin ; # P625为坐标属性
                          gn:parentADM2 ?OtherCity ; # 县、区级行政单位地域隶属于某市级行政单位?OtherCity      
                          rdfs:label ?otherCounLab .
  ?OtherCity rdfs:label ?otherCityLab .
  # ?OtherTown gn:parentADM3 ?OtherCounty . # 某些乡镇级行政单位?OtherTown隶属于该县级行政单位（假定一个县区级行政单位必然有下辖的乡镇级行政单位）
  # （3）如果某些音乐类型(乐种)的分布地域是那些县区级或市级行政单位，进而，如果这些音乐类型涉及到我馆的特藏独立资源
  optional { 
    ?mTFCounty a ctm:MusicType ;
                          bf:place ?OtherCounty ;
                          rdfs:label ?mTFCounLab .
    FILTER(LANG(?mTFCounLab) != "py")
    optional { ?mTFCounty ctm:relatesWork ?Reso .
               #?SpecialIndependentResource rdfs:label ?resouL
}
  }
  
  optional { 
    ?MTForCity a ctm:MusicType ;
                        bf:place ?OtherCity ;
                        rdfs:label ?mTFCityLab .
    FILTER(LANG(?mTFCityLab) != "py")
    optional { ?MTForCity ctm:relatesWork ?Reso .
               #?SpecialIndependentResource rdfs:label ?resouL
}
  }
#  optional { ?MusicType2 a ctm:MusicType ; 
#                                         bf:place ?OtherTown . # [可能并有音乐类型(乐种)是直接关联此片县级行政单位下属的乡镇级行政单位的，为了本案例研究的简约性，暂对此略去]
#             optional { ?MusicType2 ctm:relatesWork ?SpecialIndependentResource . }}
#（4）计算东宝区和其他县级行政单位之间的距离，设筛选条件为75公里之内
  bind (bif:st_distance(?centerCoordinateLocation, ?coordin) AS ?distan)
  filter (?distan<=75)
} 
group by ?OtherCity ?otherCityLab ?OtherCounty ?coordin ?otherCounLab ?distan ?MTForCity ?mTFCityLab ?mTFCounty ?mTFCounLab ?Reso # ?resouL # ?MusicType2 # 为了避免返回的数据行有重复，故加group by
order by ?distan

