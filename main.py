from distance import distance_beats
import cluster
import pickle
import glob
import random
from markov import MarkovModel
import echonest.remix.audio as audio
from concatenate_mp3 import generate

SAMPLING_STEP = 2
K = 50
NGRAM = 4

def get_cluster_index(beat, clusters):
    closest_cluster = 0
    closest_distance = distance_beats(beat, clusters[0].centroid)
    for i in range(len(clusters)):
        distance = distance_beats(beat, clusters[i].centroid)
        if distance < closest_distance:
            closest_cluster = i
            closest_distance = distance
    return closest_cluster

def get_beats_back(index, clusters):
    c = clusters[index]
    return c[random.randint(0, len(c) - 1)]

def main():

    #### We can't do this for multiple songs.
    songs = glob.glob("songs/*.mp3")
    filename = generate(songs)
    beats = []
    audiofile = audio.LocalAudioFile(filename)
    beats = audiofile.analysis.beats
    print "Number of beats %s" % len(beats)

    samples = beats[::SAMPLING_STEP]
    print "Number of samples to build cluster model %s" % len(samples)
    cl = cluster.KMeansClustering(samples, distance_beats)
    clusters = cl.getclusters(K)
    print "Clustering completed"

    for c in clusters:
        c.centroid = None
    pickle.dump(clusters, open("clustering.c", "wb"))
    print "Pickled Cluster Model"

    for c in clusters:
        c.centroid = cluster.centroid(c)
    print "Reset the centroids"

    training_input = []
    for beat in beats:
        training_input.append(get_cluster_index(beat, clusters))
    print("Training markovModel")
    markov_model = MarkovModel()
    markov_model.learn_ngram_distribution(training_input, NGRAM)

    #### We should have his function as iterator.
    print "Generating bunch of music"
    output_list = markov_model.generate_a_bunch_of_text(len(training_input))
    generated_beats = audio.AudioQuantumList()
    print "Coming back to beats"
    for index in output_list:
        generated_beats.append(get_beats_back(index, clusters))

    #### We can't do this for multiple songs.
    print "Saving an Amazing Song"
    out = audio.getpieces(audiofile, generated_beats)
    out.encode("bunch_of_music.wav")


if __name__ == "__main__":
    main()
