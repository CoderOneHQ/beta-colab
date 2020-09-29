'''
This is your AGENT. It is technically random agent but this is yours
# PLEASE don't use any additional packages other than those provided below
'''
import time
import random
import numpy as np

class agent:
	def __init__(self, player_num, env):
		self.name = "a bot has no name"  ###### give your bot a name ######
		self.player_num = player_num
		self.env = env


	def give_next_move(self, solid_state):
		'''
		This method is called each time the player needs to choose an 
		action
		solid_state: is a dictionary containing all the information about the board
		''' 

		#transfering a single solid_state
		
		self.board = solid_state["board"] 
		self.done = solid_state["done"]
		self.bombs = solid_state["bombs"]
		self.turn = solid_state["turn"]
		self.player = solid_state["players"][self.player_num-1]


		#############################
		###### Your Code Here #######

		
		actions =[0,1,2,3,4,5]
		action = random.choice(actions)


		#############################
		
		return action
