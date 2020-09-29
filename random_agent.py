'''
RANDOM AGENT
'''
import time
import random

class agent:
	def __init__(self, player_num, env):
		self.name = "random bot"
		self.player_num = player_num
		self.env = env
		'''
		 This might need to be added in future
				# This is the case if the player wants to decide on some actions before 
				#the start of the game
				self.board = solid_state["board"] 
				self.done = solid_state["done"]
				self.bombs = solid_state["bombs"]
				self.turn = solid_state["turn"]
				self.player = solid_state["players"][self.player_num-1]

		'''


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

		
		#actions = [0,1,2,3,4]
		actions =[0,1,2,3,4,5]
		action = random.choice(actions)
		
		#I want to delay more than half of the times
		#random.seed(1)
		waitTime = 1 + (3*random.random())
		##waitTime = 2
		#time.sleep(waitTime)

		return action
