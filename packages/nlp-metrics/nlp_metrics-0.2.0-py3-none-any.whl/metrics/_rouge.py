def ngram_counts(sentence, n):
    return dict([(tuple(sentence[i:i+n]), sentence[i:i+n].count(sentence[i])) for i in range(len(sentence)-n+1)])

def rouge_n(pred, ref, n):
    pred_counts = ngram_counts(pred.split(), n)
    ref_counts = ngram_counts(ref.split(), n)
    overlap = sum(min(pred_counts[gram], ref_counts.get(gram, 0)) for gram in pred_counts)
    return overlap / float(len(pred.split()) - n + 1)

def longest_common_subsequence(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n+1) for _ in range(m+1)]
    
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

def rouge_l(pred, ref):
    lcs = longest_common_subsequence(pred.split(), ref.split())
    return lcs / float(len(ref.split()))

def calculate_rouge(predictions, references):
    total_score = 0
    valid_metrics = 0  # Number of metrics that didn't result in an exception
    
    for n in range(1, 5):  # 1, 2, 3, 4
        try:
            score = sum(rouge_n(pred, ref, n) for pred, ref in zip(predictions, references)) / len(predictions)
            total_score += score
            valid_metrics += 1
        except Exception as e:
            print(f"Error calculating ROUGE-{n}: {e}")

    try:
        score_l = sum(rouge_l(pred, ref) for pred, ref in zip(predictions, references)) / len(predictions)
        total_score += score_l
        valid_metrics += 1
    except Exception as e:
        print(f"Error calculating ROUGE-L: {e}")

    if valid_metrics == 0:
        return 0
    return total_score / valid_metrics


