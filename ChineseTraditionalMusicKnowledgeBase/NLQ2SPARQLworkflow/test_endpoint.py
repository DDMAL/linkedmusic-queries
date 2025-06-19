#!/usr/bin/env python3
"""
简化的SPARQL查询测试脚本
"""

import urllib.request
import urllib.parse
import json

def test_simple_query():
    """
    测试简单的SPARQL查询
    """
    endpoint = "http://www.usources.cn:8891/sparql"
    
    # 简单的测试查询
    simple_query = """
PREFIX ctm: <https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?org ?orgLabel
WHERE {
  ?org a ctm:FolkMusicOrganization .
  ?org rdfs:label ?orgLabel .
}
LIMIT 10
"""
    
    # 准备请求
    params = {
        'query': simple_query,
        'default-graph-uri': 'https://lib.ccmusic.edu.cn/graph/music'
    }
    
    data = urllib.parse.urlencode(params).encode('utf-8')
    
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    
    try:
        print("正在测试SPARQL端点连接...")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')
            data = json.loads(result)
            
            bindings = data.get('results', {}).get('bindings', [])
            print(f"简单查询成功！找到 {len(bindings)} 个民间音乐组织")
            
            for i, binding in enumerate(bindings[:3]):
                org_label = binding.get('orgLabel', {}).get('value', 'N/A')
                print(f"  {i+1}. {org_label}")
            
            return True
            
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

if __name__ == "__main__":
    if test_simple_query():
        print("\n端点连接正常，您可以尝试运行完整查询")
    else:
        print("\n端点连接有问题，请检查网络或端点状态")
