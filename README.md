Évaluation de modèles sémantiques distributionnels
==================================================

Ce dossier contient le code et la plupart des ressources nécessaires
pour reproduire l'expérience décrite dans [1].

Code
----

* `exp_AD.py` et `exp_W2V.py` : programmes qui construisent et
  évaluent des modèles distributionnels (analyse distributionnelle et
  word2vec respectivement) sur les données de référence. **N.B.** Le
  programme `exp_AD.py` exige beaucoup de mémoire si le nombre de
  mots-cibles est élevé.

* `Corpus.py` : classe utilisée par `exp_AD.py` et `exp_W2V.py` pour
  identifier les mots-cibles en fonction de leur fréquence dans le
  corpus et d'autres critères. Elle est aussi utilisée pour générer
  les phrases que contient le corpus (dans le cas de `exp_AD.py`).

* `CoocTensor.py` et `CoocMatrix.py` : classes utilisées par
  `exp_AD.py` pour construire des matrices de cooccurrence.

* `eval_utils.py` : fonctions utilisées par `exp_AD.py` et `exp_W2V.py` pour traiter les données de
  référence et calculer les mesures d'évaluation.

* `preprocess_PANACEA_FR.py` : programme qui extrait le contenu textuel
  du corpus français PANACEA et applique différentes opérations de
  prétraitement. 

Ressources
----------

* data/stop_FR.txt (facultatif) : une liste de mots vides, utilisée
  par `exp_AD.py` et `exp_W2V.py` pour identifier les mots-cibles
  (seulement si l'option -s est utilisée). Cette liste a été adaptée
  de celle qu'exploite la version française du stemmer
  [Snowball](http://snowballstem.org/) (cette dernière se trouve
  [ici](http://snowballstem.org/algorithms/french/stop.txt)).

* data/ref_FR.txt : les données de référence, utilisées par
  `exp_AD.py` et `exp_W2V.py` pour évaluer les modèles. Ces données
  ont été extraites du
  [DiCoEnviro](http://olst.ling.umontreal.ca/cgi-bin/dicoenviro/search_enviro.cgi).


Notes
-----

L'expérience décrite dans [1] peut être reproduite de la façon suivante :

1. Obtenir le [corpus monolingue français PANACEA du domaine de
l'environnement](http://catalog.elra.info/product_info.php?products_id=1186&language=fr). Le
dossier contenant les fichiers XML du corpus sera appelé PANACEA_XML
ci-dessous.

2. `preprocess_PANACEA_FR.py -l PANACEA_XML corpus.txt`

3. `exp_AD.py -s corpus.txt res_AD.csv`

4. `exp_W2V.py -s corpus.txt res_W2V.csv`


Les résultats (MAP sur chacune des relations dans les données de
référence en fonction de la paramétrisation du modèle) seront dans
res_AD.csv et res_W2V.csv.

Il faut avoir installé Python et les bibliothèques NumPy, SciPy et
scikit-learn pour Python. 

Pour utiliser `preprocess_PANACEA_FR.py`, il faut avoir installé
[TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/)
ainsi que la bibliothèque
[TreeTaggerWrapper](https://pypi.python.org/pypi/treetaggerwrapper)
pour Python. Installer TreeTagger dans /usr/local (sinon modifier
TAGDIR dans `preprocess_PANACEA_FR.py`).


Pour utiliser `exp_W2V.py`, il faut avoir installé
[word2vec](https://code.google.com/archive/p/word2vec/). Installer
dans /usr/local (sinon modifier PATH_W2V dans `exp_W2V.py`).



Références
----------

[1] Bernier-Colborne, G. et P. Drouin. 2016. Évaluation des modèles
sémantiques distributionnels : le cas de la dérivation syntaxique. In
*Actes de TALN*, Paris, France.
