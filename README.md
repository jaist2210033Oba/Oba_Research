# Oba_Research
このリポジトリは、**Linked Open Data (DBpedia)** と自然言語処理を用いて   学習シナリオを自動生成し、その有効性を機械的指標および統計的分析によって評価するための   Pythonスクリプト群をまとめたものです。


本研究は **Web調べ学習を支援すること** を目的としており、  
初期キーワードから関連概念を探索してシナリオを構築し、  
学習者の主観評価と機械的評価を組み合わせて検証を行います。  

## 各スクリプトの役割
- **シナリオ生成**
  - `sinario_sekisyuu_fil.py` : DBpediaのリンク積集合に基づくシナリオ生成
  - `sinario_Word2Vec.py` : Word2Vecによる意味的関連度に基づくシナリオ生成
- **用語抽出**
  - `TFIDF.scraping_test.py` : Webページをスクレイピングし、MeCabで形態素解析してTF-IDFを算出
  - `in-degree.py` : DBpediaにおける語の入次数を取得
- **シナリオ評価**
  - `Sentence-BERT_test.py` : Sentence-BERTにより主題・副題・流れの一貫性を評価
  - `spearman.analyze.py` : アンケート評価と機械的評価のSpearman相関を算出
  - `analyze_wilcok.py` : Wilcoxon検定でシナリオ生成手法を比較（Word2Vec vs 積集合）

## 必要環境
- Python 3.9 以上
- 主要ライブラリ:
  - SPARQLWrapper
  - gensim
  - scikit-learn
  - sentence-transformers
  - pandas
  - scipy
  - BeautifulSoup4
  - requests
  - MeCab (Pythonバインディング)
