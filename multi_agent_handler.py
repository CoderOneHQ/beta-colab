from bm_multi_env import *
import importlib
import numpy as np
import os
from time import sleep
#import signal
import json
from IPython.display import clear_output

class TimeoutException(Exception):   # Custom exception class
	pass

def timeout_handler(signum, frame):   # Custom signal handler
	raise TimeoutException


#reading the configuration file
confi_json_file = "config.json"
with open ("config.json") as f:
  config_data = json.load(f)



#dyanmically importing random
#module_name = "random_agent_class"
m1 =  importlib.import_module(config_data["agent1"])
m2 = importlib.import_module(config_data["agent2"])




#having a solid_state
solid_state = {}

# Change the behavior of SIGALRM
#signal.signal(signal.SIGALRM, timeout_handler)

# create the bomberman environment
env = Game(5,7)


#os.system('cls')
sleep(0.5)

# set play time
num_episodes = 3
max_turns = 200
timer_each_round = 3


# set agents in play
# available: lookahead_agent, random_agent, flee_agent, monte_carlo_agent
##agent1 = monte_carlo_agent
##agent2 = random_agent
#New way, by adding classes instead of method only
agent1 = m1.agent(1, env)
agent2 = m2.agent (2, env)

win_for_agent1 = 0
win_for_agent2 = 0
winner_json = {}

for i in range(num_episodes):
	turn = 0
	# initialize the map & players
	board, players = env.reset()
	#give the name of the player
	
	env.players[0].name = agent1.name
	env.players[1].name = agent2.name
	# initialize variables
	done = False
	rewards = [0,0] # reward received per turn
	total_rewards = [0,0] # cumulative rewards received
	bomb_timer = env.MAX_TIMER
	bomb_list = [] # a list of bomb objects in play and their properties

	solid_state["players"] = players
	# until game ends
	while not done:
		clear_output(wait=True)
		if turn > max_turns:
			break

		solid_state["board"] = board
		solid_state["done"] = done
		solid_state["bombs"] = bomb_list
		solid_state["turn"] = turn


		# render the game
		env.render(True) 



		'''shhh! These are for future generation of the game.
		print("board:")
		print(board)
		print("env:")
		print(env)
		print("validMoves:")
		print(env.get_valid_actions(solid_state))
		print("---")
		'''




		# This try/except loop ensures that 
		#   you'll catch TimeoutException when it's sent.	

		# get player one's action
		# Your agent only has 3 seconds to make a move
		player_num1 = 1
		p1_action = agent1.give_next_move(solid_state)




		player_num2 = 2
		p2_action = agent2.give_next_move(solid_state)


		# perform action
		actions = [p1_action, p2_action]
		board, done, players, bomb_list = env.step(actions)

		'''
		print(f"\n {agent1.name}: {p1_action}")
		print(f"\n {agent2.name}: {p2_action}")

		print(f"\n Turn: {turn}")
		print(" --------------------")
		print(f" Player 1 score: {players[0].score}")
		print(" --------------------")
		print(f" Player 2 score: {players[1].score}")
		print(" --------------------")
		'''





		turn +=1

		sleep(0.2)

	
	env.render(True) 
	#env.convert_video() # it generates the video
	if players[0].score > players[1].score:
		print(f" Game over. {agent1.name} wins round{i+1}.")
		win_for_agent1 = win_for_agent1 + 1
	elif players[0].score < players[1].score:
		print(f" Game over. {agent2.name} wins round{i+1}.")
		win_for_agent2 = win_for_agent2 + 1
	else:
		print("Game over. It's a tie.")
			#sleep(3)
	
	sleep(3)

	if (i + 1) == num_episodes:
		#this means it is in the last round
		if (win_for_agent1 > win_for_agent2):
			print(f" The winner is: {agent1.name}")
			winner_json["winner"] = config_data["agent1"]
		elif (win_for_agent2 > win_for_agent1):
			print(f" The winner is: {agent2.name}")
			winner_json["winner"] = config_data["agent2"]
		else:
			print("Agents need to play one more time!")
			i = i - 1
		sleep(0.2)


with open('winner.json', 'w') as outfile:
    json.dump(winner_json, outfile)



