'''
MULTIPLAYER ROOK ENVIRONMENT
without recoding function due to compatibility
'''

from time import sleep
import datetime
import math
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import copy
import os
import subprocess
import glob
import json


IMAGE_DIR = 'img/'

def convert_to_rgba(img):
    if img.shape[2] == 3:
        # convert img from RGB to RGBA
        b_channel, g_channel, r_channel = cv2.split(img)
        alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype)
        img = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
        #cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

# load images
img_empty = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'empty.png'))
img_p1 = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'p1.png'))
img_p2 = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'p2.png'))
img_bomb = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'bomb.png'))
img_exploding_bomb = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'exploding_bomb.png'))
img_hard_block = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'hard_block.png'))
img_soft_block = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'soft_block.png'))
img_exploding_tile = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'exploding_tile.png'))
img_wall = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_mid.png'))
img_banner_wall = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_banner_blue.png'))
img_wall_mid = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_mid.png'))
img_wall_top_mid = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_top_mid.png'))
img_wall_left = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_mid_left.png'))
img_wall_right = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_mid_right.png'))
img_wall_bot = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_bot.png'))
img_wall_side_front_left = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_front_left.png'))
img_wall_side_front_right = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_front_right.png'))
img_wall_top_left = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_top_left.png'))
img_wall_top_right = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'wall_side_top_right.png'))

# map labels to images
dict_img = {
    0: img_empty,
    1: img_p1,
    2: img_p2,
    3: img_soft_block,
    4: img_hard_block,
    5: img_bomb,
    6: img_bomb,
    7: img_bomb,
    8: img_exploding_bomb,
    9: img_exploding_tile
}

# map rewards
d_rewards = {
    'DESTROY_BLOCK': 1,
    'INVALID_MOVE': -10,
    'LOSE_GAME': -100,
    'WIN_GAME': 100,
}

actions = ['none','left','right','up','down','bomb']
action_id = [0,1,2,3,4,5]
d_actions = dict(zip(actions,action_id))

class bcolors:
    RED= '\u001b[31m'
    GREEN= '\u001b[32m'
    YELLOW= '\u001b[33m'
    BLUE='\u001b[34m'
    MAGENTA= '\u001b[35m'
    CYAN= '\u001b[36m'
    RESET= '\u001b[0m'

class actions:
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    BOMB = 5

# define tile type
class Tile():

    # Empty = 0
    # Player 1 = 

    def __init__(self, t_type, x_p, y_p):
        self.type = t_type 
        self.x_p = x_p # x position
        self.y_p = y_p # y position

# stores bomb's timer & position
class Bomb():

    def __init__(self, position, tiles_in_range, player=0, max_timer=5):
        self.timer = max_timer
        self.position = position
        self.owned_by = player
        self.recently_exploded = False
        self.tiles_in_range = tiles_in_range

    def update_timer(self):
        self.timer -= 1

    def explode(self):
        self.recently_exploded = True

    def clear(self):
        self.recently_exploded = False

# define behavior of player e.g. powerups, score
class Player():

    def __init__(self, number, starting_position, max_bombs):
        self.number = number
        self.position = starting_position
        self.prev_position = starting_position
        self.bombs = []
        self.num_bombs = max_bombs
        self.score = 0
        self.name = "noName"

    def update_score(self, reward):
        '''
        reward system:
        +1 destroy block
        -10 invalid move
        -1000 lose game
        +100 win game
        '''
        self.score += reward

