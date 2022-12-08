import random
from itertools import product # to make combinations of plays
# Doc: https://docs.python.org/3/library/itertools.html
import pprint

# Initialize variables
options = [ 'R', 'P', 'S' ]
win_response = { 'R':'P', 'P':'S', 'S':'R' }
one_combinations, two_combinations, thr_combinations = {}, {}, {}
combinations_history, my_combinations_history = {}, {}
games_history = []
strategies_options = ['s1', 's2', 's3', 's4', 's5', 's6', 's7']
strategy = 's1'
strategies_used = dict()
strategies_outcomes = dict()

################## STRATEGIES IMPLEMENTED ##################
# s1 - Last from Three Most Played (Markov chain of length 3),
# s2 - Last from Two Most Played (Markov chain of length 2),
# s3 - Most Played In Last Ten Of My Plays List,
# s4 - Previous Play Of My Plays List,
# s5 - Last from Two Most Played Of My Plays List (Markov chain of length 2),
# s6 - One Most Played (Markov chain of length 1),
# s7 - Random.

################## TESTS ##################
# Bots: Abbey-Kris-Mrugesh-Quincy
# BEST: 82-99-99-99% win rate
# WORST: 70-98-97-97% win rate

def player(prev_play, opponent_history=[]):
  global combinations_history
  global my_combinations_history
  global games_history
  global strategies_options
  global strategy # current strategy
  global strategies_used # counts only the used strategies
  global strategies_outcomes # the final outcome of wins/losses/ties of the strategies
  new_game = dict()
  
  # if no previous play was made, then is a new match (against a new player)
  if not prev_play:
    # reset histories
    combinations_history = resetCombinationsHistory(combinations_history)
    my_combinations_history = resetCombinationsHistory(my_combinations_history)
    opponent_history.clear()
    games_history.clear()
    
    # reset strategies
    strategies_used.clear()
    strategies_outcomes = resetStrategiesOutcomes(strategies_outcomes)
    strategy = 's7' # my turn to play the first move (play random)
    
    # guess opponent's next play
    next_play_guess = applyStrategyToGuessNextPlay(strategy, opponent_history)

  else:
    # a match (set of games) is ongoing
    
    # save opponent's previous play
    opponent_history.append(prev_play)
    length = len(opponent_history)
    next_play_guess = ''
    
    # Compute games history information
    games_history[-1]['bot'] = prev_play[:] # save opponent's previous play in previous game
    games_history[-1]['result'] = computeGameResult(games_history[-1])
    
    # Compute strategies outcomes
    previous_strategy = games_history[-1]['strategy'][:]
    if games_history[-1]['result'] == 'me': strategies_outcomes[ previous_strategy ] += 1
    elif games_history[-1]['result'] == 'tie': strategies_outcomes[ previous_strategy ] += 0
    elif games_history[-1]['result'] == 'bot': strategies_outcomes[ previous_strategy ] -= 2

    # if opponent has made 1 or 2 plays/moves
    if length == 1 or length == 2:
      strategy = random.choice(['s6', 's7']) # predict opponent's next play
      next_play_guess = applyStrategyToGuessNextPlay(strategy, opponent_history)
  
    # if opponent has made 3 plays/moves (at least)
    elif length >= 3:
      # set 's1' as default strategy
      if length == 3: strategy = 's1'
  
      # change strategy if beginning to lose games
      start_from = 1 # start running from a specified game
      update_pace = 1 # run at every multiple of the chosen number (if 2, then run at games 2, 4, 6, 8, etc.)
      if length >= start_from and length % update_pace == 0:
        n_games = 10
        last_n_games_results = getGamesResults(games_history[-n_games:])
        losses = last_n_games_results['bot']
        if losses > 1:
          strategy = getBestStrategyFromStrategiesOutcomes(strategy)
  
      # apply current strategy to guess opponent's next play
      next_play_guess = applyStrategyToGuessNextPlay(strategy, opponent_history)
  
      # increment my combinations history's last moves
      updateMyCombinationsHistory()
      
      # print strategies statistics
      if length == 999:
        printStrategiesStats()
        # writeGamesHistoryToFile(games_history) # save games history in .txt file

  # process my move and save game
  my_move = winningPlay(next_play_guess)
  new_game['me'] = my_move[:]
  new_game['id'] = len(games_history)
  new_game['strategy'] = strategy[:]
  games_history.append(new_game)
  
  return my_move



################## STRATEGIES FUNCTIONS ##################
  
# s1: CHOOSE LAST FROM THREE MOST PLAYED
def applyStrategyLastFromThreeMostPlayed(last_two, combinations_history):      
  most_thr = getMostPlayedCombinationsList(last_two, combinations_history)
  next_play_guess = most_thr[0][-1]
  return next_play_guess

