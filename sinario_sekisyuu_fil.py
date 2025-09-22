from SPARQLWrapper import SPARQLWrapper, JSON
import re
import random

sparql = SPARQLWrapper("http://ja.dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

def is_valid_link(link):
    if re.match(r"^(?:[0-9]{4}|昭和|平成|令和)[0-9]{0,2}(年|年度)?$", link):
        return False
    if re.match(r"^[0-9]{1,2}月[0-9]{1,2}日$", link):
        return False
    if re.match(r"^[0-9]{4}年[0-9]{1,2}月(.*)?$", link):
        return False
    if re.match(r"^([0-9]{3,4}|昭和|平成|令和)[0-9]{0,2}年代$", link):
        return False
    if re.match(r"^[0-9]{1,2}月$", link):
        return False
    if re.search(r"[0-9]{4}年", link):
        return False
    return True

def get_links(keyword):
    uri = f"http://ja.dbpedia.org/resource/{keyword}"
    print(f"[DEBUG] SPARQL対象URI: {uri}")
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?link WHERE {{
        <{uri}> dbo:wikiPageWikiLink ?link .
        FILTER(STRSTARTS(STR(?link), "http://ja.dbpedia.org/resource/"))
    }}
    """
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        all_links = sorted(set(result["link"]["value"].split("/")[-1] for result in bindings))
        filtered_links = [link for link in all_links if is_valid_link(link)]
        if len(filtered_links) > 300:
            print(f"[INFO] 「{keyword}」は出次数が多いため除外（{len(filtered_links)} 件）")
            return []
        print(f"[INFO] 「{keyword}」から {len(filtered_links)} 件の有効リンクを取得しました（全 {len(all_links)} 件中）")
        return filtered_links
    except Exception as e:
        print(f"[ERROR] SPARQLクエリ失敗: {e}")
        return []

def score_by_intersection(link_sets, candidate_links):
    return [len(links & candidate_links) for links in link_sets]

def explore_single_scenario(k1, k2, c3_word, k1_links, k2_links, max_depth):
    visited = {k1, k2, c3_word}
    c3_links = set(get_links(c3_word))
    path = [
        (1, k1, 0, len(k1_links)),
        (2, k2, 0, len(k2_links)),
        (3, c3_word, 0, len(c3_links))
    ]
    logs = []
    current_word = c3_word
    link_history = [k1_links, k2_links, c3_links]

    for depth in range(4, max_depth + 1):
        current_links = get_links(current_word)
        candidates = []

        for link in current_links:
            if link in visited:
                continue
            link_links = set(get_links(link))
            scores = score_by_intersection(link_history, link_links)
            total_score = sum(scores)
            candidates.append((link, total_score, scores, len(link_links), link_links))

        if not candidates:
            break

        candidates.sort(key=lambda x: -x[1])
        log = [f"[候補表示] 深さ{depth}:"]
        for word, total, scores, link_size, _ in candidates[:10]:
            score_text = ", ".join([f"k{i+1}={s}" for i, s in enumerate(scores)])
            log.append(f" - {word}: Total={total}, {score_text}, 出次数={link_size}")
        logs.append("\n".join(log))

        next_word = candidates[0][0]
        next_score = candidates[0][1]
        next_link_size = candidates[0][3]
        path.append((depth, next_word, next_score, next_link_size))
        visited.add(next_word)
        current_word = next_word
        link_history.append(set(get_links(current_word)))

    return path, logs

def run_interactive_exploration():
    k1 = input("初期キーワードを入力してください: ").strip()
    k1_links_raw = get_links(k1)
    k1_links = set(k1_links_raw)

    if not k1_links_raw:
        print("[ERROR] 初期キーワードにリンクする語が取得できませんでした。")
        return

    k1_links_sample = random.sample(k1_links_raw, min(20, len(k1_links_raw)))

    print(f"\n「{k1}」にリンクしている関連語（候補・ランダム順）:")
    for i, word in enumerate(k1_links_sample):
        print(f"{i}: {word}")

    second_input = input("\n第二キーワードを選んでください（番号 or 任意の語）: ").strip()

    if second_input.isdigit() and int(second_input) < len(k1_links_sample):
        idx = int(second_input)
        k2 = k1_links_sample[idx]
        print(f"\n第二キーワードに「{k2}」を選びました（候補から選択）\n")
    else:
        k2 = second_input
        print(f"\n第二キーワードに「{k2}」を選びました（任意入力）\n")

    k2_links = set(get_links(k2))
    candidates = []
    for link in k2_links:
        if link in {k1, k2}:
            continue
        link_links = set(get_links(link))
        score1 = len(k1_links & link_links)
        score2 = len(k2_links & link_links)
        total_score = score1 + score2
        candidates.append((link, total_score))

    top_candidates = sorted(candidates, key=lambda x: -x[1])[:3]
    all_scenarios_output = []
    all_logs_output = []

    for i, (c3_word, _) in enumerate(top_candidates):
        path, logs = explore_single_scenario(k1, k2, c3_word, k1_links, k2_links, max_depth=7)

        scenario_lines = [f"[シナリオ{i+1}]"]
        for depth, word, score, link_size in path:
            if depth == 1:
                scenario_lines.append(f"1: {word}　（スコア={score}, 出次数={link_size}）")
            elif depth == 2:
                scenario_lines.append(f"2: {word}　（スコア={score}, 出次数={link_size}）")
            else:
                scenario_lines.append(f"{depth}: {word}　（スコア={score}, 出次数={link_size}）")

        all_scenarios_output.append("\n".join(scenario_lines))
        all_logs_output.append("\n".join(logs))

    print("\n===== シナリオ一覧 =====\n")
    for scenario_output in all_scenarios_output:
        print(scenario_output)
        print()

    print("\n===== 候補スコアログ =====\n")
    for i, logs_output in enumerate(all_logs_output):
        print(f"[シナリオ{i+1} 候補スコアログ]")
        print(logs_output)
        print()

if __name__ == "__main__":
    run_interactive_exploration()
