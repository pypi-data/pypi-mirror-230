def ngram_counts(sentence, n):
    return dict([(tuple(sentence[i:i+n]), sentence[i:i+n].count(sentence[i])) for i in range(len(sentence)-n+1)])

def calculate_bleu(predictions, references):
    total_score = 0
    valid_n_values = 0  # Count of n values that didn't result in count=0

    for n in range(1, 5):  # 1, 2, 3, 4
        clip_count = 0
        count = 0
        for pred, ref in zip(predictions, references):
            pred_counts = ngram_counts(pred.split(), n)
            ref_counts = ngram_counts(ref.split(), n)
            clip_count += sum(min(pred_counts[gram], ref_counts.get(gram, 0)) for gram in pred_counts)
            count += sum(pred_counts.values())
        
        if count != 0:
            total_score += clip_count / count
            valid_n_values += 1

    if valid_n_values == 0:
        return 0
    return total_score / valid_n_values