# s2: CHOOSE LAST FROM TWO MOST PLAYED
def applyStrategyLastFromTwoMostPlayed(last_one, combinations_history):  
  most_two = getMostPlayedCombinationsList(last_one, combinations_history)
  next_play_guess = most_two[0][-1]
  return next_play_guess

# s3: CHOOSE MOST PLAYED IN LAST TEN OF MY PLAYS LIST
def applyStrategyMostPlayedInLastTenOfMyPlaysList(games_history):
  my_plays_lst = getMyPlaysList(games_history)
  last_nine = my_plays_lst[-9:]
  most_played = max(set(last_nine), key=last_nine.count)
  next_play_guess = invertPlay(most_played[:]) # opponent chooses to play against the move he predicted
  return next_play_guess

# s4: CHOOSE PREVIOUS PLAY OF MY PLAYS LIST
def applyStrategyPreviousPlayOfMyPlaysList(prev_play):
  next_play_guess = invertPlay(prev_play) # opponent chooses to play against the move he predicted
  return next_play_guess

# s5: CHOOSE LAST FROM TWO MOST PLAYED OF MY COMBINATIONS HISTORY
def applyStrategyLastFromTwoMostPlayedOfMyPlaysList(last_one, my_combinations_history):
  most_two = getMostPlayedCombinationsList(last_one, my_combinations_history)
  next_play_guess = invertPlay(most_two[0][-1])
  return next_play_guess

# s6: CHOOSE ONE MOST PLAYED
def applyStrategyLastFromOneMostPlayed(combinations_history):
  most_one = getMostPlayedCombinationsList('', combinations_history)
  next_play_guess = most_one[0][-1]
  return next_play_guess
  
# s7: CHOOSE RANDOM  
def applyStrategyRandom():
  next_play_guess = randomPlay()
  return next_play_guess

# MAIN STRATEGY APPLIER FUNCTION
def applyStrategyToGuessNextPlay(strategy, opponent_history):
  # get the last three plays/moves from opponent's history
  last_one = ''
  last_two = ''
  last_thr = ''
  length = len(opponent_history)

  if length >= 1:
    last_one = opponent_history[-1] # 'R'
    combinations_history[last_one] += 1
  if length >= 2:
    last_two = joinStringList(opponent_history[-2:]) # 'RR'
    combinations_history[last_two] += 1
  if length >= 3:
    last_thr = joinStringList(opponent_history[-3:]) # 'RRR'
    combinations_history[last_thr] += 1
  
  next_play_guess = ''
  if strategy == 's1': #          CHOOSE LAST FROM THREE MOST PLAYED
    next_play_guess = applyStrategyLastFromThreeMostPlayed(last_two, combinations_history)
    processStrategyUsed('s1')
      
  elif strategy == 's2': #        CHOOSE LAST FROM TWO MOST PLAYED
    next_play_guess = applyStrategyLastFromTwoMostPlayed(last_one, combinations_history)
    processStrategyUsed('s2')
      
  elif strategy == 's3': #        CHOOSE MOST PLAYED IN LAST TEN OF MY PLAYS LIST
    next_play_guess = applyStrategyMostPlayedInLastTenOfMyPlaysList(games_history)
    processStrategyUsed('s3')
      
  elif strategy == 's4': #        CHOOSE PREVIOUS PLAY OF MY PLAYS LIST
    next_play_guess = applyStrategyPreviousPlayOfMyPlaysList(games_history[-1]['me'])
    processStrategyUsed('s4')
      
  elif strategy == 's5': #        CHOOSE LAST FROM TWO MOST PLAYED OF MY PLAYS LIST
    next_play_guess = applyStrategyLastFromTwoMostPlayedOfMyPlaysList(games_history[-1]['me'], my_combinations_history)
    processStrategyUsed('s5')
      
  elif strategy == 's6': #                        CHOOSE LAST FROM ONE MOST PLAYED
    next_play_guess = applyStrategyLastFromOneMostPlayed(combinations_history)
    processStrategyUsed('s6')
      
  elif strategy == 's7': #                        CHOOSE RANDOM
    next_play_guess = applyStrategyRandom()
    processStrategyUsed('s7')

  return next_play_guess


def processStrategyUsed(strategy):
  if strategies_used.get(strategy): strategies_used[strategy] += 1
  else: strategies_used[strategy] = 1

def getBestStrategyFromStrategiesOutcomes(strategy):
  best_strategy = max(strategies_outcomes, key=strategies_outcomes.get)
  if best_strategy == strategy:
    outcomes = strategies_outcomes.copy() # make a copy of strategies outcomes
    outcomes[strategy] = -1 # "nullify" the best strategy, which is the one already loosing
    best_strategy = max(outcomes, key=outcomes.get) # get the next best strategy
  strategy = best_strategy[:]
  return strategy



################## AUXILIARY FUNCTIONS ##################

def joinStringList(lst):
  # return "".join(lst)
  str = ''
  for value in lst:
    str += value
  return str

