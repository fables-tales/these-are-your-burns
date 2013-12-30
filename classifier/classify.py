

def classify(word_list):
    labels = open("labels.txt").read().strip().split("\n")
    result_dict = {}
    for label_line in labels:
        label_line = label_line.split(",")
        label = label_line[0]
        scores = [float(x) for x in label_line[1:]]
        result_dict[label] = scores

    summary_scores = [0,0,0,0,0]

    for word in word_list:
        if word in result_dict.keys():
            scores = result_dict[word]
            for index, score in enumerate(scores):
                summary_scores[index] += score


    for i in xrange(0,len(summary_scores)):
        summary_scores[i] = summary_scores[i] * 1.0 /len(word_list)

    return summary_scores

if __name__ == "__main__":
    f = open("songs/song_1.txt").read().strip().split("\n")

    line_pairs = []
    for i in xrange(1, len(f), 2):
        line_pairs.append(f[i-1].split(" ") + f[i].split(" "))
