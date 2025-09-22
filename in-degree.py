# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import quote
import csv

# SPARQLエンドポイント（日本語DBpedia）
SPARQL_ENDPOINT = "http://ja.dbpedia.org/sparql"

# ====== 入次数を取得する関数 ======
def get_indegree(keyword):
    uri = f"<http://ja.dbpedia.org/resource/{keyword}>"
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    query = f"""
    SELECT DISTINCT ?link WHERE {{
        ?link <http://dbpedia.org/ontology/wikiPageWikiLink> {uri} .
        FILTER(STRSTARTS(STR(?link), "http://ja.dbpedia.org/resource/"))
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return len(results["results"]["bindings"])
    except Exception as e:
        print(f"[ERROR] SPARQL失敗: {keyword} → {e}")
        return -1



# ====== 語句ごとに入次数を取得（重複許容） ======
def count_indegrees_allow_duplicates(keywords):
    results = []
    for kw in keywords:
        kw = kw.strip()
        if kw:
            count = get_indegree(kw)
            print(f"{kw} → {count}")
            results.append((kw, count))
    return results

# ====== CSVに保存 ======
def save_to_csv(data, filename="indegree_ja_dbpedia.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["語句", "入次数"])
        writer.writerows(data)

# ====== メイン処理 ======
if __name__ == "__main__":
    raw_input = """
    思考 理性 知覚 聴覚 五感 哲学 美学　形而上学 弁証法 論理学 知覚 聴覚 五感　触覚 皮膚感覚 心理療法 心理療法の一覧 精神分析学 精神医学 精神障害 精神分析学 ジークムント・フロイト 精神医学 精神障害 精神科 意識 心の哲学 認識論 真理 存在論
    """
    # 全角スペース対応
    keywords = raw_input.replace("　", " ").split()
    results = count_indegrees_allow_duplicates(keywords)
    save_to_csv(results)
    print("\n📁 結果を indegree_ja_dbpedia.csv に保存しました。")