def initializeStrategiesOutcomes():
  return { s: 0 for s in strategies_options }
strategies_outcomes = initializeStrategiesOutcomes()

def resetStrategiesOutcomes(strategies_outcomes):
  return resetDictionary(strategies_outcomes)

def makeCombinationsHistory(comb_units, comb_length=1):
  # comb_units may be a list of strings, or a string with several characters
  combinations = dict()
  if comb_length <= 0: return combinations
  lsts_of_split_combinations = [ list(value) for value in product(comb_units, repeat=comb_length) ]
  for lst in lsts_of_split_combinations:
    combinations[ joinStringList(lst) ] = 0 # [["R", "P", "S"], ...] -> { "RPS": 0, ... }
  return combinations

one_combinations = makeCombinationsHistory(options, 1) # {'R': 0, 'P': 0, 'S': 0}
two_combinations = makeCombinationsHistory(options, 2) # {'RR': 0, ..., 'SS': 0}
thr_combinations = makeCombinationsHistory(options, 3) # {'RRR': 0, ..., 'SSS': 0}
combinations_history = { **one_combinations, **two_combinations, **thr_combinations } # {'R': 0, ..., 'SSS': 0}
my_combinations_history = { **one_combinations, **two_combinations, **thr_combinations }

def updateMyCombinationsHistory():
  my_last_one = games_history[-1]['me']
  my_last_two = games_history[-2]['me'] + games_history[-1]['me']
  my_last_thr = games_history[-3]['me'] + games_history[-2]['me'] + games_history[-1]['me']
  my_combinations_history[my_last_one] += 1
  my_combinations_history[my_last_two] += 1
  my_combinations_history[my_last_thr] += 1

def resetDictionary(dictionary):
  return { key: 0 for key in dictionary }

def resetCombinationsHistory(combs_dict):
  return resetDictionary(combs_dict)

def getCombinationsHistory(combs_dict, plays_lst):
  plays_history = {
    play: combs_dict[play]
    for play in plays_lst if play in combs_dict
  }
  return plays_history

def makePotentialCombinations(previous_plays_str, possible_plays_lst):
  potential_combs = list()
  for possible_next_play in possible_plays_lst:
    potential_combs.append( previous_plays_str + possible_next_play )
  return potential_combs

def getMaximumCombinationsFromHistory(plays_history_dict):
  # find the most played combination and get its maximum count value
  max_count = max(plays_history_dict.values()) # int
  # return all most played combinations (if several exist with the same maximum count value)
  return [ play for play,count in plays_history_dict.items() if count == max_count ] # list

def getMostPlayedCombinationsList(plays_str, combs_dict):
  # make potential combinations
  potential_plays = makePotentialCombinations(plays_str, options) # list of n-chars potential combs
  # get the potential plays's history (the # of how many times they were played)
  potential_plays_history = getCombinationsHistory(combs_dict, potential_plays) # dict
  # find all most played combinations (if several exist with the same maximum count value)
  most_played_combs_lst = getMaximumCombinationsFromHistory(potential_plays_history) # list
  return most_played_combs_lst

def pickCombinationFromList(most_plays_lst):
  return most_plays_lst[ random.randint(0, len(most_plays_lst)-1) ]



def computeGameResult(game_dict):
  result = ''
  me = game_dict['me']
  bot = game_dict['bot']
  if me == bot:
    result = 'tie'
  elif (me == 'R' and bot == 'S') or (me == 'P' and bot == 'R') or (me == 'S' and bot == 'P'):
    result = 'me'
  elif (bot == 'R' and me == 'S') or (bot == 'P' and me == 'R') or (bot == 'S' and me == 'P'):
    result = 'bot'
  return result

def getGamesResults(games_lst):
  games_results = dict()
  me, bot, tie = 0, 0, 0
  for game in games_lst:
    if game['result'] == 'me': me += 1; continue
    if game['result'] == 'bot': bot += 1; continue
    if game['result'] == 'tie': tie += 1; continue
  games_results['me'] = me
  games_results['bot'] = bot
  games_results['tie'] = tie
  return games_results

def getMyPlaysList(games_lst):
  return [ game['me'] for game in games_lst ]



def winningPlay(opponent_play):
  return win_response[opponent_play]

def invertPlay(opponent_play):
  return win_response[opponent_play]

def randomPlay():
  return options[random.randint(0,2)]
  # return random.choice(options)

def printStrategiesStats():
  print('\nStrategies used:')
  pprint.pprint(strategies_used, sort_dicts=True)
  b = strategies_outcomes.copy()
  print('\nStrategies scores:')
  pprint.pprint(b, sort_dicts=True)
  print()

def writeGamesHistoryToFile(games_history):
    file = open('./games_history.txt', 'w') # modes: 'a' means 'append', 'w' means 'overwrite'
    file.write('TITLE: 00\n' + str(games_history) + "\n"*20)
    file.close()