import os
import time
import re
import requests
from bs4 import BeautifulSoup
import MeCab
from collections import Counter
from googlesearch import search
from sklearn.feature_extraction.text import TfidfVectorizer

# 不要語句のリスト
STOPWORDS = {'こと', 'もの', 'これ', 'それ', 'ところ', 'よう', 'ため', 'ほか', '方', '時', '人',
             '場合', '後', '中', '前', '今日', '昨日', '今', '誰', '何', 'など', 'さん', '一つ', 'さまざま', '私たち', '多く', 'PR', '日本', '取り組み'}
NOISEWORDS = {'編集', '表示', '英語版', 'ISBN', '参照', 'ページ', '検索', '記事', 'ヘルプ',
              '履歴', '出典', '目次', 'カテゴリ', '項目', '非表示', 'メニュー', 'ツール', 'ダウンロード', '印刷'}

# URL収集
def fetch_top_urls(query, num_results=15):
    urls = []
    for url in search(query, num_results=num_results + 5):
        if not url.lower().endswith('.pdf'):
            urls.append(url)
        if len(urls) >= num_results:
            break
        time.sleep(1)
    return urls

# HTMLテキスト抽出
def extract_text_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=10)
    res.encoding = 'utf-8'
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    texts = soup.find_all(['p', 'div'])
    content = '\n'.join([t.get_text(strip=True) for t in texts if t.get_text(strip=True)])
    return content

# MeCabトークナイズ（複合名詞対応）
def tokenize_mecab(text):
    tagger = MeCab.Tagger()
    tagger.parse('')
    node = tagger.parseToNode(text)
    words, buffer = [], []

    while node:
        surface = node.surface
        features = node.feature.split(',')

        if features[0] == '名詞' and features[1] not in ['非自立', '代名詞', '数']:
            buffer.append(surface)
        else:
            if buffer:
                compound = ''.join(buffer)
                if is_valid_token(compound):
                    words.append(compound)
                buffer = []
        node = node.next

    if buffer:
        compound = ''.join(buffer)
        if is_valid_token(compound):
            words.append(compound)

    return words

# 有効語の条件（長さ・記号・数字のみを除外）
def is_valid_token(word):
    if len(word) <= 1 or len(word) > 20:
        return False
    if word in STOPWORDS or word in NOISEWORDS:
        return False
    if re.fullmatch(r'\d+|[a-zA-Z]+|[^\w\s]', word):
        return False
    if re.fullmatch(r'[\W_]+', word):
        return False
    return True

# TF-IDF用トークナイザ
def tokenizer_for_tfidf(text):
    return tokenize_mecab(text)

# メイン処理
def main():
    query = input("検索キーワードを入力してください: ").strip()
    focus_words_input = input("注目単語（スペース区切り）を入力してください: ").strip()
    focus_words = focus_words_input.split()

    urls = fetch_top_urls(query)
    corpus = []
    total_counter = Counter()

    for idx, url in enumerate(urls, 1):
        print(f"\n==== [{idx}] {url} ====")
        try:
            text = extract_text_from_url(url)
            corpus.append(text)
            tokens = tokenize_mecab(text)
            total_counter.update(tokens)
        except Exception as e:
            print(f"⚠️ エラー: {e}")
            continue

    # 頻出語ランキング
    print("\n📊 頻出語ランキング Top 30")
    for word, count in total_counter.most_common(30):
        print(f"{word}: {count}回")

    # TF-IDFスコア計算
    vectorizer = TfidfVectorizer(tokenizer=tokenizer_for_tfidf)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    mean_scores = tfidf_matrix.mean(axis=0).A1
    word_score_pairs = list(zip(feature_names, mean_scores))
    word_score_pairs.sort(key=lambda x: x[1], reverse=True)

    print("\n📊 TF-IDF ランキング Top 30")
    for word, score in word_score_pairs[:30]:
        print(f"{word}: {score:.4f}")

    # 注目語の評価（全文に対して直接一致検索）
    print("\n🔍 注目語の評価")
    for fw in focus_words:
        raw_freq = sum(text.count(fw) for text in corpus)
        tfidf = next((score for word, score in word_score_pairs if word == fw), 0.0)
        print(f"{fw}: 出現回数 = {raw_freq}回, TF-IDF = {tfidf:.4f}")

if __name__ == "__main__":
    main()
