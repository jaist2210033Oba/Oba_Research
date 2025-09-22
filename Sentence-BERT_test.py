from sentence_transformers import SentenceTransformer, util
import pandas as pd

# モデル読み込み（日本語対応）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 評価対象のシナリオ群（各行がシナリオ）
scenarios = [
    ["環境問題", "海面上昇", "気候変動", "地球温暖化", "寒冷化", "地球寒冷化", "二酸化炭素"],
    ["環境問題", "海面上昇", "水質汚濁", "富栄養化", "ヘドロ", "水質汚染", "土壌汚染"],
    ["環境問題", "海面上昇", "大気汚染", "土壌汚染", "水質汚濁", "水質汚染", "海洋汚染"],
    ["環境問題", "海面上昇", "地球温暖化", "地球温暖化の影響", "気候", "気温", "ヒートアイランド"],
    ["環境問題", "海面上昇", "気候変動", "地球温暖化", "地球温暖化の影響", "気候", "気温"],
    ["環境問題", "海面上昇", "ツバル", "地球温暖化", "地球温暖化の影響", "地球温暖化への対策", "地球温暖化の原因"]
]

# ユーティリティ
def to_sentence(word):
    return f"{word}について学ぶ"

def encode(word):
    return model.encode(to_sentence(word), convert_to_tensor=True)

# 各スコア算出
records = []
for i, scenario in enumerate(scenarios):
    main = scenario[0]
    sub = scenario[1]
    rest = scenario[2:]
    scenario_id = f"Scenario {i+1}"

    # エンコード
    emb_main = encode(main)
    emb_sub = encode(sub)
    emb_rest = [encode(w) for w in rest]
    emb_all = [encode(w) for w in scenario]

# 主題スコア
    main_scores = [round(util.cos_sim(emb_main, emb).item(), 3) for emb in emb_rest]
    main_avg = round(sum(main_scores) / len(main_scores), 3)

# 副題スコア
    sub_scores = [round(util.cos_sim(emb_sub, emb).item(), 3) for emb in emb_rest]
    sub_avg = round(sum(sub_scores) / len(sub_scores), 3)

# 流れスコア（隣接語）
    flow_scores = [round(util.cos_sim(e1, e2).item(), 3) for e1, e2 in zip(emb_all, emb_all[1:])]
    flow_avg = round(sum(flow_scores) / len(flow_scores), 3)


    records.append({
        "シナリオID": scenario_id,
        "主題スコア（平均）": main_avg,
        "主題スコア（内訳）": main_scores,
        "副題スコア（平均）": sub_avg,
        "副題スコア（内訳）": sub_scores,
        "流れスコア（平均）": flow_avg,
        "流れスコア（内訳）": flow_scores
    })

# 結果をDataFrame化して表示
df_results = pd.DataFrame(records)
print(df_results)
