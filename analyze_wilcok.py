import pandas as pd
from scipy.stats import wilcoxon

# ===== データ読み込み =====
df = pd.read_csv("sinario_11.csv", encoding="utf-8-sig")
#df = pd.read_csv("sinario_11.csv", encoding="cp932")

# ===== 既知性を逆尺度に変換（新規性） =====
for col in ["既知性_W1","既知性_W2","既知性_W3",
            "既知性_S1","既知性_S2","既知性_S3"]:
    df[col] = 6 - df[col]

# ===== 被験者ごとに平均（全テーマまとめて） =====
grouped = df.groupby("被験者").mean(numeric_only=True).reset_index()

# ===== Word2Vec・積集合の平均 =====
W_main = grouped[["主題理解_W1","主題理解_W2","主題理解_W3"]].mean(axis=1)
S_main = grouped[["主題理解_S1","主題理解_S2","主題理解_S3"]].mean(axis=1)

W_relation = grouped[["関連性_W1","関連性_W2","関連性_W3"]].mean(axis=1)
S_relation = grouped[["関連性_S1","関連性_S2","関連性_S3"]].mean(axis=1)

W_useful = grouped[["有用性_W1","有用性_W2","有用性_W3"]].mean(axis=1)
S_useful = grouped[["有用性_S1","有用性_S2","有用性_S3"]].mean(axis=1)

W_novelty = grouped[["既知性_W1","既知性_W2","既知性_W3"]].mean(axis=1)
S_novelty = grouped[["既知性_S1","既知性_S2","既知性_S3"]].mean(axis=1)

# ===== 差分 =====
diffs = {
    "主題理解": W_main - S_main,
    "関連性":   W_relation - S_relation,
    "有用性":   W_useful - S_useful,
    "新規性":   W_novelty - S_novelty,
}

# ===== Wilcoxon検定（両側・片側） =====
for name, diff in diffs.items():
    stat, p_two = wilcoxon(diff)
    # 片側（積集合優位）→差が正方向
    p_one_s = p_two / 2 if diff.mean() < 0 else 1 - (p_two / 2)
    # 片側（Word2Vec優位）→差が負方向
    p_one_w = p_two / 2 if diff.mean() > 0 else 1 - (p_two / 2)

    print(f"{name}:")
    print(f"  両側検定: stat={stat:.3f}, p={p_two:.4f}")
    print(f"  片側検定（積集合優位）: stat={stat:.3f}, p={p_one_s:.4f}")
    print(f"  片側検定（Word2Vec優位）: stat={stat:.3f}, p={p_one_w:.4f}")
