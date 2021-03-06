
"""""""""
author: loreznoscottb

script compute fallacy estimation for eaxh scario based on two models:
        
    - Bhatia (see Bhatia, 2017)
    - RAD, an original implementation, authors are Lorenzo Scott Bertolini and Katya Tentori

"""

##############################################

#  Imports

#############################################

from corpora_tools import *
import gensim
import nltk
import re
import os
import math
import seaborn as sns
import numpy as np
import pandas as pd
import string
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import seaborn as sns
import logging

##############################################

#  Methods

#############################################


def cosine_similarity(v1, v2):

    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"

    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y

    return sumxy/math.sqrt(sumxx*sumyy)


def multi_vec(string):

    "does the norm of a vector using numpy, useful for projection and stuff"

    words = nltk.word_tokenize(string)
    v = np.zeros(300, dtype=np.float32)

    for word in words:
        if word not in en_stop:
         v += gn_model.get_vector(word.strip('.1'))  # pandas does not like repetitions...

    return v


##############################################

# Loading data

#############################################

logging.getLogger().setLevel(logging.INFO)

en_stop = nltk.corpus.stopwords.words('english')
punctuation = string.punctuation
subject_n = 38
scenario_n = 82

# Pure stimuli
st = pd.read_excel('/Users/lb540/Documents/uni/data/cnj_fllc/'
                   'stimuli.xlsx')
options = st.values
scenarios = st.columns

# subjects' data (values[x] = subj_x)
data = pd.read_excel('/Users/lb540/Documents/uni/data/cnj_fllc/'
                     'data.xlsx')
# values = data.values
# columns = data.columns

logging.info('loading Google News Vectors...')
# Google News pre trained vectors
gn_model = gensim.models.KeyedVectors.load_word2vec_format('/Users/lb540/Documents/corpora/vectors/'
                                                           'googlenews-vectors-negative300.bin',
                                                           binary=True)
logging.info('done..')
# vocabulary = [word.strip('.1') for word in set(nltk.word_tokenize(str(options+scenarios))) if
#               word not in en_stop and word not in punctuation and word.strip('.1')
#               not in vocabulary]


##############################################

# estimations

#############################################

# BHATIA'S
logging.info('computing Bhatia\'s estimatons..')
cs_values = []
for i in range(0, len(scenarios)):
    txw = (multi_vec(scenarios[i]))/len(nltk.word_tokenize(scenarios[i]))
    v_nfw = (multi_vec(options[0][i]))/len(nltk.word_tokenize(options[0][i]))
    v_fw = (multi_vec(options[1][i]))/len(nltk.word_tokenize(options[1][i]))
    cs_values.append((cosine_similarity(txw, v_nfw), cosine_similarity(txw, v_fw)))

softmax = lambda x : np.exp(x)/np.sum(np.exp(x))
bt_gap = []  # gap as all
bt_fall = []  # algorithm pick
for b in range(len(cs_values)):
    bt_fall.append(round((softmax(cs_values[b])[1]), 3))

logging.info('computing RAD\'s estimations..')
# RAD model
rad_values = []
for i in range(0, len(scenarios)):
    txw = (multi_vec(scenarios[i]))/len(nltk.word_tokenize(scenarios[i]))
    v_nfw = (multi_vec(options[0][i]))/len(nltk.word_tokenize(options[0][i]))
    v_fw = multi_vec(options[1][i].replace(options[0][i], ""))/len(nltk.word_tokenize(options[1][i].replace(options[0][i], "")))

    eh1 = ((cosine_similarity(txw, v_nfw) + 1)/2)
    eh2 = ((cosine_similarity(txw, v_fw) + 1)/2)
    h1h2 = (cosine_similarity((txw + v_nfw), (txw + v_fw)) + 1)/2
    rad_values.append([eh1, eh2, h1h2])

rad_fall = [e[1]*e[2]*(1-e[0]) for e in rad_values]

##############################################

# Plots

#############################################

logging.info('preparing plot..')

sns.set(color_codes=True)
sns.set_style("whitegrid")

# # single plot
#btg = sns.regplot(data['Fallacy percentage'][0:82], rad_fall, color='g')

# double plot
col_name = ['Bhatia prob', 'Rad prob']
mdl_name = ['Bhatia', 'Rad']
x = data['Fallacy percentage'][0:82]
ys = [bt_fall, rad_fall]
color = ['b', 'g']

for e in range(len(mdl_name)):
    y = ys[e]
    plt.subplot(1, 2, (1 + e))
    btg = sns.regplot(y=y, x=x, color=color[e])
    # btg.set_axis_labels("Fallcy percentage", "models estimations")
    if e == 0:
        plt.ylabel('Models\' Estimations', fontsize=20)
    else:
        plt.ylabel('')
    plt.title(mdl_name[e], fontsize=25)
    plt.xlabel('Fallacy Degree', fontsize=20)
    plt.tick_params(labelsize=20)
