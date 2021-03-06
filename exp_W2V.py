#! -*- coding:utf-8 -*-
""" Evaluate word2vec models. """
import sys, os, subprocess, codecs, argparse
from numpy import zeros
from sklearn.metrics.pairwise import pairwise_distances
from gensim import models
import Corpus, eval_utils

def join_strings_and_append_to_file(strings, filename):
    """ 
    Join strings in list using comma as delimiter, append to file at
    path provided.
    """

    with open(filename, 'a') as f:
        f.write(','.join(strings)+'\n')

if __name__ == "__main__":
    dsc = ("Évaluer différentes paramétrisations de word2vec "
           "au moyen des données de référence.")
    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('-s', '--exclude_stop', action="store_true",
                        help='Exclure les mots vides des mots-cibles')
    parser.add_argument('corpus', help="Chemin du corpus (fichier texte, une phrase par ligne)")
    parser.add_argument('output', help="Chemin du fichier de résultats (CSV) qui sera produit")
    args = parser.parse_args()

    # Check args
    if os.path.exists(args.output):
        sys.exit('ERREUR: Le fichier {} existe déjà.'.format(args.output))

    # Set path of word2vec
    PATH_W2V = "/usr/local/word2vec/word2vec"

    # Set temporary path for word2vec models
    TMP_PATH_MODEL = "/tmp/W2V_MODEL_TMP.bin"

    # Check that the evaluation data are where they should be
    PATH_REF = 'data/ref_FR.csv'
    if not os.path.isfile(PATH_REF):
        e = "Erreur: le fichier {} n'existe pas.".format(PATH_REF)
        sys.exit(e)

    # Load stop words if necessary
    stopwords = None
    if args.exclude_stop:
        stopwords = set()
        with codecs.open('data/stop_FR.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if len(line) and line[0] != '#':
                    stopwords.add(line)

    # Prepare corpus, compute vocab
    print u'\nLecture du corpus et calcul du vocabulaire...'
    corpus = Corpus.Corpus(args.corpus)
    print u'Terminée. Le corpus contient {} mots.'.format(corpus.size)

    # Select target words
    print u'\nIdentification des mots-cibles...'
    nb_targets = 10000
    targets = []
    for word in corpus.most_freq_words(apply_filters=True, stopwords=stopwords):
        targets.append(word)
        if len(targets) == nb_targets:
            break
    target2id = dict([(w,i) for (i,w) in enumerate(targets)])
    print u'Terminée. {} mots-cibles identifiés.'.format(len(targets))

    # Process evaluation data
    print u'\nLecture des données de référence...'
    ref = eval_utils.process_ref(PATH_REF, target_words=targets)
    nb_rels = sum(len(v) for v in ref['TOUTES'].itervalues())
    if nb_rels == 0:
        sys.exit('ERREUR: Aucune relation extraite.')
    print u'Terminée. {} relations extraites.'.format(nb_rels)

    # Define hyperparameter values to be tested
    model_params = []
    MIN_COUNT = "5" # Default: 5
    for size in ["300", "100"]:
        for win in ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]:
            for cbow in ["0", "1"]:
                for neg in ["10","5","0"]:
                    for sample in ["1e-5","1e-3","0"]:
                        model_params.append((size, win, cbow, neg, sample))

    # Write header in output
    ref_rels = ['QSYN', 'ANTI', 'HYP', 'DRV', 'TOUTES']
    header = ['size', 'win', 'cbow','neg','sample']
    header += ['MAP({})'.format(rel) for rel in ref_rels]
    join_strings_and_append_to_file(header, args.output)     

    # Start experiment
    num_models = len(model_params)
    model_counter = 0
    for (size, win, cbow, neg, sample) in model_params:
        model_counter += 1
        msg = u'\nConstruction du modèle {} de {}...'.format(model_counter,num_models)
        msg += u'\n  - size = {}'.format(size)
        msg += u'\n  - win = {}'.format(win)
        msg += u'\n  - cbow = {}'.format(cbow)
        msg += u'\n  - neg = {}'.format(neg)
        msg += u'\n  - sample = {}'.format(sample)
        print msg

        # Call word2vec, train model, and write
        command = [PATH_W2V, "-train", args.corpus, "-output", TMP_PATH_MODEL]
        command += ["-cbow", cbow] 
        command += ["-size", size]
        command += ["-window", win]
        command += ["-negative",  neg]
        if neg == "0":
            command += ["-hs", "1"]
        else:
            command += ["-hs", "0"]
        command += ["-sample", sample]
        command += ["-threads", "40", "-binary", "1"]
        command += ["-min-count", MIN_COUNT]
        subprocess.call(command)
        # Load model
        print u"\n\nLecture du modèle {}...".format(TMP_PATH_MODEL)
        full_model = models.Word2Vec.load_word2vec_format(TMP_PATH_MODEL, binary=True, 
                                                          unicode_errors='ignore')
        full_model.init_sims(replace=True)  # Saves RAM but the model can't be trained any further.
        print u'Terminée.'
        # Extract vector of target words.
        print "Extraction des vecteurs des mots-cibles..."
        vocab = set(full_model.vocab.keys()) 
        model = zeros((len(targets), int(size)), dtype=float)
        for (t, t_id) in target2id.items():
            if t in vocab:
                model[t_id] = full_model[t]
            else:
                msg = u'ATTENTION : "{}" n\'est pas dans le vocabulaire du modèle.'.format(t)
                msg += u' Son vecteur sera nul.'
                print msg
        print u"Terminée."
        # Dump model from memory
        del full_model
        # Delete the model
        print u"Suppression du modèle {}...".format(TMP_PATH_MODEL)
        subprocess.call(["rm", TMP_PATH_MODEL])
        print u"Terminée."

        # Compute MAP on all data sets
        print u'Évaluation du modèle...'
        dist = pairwise_distances(model, metric='cosine')
        MAP_strings = []
        for rel in ref_rels:
            MAP = eval_utils.compute_MAP_from_dist_mat(dist, ref[rel], target2id)
            MAP_strings.append('{:.4f}'.format(MAP))
        print u'Terminée.'

        # Write results of model evaluation (MAP) 
        param_strings = [size, win, cbow, neg, sample]
        join_strings_and_append_to_file(param_strings + MAP_strings, args.output)     
      

    print u'\n\n\nVoir les résultats dans {}.\n'.format(args.output)
