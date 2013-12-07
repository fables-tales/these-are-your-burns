if __name__ == "__main__":
    label_file = open("labels.txt", "a")

    song = open("songs/song_1.txt").read().strip().split("\n")


    line_pairs = []
    for i in xrange(1, len(song), 2):
        line_pairs.append(song[i-1].split(" ") + song[i].split(" "))


    for line_pair in line_pairs:
        for word in line_pair:
            print word
            print "the labels are 1 2 3 4 5"
            labels = raw_input(">")
            ticks = [0,0,0,0,0]
            for i in xrange(0,len(ticks)):
                if str(i+1) in labels:
                    ticks[i] = 1

            label_file.write(word + "," + ",".join([str(x) for x in ticks]) + "\n")

            label_file.flush()