# defines the Rook environment
class Game():

    # environment attributes
    MAX_BOMBS = 1
    MAX_TIMER = 5 # number of steps before bomb explodes

    # dictionary of board labels
    BOARD_DICT = {'empty':0,'player1':1, 'player2':2,'soft_block':3,'hard_block':4,
    'bomb':5,'p1_on_bomb':6, 'p2_on_bomb':7, 'exploding_bomb':8, 'exploding_tile':9}

    # dictionary of rewards
    REWARDS_DICT = {'destroy_blocks':10, 'invalid_move':-1, 'lose':-45}

    PLAYER_LIST = ['player1','player2']
    ON_BOMB_LIST = ['p1_on_bomb','p2_on_bomb']

    # define movement patterns for each action
    ACTIONS_DICT = {0:(0,0),5:(0,0),1:(0,-1),2:(0,1),3:(-1,0),4:(1,0)}

    def __init__(self,rows=11,cols=13):
        self.rows=rows
        self.cols=cols
        self.turn_i = 0
        confi_json_file = "config.json"
        with open ("config.json") as f:
            self.config_data = json.load(f)



    def get_valid_actions(self, current_state):
        '''
        Armin
        This methods takes a state, in dict format and returns the
        list of valid actions
        '''
        board = current_state["board"] 
        done = current_state["done"]
        bombs = current_state["bombs"]
        turn = current_state["turn"]
        players = current_state["players"]
    


        validAllActions = []
        players = current_state["players"]
        for x in range(len(players)):
            validAofPlayer = []           
            player = players[x]

            # get player reference id's for the map
            if player.number == 0:
                player_id = 1
                player_on_bomb_id = 6
            else:
                player_id = 2
                player_on_bomb_id = 7


            ### find valid moves
            # get current location of agent
            curr_pos = np.where(board == player_id)
            if curr_pos[0].size==0 and curr_pos[1].size==0:
                # if player couldn't be found, check if the player is on a bomb
                curr_pos = np.where(board == player_on_bomb_id)

            # check if there is a bomb on the map

            bomb_pos = np.where(board == self.BOARD_DICT['bomb'])
            if bomb_pos[0].size==0 and bomb_pos[1].size==0:
                bomb_pos = np.where(board == self.BOARD_DICT['p1_on_bomb'])
            if bomb_pos[0].size==0 and bomb_pos[1].size==0:
                bomb_pos = np.where(board == self.BOARD_DICT['p2_on_bomb'])
         
            # get surrounding tiles
            tile_up = (curr_pos[0]-1,curr_pos[1])
            tile_down = (curr_pos[0]+1,curr_pos[1])
            tile_left = (curr_pos[0],curr_pos[1]-1)
            tile_right = (curr_pos[0],curr_pos[1]+1)

            surrounding_tiles = [tile_up, tile_down, tile_left, tile_right]

            # exclude tiles that cross the border of the board
            tiles_to_remove = []
            for tile in surrounding_tiles:
                if tile[0] < 0 or tile[1] < 0 or tile[0] >= self.rows or tile[1] >= self.cols:
                    tiles_to_remove.append(tile)

            for tile in tiles_to_remove:
                surrounding_tiles.remove(tile)

            # find list of empty tiles
            empty_tiles = []
            for tile in surrounding_tiles:
                if board[tile] == 0:
                    empty_tiles.append(tile)

            all_actions = [d_actions['up'],d_actions['down'],d_actions['left'],d_actions['right'],d_actions['none'],d_actions['bomb']]

            valid_actions = [d_actions['none']]
            # get valid moves
            for tile in empty_tiles:
                if tile == tile_up:
                    valid_actions.append(d_actions['up'])
                elif tile == tile_down:
                    valid_actions.append(d_actions['down'])
                elif tile == tile_left:
                    valid_actions.append(d_actions['left'])
                elif tile == tile_right:
                    valid_actions.append(d_actions['right'])

            valid_move_actions = valid_actions
            
            if bomb_pos[0].size==0 and bomb_pos[1].size==0:
                valid_actions.append(d_actions['bomb'])
                is_bomb = False
            else:
                is_bomb = True


            '''
            # calculate best next move
            scores = dict(zip(valid_actions, [score_move(state, action, curr_pos, bomb_timer) for action in valid_actions]))

            # Get a list of moves that maximize the heuristic
            max_actions = [key for key in scores.keys() if scores[key] == max(scores.values())]
            if max_actions:
                action = random.choice(max_actions)
            elif valid_move_actions:
                action = random.choice(valid_move_actions)
            else:
                action = random.choice(all_actions)
            '''
            validAllActions.append(valid_move_actions)

        return validAllActions

    '''def generate_validActions(self, current_state):
        validAllActions = []
        players = current_state["players"]
        for x in range(len(players)):
            validAofPlayer = []
            player = players[x]
            for action in self.ACTIONS_DICT.keys():
                new_position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[action],player.prev_position)])
                if self.check_if_valid(action, player.prev_position, new_position):
                    validAofPlayer.append(action)
            validAllActions.append(validAofPlayer)


        return validAllActions
'''
    def next_state(self, old_state, player_actions):
        """
        Armin
        This method is used to help the agent development. 
        With the help this method, agents can easily find out what is the 
        next state after playing the given actions
    
        Input parameter:
        old_state: This is a dictionary of a state. It is in a format of solid_state
        player_actions: This is the list of players' actions, it is identical to the 
        input of the step method. 
        """
        new_state = copy.deepcopy(old_state)

        players = new_state["players"]
        board = new_state["board"] 
        done = new_state["done"]
        bombs = new_state["bombs"]
        turn = new_state["turn"]


        rewards = np.zeros((len(players),1)) # rewards assigned this turn
        bomb_list = [] # populate list of bombs to return to players

        # get player's new positions
        for player in players:
            # store current position before next move
            player.prev_position = player.position 
            # update players new position
            #player.position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[player_actions[player.number]],player.prev_position)])

            # clear any recent bombs
            for bomb in player.bombs:
                if bomb.recently_exploded == True:
                    self.state_clear_bomb(bomb, board)
                    del bomb # don't think this works?
                    player.bombs = [] # will need to fix this for when players have multiple bombs

            # get player's action
            action = player_actions[player.number]
            # get player's new position if action is taken
            new_position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[player_actions[player.number]],player.prev_position)])

            if self.state_check_if_valid(action, player.prev_position, new_position, board):
                player.position = new_position # valid move, so update player's position
                if action == actions.BOMB:
                    if player.num_bombs > 0:
                        player.bombs.append(Bomb(player.position, self.get_tiles_in_range(player.position), player.number, self.MAX_TIMER)) # create a bomb instance
                        player.num_bombs -= 1 # one less bomb available for the player
                        board[player.position] = self.BOARD_DICT[self.ON_BOMB_LIST[player.number]] # place bomb on map
                elif action == actions.NONE:
                    pass
                else:
                    # move
                    board[player.position] = self.BOARD_DICT[self.PLAYER_LIST[player.number]]

                    if not board[player.prev_position] == self.BOARD_DICT[self.ON_BOMB_LIST[player.number]]:
                        # clear previous position only if it wasn't a just-placed bomb
                        board[player.prev_position] = self.BOARD_DICT['empty']
                    else:
                        # player has left behind a bomb
                        board[player.prev_position] = self.BOARD_DICT['bomb']
            else:
                # return some invalid move penalty
                player.score += self.get_reward('invalid_move')

            # update timer of any bombs
            for bomb in player.bombs:
                bomb_list.append(bomb)
                bomb.update_timer()                               
                if bomb.timer == 0: # bomb explodes
                    # check if any player is in range of the bomb
                    is_game_over, player_hit = self.state_check_if_game_over(bomb.tiles_in_range,board)
                    if is_game_over:
                        done = True
                        players[player_hit].score += self.get_reward('lose')
                    #num_blocks = self.state_explode_bomb(bomb, board) # update bomb objects and map
                    num_blocks = self.explode_bomb(bomb)
                    player.score += self.get_reward('destroy_blocks', num_blocks)
                    player.num_bombs += 1 # return bomb to the player



        turn = turn + 1
        new_state["players"] = players
        new_state["board"] = board
        new_state["done"] = done 
        new_state["bombs"] = bomb_list
        new_state["turn"] = turn

        return new_state



    def step(self, player_actions):

        rewards = np.zeros((len(self.players),1)) # rewards assigned this turn
        bomb_list = [] # populate list of bombs to return to players

        # get player's new positions
        # this is to make things in random
        r = list(range(len(self.players)))
        random.shuffle(r)
        for i in r:
            player = self.players[i] # this is to make it random

            # store current position before next move
            player.prev_position = player.position 
            # update players new position
            #player.position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[player_actions[player.number]],player.prev_position)])

            # clear any recent bombs
            for bomb in player.bombs:
                if bomb.recently_exploded == True:
                    self.clear_bomb(bomb)
                    del bomb # don't think this works?
                    player.bombs = [] # will need to fix this for when players have multiple bombs

            # get player's action
            action = player_actions[player.number]
            # get player's new position if action is taken
            new_position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[player_actions[player.number]],player.prev_position)])

            if self.check_if_valid(action, player.prev_position, new_position):
                player.position = new_position # valid move, so update player's position
                if action == actions.BOMB:
                    if player.num_bombs > 0:
                        player.bombs.append(Bomb(player.position, self.get_tiles_in_range(player.position), player.number, self.MAX_TIMER)) # create a bomb instance
                        player.num_bombs -= 1 # one less bomb available for the player
                        self.board[player.position] = self.BOARD_DICT[self.ON_BOMB_LIST[player.number]] # place bomb on map
                elif action == actions.NONE:
                    pass
                else:
                    # move
                    self.board[player.position] = self.BOARD_DICT[self.PLAYER_LIST[player.number]]

                    if not self.board[player.prev_position] == self.BOARD_DICT[self.ON_BOMB_LIST[player.number]]:
                        # clear previous position only if it wasn't a just-placed bomb
                        self.board[player.prev_position] = self.BOARD_DICT['empty']
                    else:
                        # player has left behind a bomb
                        self.board[player.prev_position] = self.BOARD_DICT['bomb']
            else:
                # return some invalid move penalty
                '''
                print("<<<<An Unvalid move is played>>>>")
                print("action:", action)
                print("curr_pos", player.prev_position)
                print("new_pos", new_position)
                print("playerNumber:", player.number)
                '''

                player.score += self.get_reward('invalid_move')

            # update timer of any bombs
            for bomb in player.bombs:
                bomb_list.append(bomb)
                bomb.update_timer()                               
                if bomb.timer == 0: # bomb explodes
                    # check if any player is in range of the bomb
                    is_game_over, player_hit = self.check_if_game_over(bomb.tiles_in_range)
                    if is_game_over:
                        self.done = True
                        self.players[player_hit].score += self.get_reward('lose')
                    num_blocks = self.explode_bomb(bomb) # update bomb objects and map
                    player.score += self.get_reward('destroy_blocks', num_blocks)
                    player.num_bombs += 1 # return bomb to the player

        return self.board, self.done, self.players, bomb_list

    def state_check_if_valid(self, action, curr_pos, new_pos, current_board):
        ##Armin
        ######################### add logic for 'none' after recent bomb
        ### merge

        if (action == actions.NONE) or (action == actions.BOMB):
            is_valid = True
        elif (new_pos[0] < 0 or new_pos[1] < 0):
            # trying to move through left or top boundary
            is_valid = False
        elif new_pos[0] >= self.rows or new_pos[1] >= self.cols:
            # trying to move through right or bottom boundary
            is_valid = False
        elif (current_board[tuple(new_pos)] == self.BOARD_DICT['empty']) or (current_board[tuple(new_pos)] == self.BOARD_DICT['exploding_tile']):
            is_valid = True
        else:
            is_valid = False

        return is_valid


    def check_if_valid(self, action, curr_pos, new_pos):
        
        ######################### add logic for 'none' after recent bomb
        ### merge

        if (action == actions.NONE) or (action == actions.BOMB):
            is_valid = True
        elif (new_pos[0] < 0 or new_pos[1] < 0):
            # trying to move through left or top boundary
            is_valid = False
        elif new_pos[0] >= self.rows or new_pos[1] >= self.cols:
            # trying to move through right or bottom boundary
            is_valid = False
        elif (self.board[tuple(new_pos)] == self.BOARD_DICT['empty']) or (self.board[tuple(new_pos)] == self.BOARD_DICT['exploding_tile']):
            is_valid = True
        else:
            is_valid = False

        return is_valid

    def check_if_game_over(self,tiles):

        is_game_over = False # did a player get hit
        player_hit = None # which player

        for tile in tiles:
            if (self.board[tile] == self.BOARD_DICT['player1']) or (self.board[tile] == self.BOARD_DICT['p1_on_bomb']):
                is_game_over = True
                player_hit = 0

            if (self.board[tile] == self.BOARD_DICT['player2']) or (self.board[tile] == self.BOARD_DICT['p2_on_bomb']):
                is_game_over = True
                player_hit = 1

        return is_game_over, player_hit

    def state_check_if_game_over(self,tiles, current_board):
        '''ARMIN state_based'''
        is_game_over = False # did a player get hit
        player_hit = None # which player

        for tile in tiles:
            if (current_board[tile] == self.BOARD_DICT['player1']) or (current_board[tile] == self.BOARD_DICT['p1_on_bomb']):
                is_game_over = True
                player_hit = 0

            if (current_board[tile] == self.BOARD_DICT['player2']) or (current_board[tile] == self.BOARD_DICT['p2_on_bomb']):
                is_game_over = True
                player_hit = 1

        return is_game_over, player_hit

    ###################################            
    ###### BOMB HELPER FUNCTIONS ######
    ###################################

    def get_tiles_in_range(self, position):
        '''
        get surrounding 4 tiles impacted near bomb
        '''

        tile_up = (position[0]-1,position[1])
        tile_down = (position[0]+1,position[1])
        tile_left = (position[0],position[1]-1)
        tile_right = (position[0],position[1]+1)


        long_range = False
        if (long_range):
            ## making explosions go till the edge
            ## explosions stops if they hit a block
            bomb_range = []
            #going right
            #xPosition = position[1]
            #yPosition = position[0]
            for xPosition in range(position[1], self.cols):
                tempTile = (position[0], xPosition)
                if (self.board[tempTile] == self.BOARD_DICT['hard_block']):
                    break
                elif(self.board[tempTile] == self.BOARD_DICT['soft_block']):
                    bomb_range.append(tempTile)
                    break
                else:
                    bomb_range.append(tempTile)
            #going left
            for xPosition in range(position[1], -1, -1):
                tempTile = (position[0], xPosition)
                if (self.board[tempTile] == self.BOARD_DICT['hard_block']):
                    break
                elif(self.board[tempTile] == self.BOARD_DICT['soft_block']):
                    bomb_range.append(tempTile)
                    break
                else:
                    bomb_range.append(tempTile)
            #going down
            for yPosition in range(position[0], self.rows):
                tempTile = (yPosition, position[1])
                if (self.board[tempTile] == self.BOARD_DICT['hard_block']):
                    break
                elif(self.board[tempTile] == self.BOARD_DICT['soft_block']):
                    bomb_range.append(tempTile)
                    break
                else:
                    bomb_range.append(tempTile)
            #going up
            for yPosition in range(position[0],-1 , -1):
                tempTile = (yPosition, position[1])
                if (self.board[tempTile] == self.BOARD_DICT['hard_block']):
                    break
                elif(self.board[tempTile] == self.BOARD_DICT['soft_block']):
                    bomb_range.append(tempTile)
                    break
                else:
                    bomb_range.append(tempTile)

        else:

            #Single block
            bomb_range = [tile_up, tile_down, tile_left, tile_right, position]
            tiles_to_remove = []

            for tile in bomb_range:
                if (tile[0] < 0 or tile[1] < 0 or tile[0] >= self.rows or tile[1] >= self.cols or 
                    self.board[tile] == self.BOARD_DICT['hard_block']):
                    # exclude tiles that cross the border of the board
                    # or contain indestructible object
                    tiles_to_remove.append(tile)

            for tile in tiles_to_remove:
                bomb_range.remove(tile)

        return bomb_range

    def explode_bomb(self, bomb):
        '''
        reset bomb parameters and return number of blocks destroyed
        '''
        #### fix bomb behavior - inputs are tiles & position only, not bomb object

        num_blocks = 0

        # update tiles that have been impacted
        for tile in bomb.tiles_in_range:
            if self.board[tile] == self.BOARD_DICT['soft_block']:
                num_blocks+=1
            self.board[tile] = self.BOARD_DICT['exploding_tile']

        self.board[bomb.position] = self.BOARD_DICT['exploding_bomb']

        bomb.explode()

        return num_blocks


    def state_explode_bomb(self, bomb, current_board):
        '''
        Armin
        reset bomb parameters and return number of blocks destroyed
        '''
        #### fix bomb behavior - inputs are tiles & position only, not bomb object

        num_blocks = 0

        # update tiles that have been impacted
        for tile in bomb.tiles_in_range:
            if current_board[tile] == self.BOARD_DICT['soft_block']:
                num_blocks+=1
            current_board[tile] = self.BOARD_DICT['exploding_tile']

        current_board[bomb.position] = self.BOARD_DICT['exploding_bomb']

        bomb.explode()

        return num_blocks

     


    def clear_bomb(self, bomb):
        '''
        clear map after recent bomb
        '''

        self.board[bomb.position] = self.BOARD_DICT['empty'] 
        for tile in bomb.tiles_in_range:
            if (self.board[tile] != self.BOARD_DICT['player1']) and (self.board[tile] != self.BOARD_DICT['player2']):
                self.board[tile] = self.BOARD_DICT['empty']

        bomb.clear()


    def state_clear_bomb(self, bomb, current_board):
        '''
        Armin
        clear map after recent bomb
        '''

        current_board[bomb.position] = self.BOARD_DICT['empty'] 
        for tile in bomb.tiles_in_range:
            if (current_board[tile] != self.BOARD_DICT['player1']) and (current_board[tile] != self.BOARD_DICT['player2']):
                current_board[tile] = self.BOARD_DICT['empty']

        bomb.clear()
        
    def get_reward(self, item, num_blocks=0):
        '''
        reward system:
        +1 destroy block
        -10 invalid move
        -1000 lose game
        +100 win game
        '''
        if item == 'destroy_blocks':
            return num_blocks * self.REWARDS_DICT[item]
        else:
            return self.REWARDS_DICT[item]

    def reset(self,num_players=2):
        '''
        Initializes a starting board
        '''

        ### move num_players to environment level

        # initalize board
        self.board = np.zeros((self.rows,self.cols)).astype(int)
        self.players = [] # stores player objects
        self.tiles_in_range = [] # stores position of surrounding spaces near a bomb --> should beowned by bomb?
        self.done = False # checks if game over

        self.turn_i = 0

        # number of soft blocks to place
        num_soft_blocks = int(math.floor(0.3*self.cols*self.rows))

        # initialize players
        assert num_players <= 4
        starting_positions = [(0,0), (self.rows-1, self.cols-1), (0, self.cols-1), (self.rows-1, 0)]
        for i in range(num_players):
            self.players.append(Player(i, starting_positions[i], self.MAX_BOMBS))

        # update map with player locations
        player_list = ['player1', 'player2', 'player3', 'player4']
        for player in range(len(self.players)):
            self.board[self.players[player].position] = self.BOARD_DICT[player_list[player]]

        # place hard blocks
        self.board[1::2,1::2] = self.BOARD_DICT['hard_block']

        ## place soft blocks (random)
        # flatten array
        flat_board = np.reshape(self.board,-1)
        # get positions that can be filled
        open_pos = [i for i in range(len(flat_board)) if flat_board[i] == 0]
        # spots immediately to the right and bottom of player1 can't be filled
        open_pos.remove(1)
        open_pos.remove(2)
        open_pos.remove(self.cols)
        open_pos.remove(self.cols*2)
        # spots immediately to the left and top of player2 can't be filled
        open_pos.remove(self.cols * self.rows - 2)
        open_pos.remove(self.cols * self.rows - 3)
        open_pos.remove(self.cols * self.rows - self.cols*2 - 1)
        open_pos.remove(self.cols * self.rows - self.cols - 1)
        # choose a random subset from open spots
        rand_pos = random.sample(open_pos,num_soft_blocks)
        flat_board[rand_pos] = self.BOARD_DICT['soft_block']
        self.board = np.reshape(flat_board,(self.rows,self.cols))

        return self.board, self.players

    def render(self, graphical=True):
        self.turn_i = self.turn_i +1
        folder = "./temp_photo"
        os.makedirs(folder,exist_ok=True)
        # renders bomberman environment
        print_ascii = True
        
        if self.config_data["print_ascii"] == 'True':
            if os.name == 'nt': 
                os.system('cls') 
  
            # for mac and linux(here, os.name is 'posix') 
            else: 
                os.system('clear')
            print(self)

        #if self.config_data["graphical"] == 'True':

        # render with graphics
        if graphical:
            flattened_map = np.reshape(self.board,-1)
            # get rows
            map_rows=[]

            map_rows.append(np.concatenate(([img_wall_top_mid for i in range(self.cols)]),axis=1))
            mid_wall = np.concatenate(([img_wall for i in range((2))]),axis=1)
            map_rows.append(np.concatenate((mid_wall,img_banner_wall,img_banner_wall,img_banner_wall,mid_wall),axis=1))

            for row in range(self.rows):
                map_rows.append(np.concatenate(([dict_img[i] for i in self.board[row]]),axis=1))

            temp_cols = np.concatenate(([img_wall_bot for i in range(self.cols)]),axis=1)
            map_rows.append(temp_cols)

            full_map = np.concatenate(([i for i in map_rows]),axis=0)

            lhs = np.concatenate(([img_wall_left for i in range(self.rows+1)]),axis=0)
            lhs = np.concatenate((img_wall_top_left,lhs,img_wall_side_front_left),axis=0)
            rhs = np.concatenate(([img_wall_right for i in range(self.rows+1)]),axis=0)
            rhs = np.concatenate((img_wall_top_right,rhs,img_wall_side_front_right),axis=0)

            full_map = np.concatenate((lhs,full_map,rhs),axis=1)
            
            plt.clf()
            plt.imshow(full_map)
            plt.axis('off')
            plt.ion()

            plt.suptitle(f'P{self.players[0].number+1} {self.players[0].name}: {self.players[0].score} vs P{self.players[1].number+1} {self.players[1].name}: {self.players[1].score}')

            #plt.savefig(folder + "/" +'match{0:02}.png'.format(self.turn_i), dpi = 120, bbox_inches= "tight") #Armin
            
            plt.show()

            plt.pause(0.05)
        # render text-based environment




    def render_with_state(self, graphical, current_state):
        # renders the given state based on the current_State
        current_board = current_state["board"] 
        current_done = current_state["done"]
        current_bombs = current_state["bombs"]
        current_turn = current_state["turn"]
        current_player = current_state["players"]

        print_ascii = True



        # render with graphics
        if graphical:
            flattened_map = np.reshape(current_board,-1)
            # get rows
            map_rows=[]
            for row in range(len(current_board)):
                map_rows.append(np.concatenate(([dict_img[i] for i in current_board[row]]),axis=1))

            full_map = np.concatenate(([i for i in map_rows]),axis=0)


            #full_map = np.concatenate(([dict_img[i] for i in flattened_map]),axis=0)
            plt.clf()
            plt.imshow(full_map)
            plt.axis('off')
            plt.ion()
            plt.show()
            plt.pause(0.05)
        # render text-based environment
        else:
            print(current_board)


    def print_state(self,current_state):
        current_board = current_state["board"]        

        # return visualized board
        '''
        Displays board with icons instead of number values
        Player = P
        Bomb = *
        Soft block = O
        Hard block = X
        '''
        #initialize row & col
        row=0
        col=0

        # map icons to board
        d = {0: '     ', 1:f'{bcolors.MAGENTA}  P1 {bcolors.RESET}', 2:f'{bcolors.BLUE}  P2 {bcolors.RESET}', 3:f'{bcolors.YELLOW}  O  {bcolors.RESET}',
         4:'  X  ', 5:f'{bcolors.RED}  *  {bcolors.RESET}', 6:f'{bcolors.MAGENTA} P1* {bcolors.RESET}', 7:f'{bcolors.BLUE} P2* {bcolors.RESET}',
          8:f'{bcolors.RED}  !  {bcolors.RESET}', 9:f'{bcolors.RED} === {bcolors.RESET}'}
        #d = {0: '     ', 1:'  P1 ', 2:'  O  ', 3:'  X  ', 4:'  *  ', 5:'  P* ', 6:'  !  ', 7:' === '}
        flat_board = np.reshape(current_board,-1)
        mapped_board=[d[i] for i in flat_board]
        mapped_board = np.reshape(mapped_board,current_board.shape)

        board_str=""
        for row in range(len(current_board)):
            row_str = ""
            board_str += "-"*(len(current_board[0]))*6 + "\n"
            for col in range(len(current_board[0])):
                row_str += f"|{mapped_board[row,col]}"
            board_str += row_str + "|" + "\n"
        board_str += "-"*(len(current_board[0]))*6
        print(board_str)
    


    def __str__(self):
        # return visualized board
        '''
        Displays board with icons instead of number values
        Player = P
        Bomb = *
        Soft block = O
        Hard block = X
        '''
        #initialize row & col
        row=0
        col=0

        # map icons to board
        d = {0: '     ', 1:f'{bcolors.MAGENTA}  P1 {bcolors.RESET}', 2:f'{bcolors.BLUE}  P2 {bcolors.RESET}', 3:f'{bcolors.YELLOW}  O  {bcolors.RESET}',
         4:'  X  ', 5:f'{bcolors.RED}  *  {bcolors.RESET}', 6:f'{bcolors.MAGENTA} P1* {bcolors.RESET}', 7:f'{bcolors.BLUE} P2* {bcolors.RESET}',
          8:f'{bcolors.RED}  !  {bcolors.RESET}', 9:f'{bcolors.RED} === {bcolors.RESET}'}
        #d = {0: '     ', 1:'  P1 ', 2:'  O  ', 3:'  X  ', 4:'  *  ', 5:'  P* ', 6:'  !  ', 7:' === '}
        flat_board = np.reshape(self.board,-1)
        mapped_board=[d[i] for i in flat_board]
        mapped_board = np.reshape(mapped_board,self.board.shape)

        board_str=""
        for row in range(self.rows):
            row_str = ""
            board_str += "-"*self.cols*6 + "\n"
            for col in range(self.cols):
                row_str += f"|{mapped_board[row,col]}"
            board_str += row_str + "|" + "\n"
        board_str += "-"*self.cols*6
        
        return board_str


