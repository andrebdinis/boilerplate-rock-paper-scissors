# HOW TO USE:
# import model
# model_markov = model.MarkovChain(0.9) # instantiate
# model_markov.predict('') # predict without a previous play
# model_markov.predict(prev_play) # predict with a previous play

import random

class MarkovChain():

  def __init__(self, decay=1.0):
    self.matrix = self.create_matrix()
    self.decay = decay
    self.prev_pred = ''

  def create_matrix(self):
    
    keys = ['R', 'P', 'S',
            'RR', 'RP', 'RS',
            'PR', 'PP', 'PS',
            'SR', 'SP', 'SS']

    matrix = {}

    for key in keys:
      matrix[key] = {'R': {'prob': 1/3, 'n_occ': 0},
                     'P': {'prob': 1/3, 'n_occ': 0},
                     'S': {'prob': 1/3, 'n_occ': 0}}
    
    return matrix

  def update_matrix(self, key, prev_play):

    # decays the # of occurrences for each key in the matrix, , i.e. "forgetting" them a bit each time
    for i in self.matrix[key]:
      self.matrix[key][i]['n_occ'] *= self.decay

    # increment the # of occurrences of prev_play in matrix[key]
    self.matrix[key][prev_play]['n_occ'] += 1    # two last key, e.g. [RP][S]: after 'RP', occurs 'S' 
    
    # get total # of occurrences
    total = 0
    for i in self.matrix[key]:
      total += self.matrix[key][i]['n_occ']

    # calculate/update probability matrix after incrementing occurrances
    for i in self.matrix[key]:
      self.matrix[key][i]['prob'] = self.matrix[key][i]['n_occ'] / total

  def predict(self, prev_play=''):

    defeats = { 'R': 'P',
                'P': 'S',
                'S': 'R' }
    pred = ''

    if prev_play == '':
      self.prev_pred = random.choice(['R', 'P', 'S'])
      return self.prev_pred

    key = self.prev_pred + prev_play

    self.update_matrix(key, prev_play)

    probs = self.matrix[key]
    
    max_prob = max( list(probs.values()), key=lambda x: x['prob'] )
    min_prob = min( list(probs.values()), key=lambda x: x['prob'] )
    if max_prob == min_prob:
      pred = random.choice(['R', 'P', 'S'])
    else:
      pred = defeats[ max(probs.items(), key=lambda i: i[1]['prob'])[0] ]

    self.prev_pred = pred
    
    return pred