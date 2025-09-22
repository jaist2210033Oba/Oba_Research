from SPARQLWrapper import SPARQLWrapper, JSON
from gensim.models import KeyedVectors
import json

# ====== 設定 ======
SPARQL_ENDPOINT = "http://ja.dbpedia.org/sparql"
MODEL_PATH = "C:/MyResearch/entity_vector/entity_vector.model.bin"
MAX_DEPTH = 6
SCENARIO_NUM = 3

print("[INFO] Word2Vecモデルを読み込み中...")
model = KeyedVectors.load_word2vec_format(MODEL_PATH, binary=True)

# ====== DBpediaリンク取得 ======
def get_wikilinks(keyword):
    uri = f"<http://ja.dbpedia.org/resource/{keyword}>"
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    query = f"""
    SELECT DISTINCT ?link WHERE {{
        {uri} <http://dbpedia.org/ontology/wikiPageWikiLink> ?link .
        FILTER(STRSTARTS(STR(?link), "http://ja.dbpedia.org/resource/"))
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return [
            result["link"]["value"].replace("http://ja.dbpedia.org/resource/", "")
            for result in results["results"]["bindings"]
        ]
    except Exception as e:
        print(f"[ERROR] SPARQL失敗: {e}")
        return []

# ====== 類似度最大の語を1つ選ぶ ======
def select_best_link(links, base_word, visited):
    scored = []
    for word in links:
        if word in model and base_word in model and word not in visited and word != base_word:
            sim = model.similarity(base_word, word)
            scored.append((word, sim))
    if not scored:
        return None
    return max(scored, key=lambda x: x[1])[0]

# ====== シナリオ構築（1本道） ======
def build_single_path(current_word, depth, visited, base_word):
    score = float(model.similarity(base_word, current_word)) if current_word in model and base_word in model else 0.0

    node = {"keyword": current_word, "depth": depth, "score": round(score, 3), "children": []}

    if depth >= MAX_DEPTH:
        return node

    visited.add(current_word)
    links = get_wikilinks(current_word)
    filtered_links = [w for w in links if w not in visited and w != base_word]
    next_word = select_best_link(filtered_links, base_word, visited)

    if next_word:
        visited.add(next_word)
        child_node = build_single_path(next_word, depth + 1, visited, base_word)
        node["children"].append(child_node)
    return node

# ====== 表示関数（スコア付き） ======
def print_scenario(scenario):
    print(f"Depth {scenario['depth']}: {scenario['keyword']} ({scenario.get('score', 1.000):.3f})")
    for child in scenario.get("children", []):
        print_scenario(child)

# ====== メイン処理 ======
if __name__ == "__main__":
    start_word = input("初期キーワードを入力してください：").strip()

    # 初期リンク取得 → 初期語とのスコアで上位3語を選出
    initial_links = get_wikilinks(start_word)
    scored_links = []
    for word in initial_links:
        if word in model and start_word in model and word != start_word:
            sim = model.similarity(start_word, word)
            scored_links.append((word, sim))
    scored_links.sort(key=lambda x: x[1], reverse=True)
    top3_words = [word for word, _ in scored_links[:SCENARIO_NUM]]

    # シナリオ生成
    scenarios = []
    for i, word in enumerate(top3_words):
        print(f"\n[INFO] シナリオ{i+1}を生成中...")
        scenario = {
            "keyword": start_word,
            "depth": 0,
            "score": 1.000,
            "children": [
                build_single_path(word, 1, set([start_word]), start_word)
            ]
        }
        scenarios.append(scenario)

    # JSON保存
    with open("learning_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    # 整形表示
    for i, scenario in enumerate(scenarios):
        print(f"\n--- シナリオ{i+1} ---")
        print_scenario(scenario)
