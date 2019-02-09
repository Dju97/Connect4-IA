from player import Player
import random
import copy
import math
import utils
import time
import numpy as np

class AIPlayer(Player):
    """This player should implement a heuristic along with a min-max or alpha
    beta search to """


    def __init__(self):
        super().__init__()
        self.name = "AlphaConnect4"

    def getColumn(self, board):
        # TODO(student): implement this!
        start = time.time()
        number_of_move = sum(sum(abs(np.array(board.board))))#Compute how many moves have been played so far
        max_exploration = 3 #Increase or decrease this to increase/decrease level of AI, it is the depth of the algorithm
        max_value = -math.inf
        best_move = board.getPossibleColumns()[0]
        alpha = -math.inf
        beta = math.inf
        for i in board.getPossibleColumns(): #Here we implement a alpha-beta algorithm, we loop over each possibility
            new_board = copy.deepcopy(board)#We make a copy of the actual board to simulate a move
            pos = i,new_board.play(self.color,i)
            #We search the max we can obtain from the min value the opponent can have if he plays the best moves.
            min_value_found = self.min_value(new_board,max_exploration,0,self.color*-1,alpha,beta,self.color,pos,number_of_move+1)
            if min_value_found > max_value:
                best_move = i
                max_value = min_value_found
        end = time.time()
        print(end-start)
        return best_move
        

    def max_value(self,board,max_exploration,current_exploration,player,alpha,beta,initial_player,last_move,number_of_move):
        #If a sufficient number of moves has been played, we check if someone has won 
        if(number_of_move>=7):
            hasWon = self.hasWon(board,initial_player,last_move)
            if hasWon:
                return hasWon
        #If we arrived at the maximum depth, we compute the estimation of the position
        if current_exploration >= max_exploration or board.isFull(): 
            cost = self.cost(board,initial_player,last_move)
            return cost
        #Else we continue to explore the tree
        else:
            v = -math.inf
            for i in board.getPossibleColumns():
                new_board = copy.deepcopy(board)
                pos = i,new_board.play(player,i)
                min_value = self.min_value(new_board,max_exploration,current_exploration+1,player*-1,alpha,beta,initial_player,pos,number_of_move+1)
                v = max(v,min_value)
                if v >= beta:
                    return v #Beta cut
                alpha = max(alpha,v)
            return v

    #Same as max function
    def min_value(self,board,max_exploration,current_exploration,player,alpha,beta,initial_player,last_move,number_of_move):
        if(number_of_move>=7):
            hasWon = self.hasWon(board,initial_player,last_move)
            if hasWon:
                return hasWon
        if current_exploration >= max_exploration or board.isFull():
            cost = self.cost(board,initial_player,last_move)
            return cost
        else:
            v = math.inf
            for i in board.getPossibleColumns():
                new_board = copy.deepcopy(board)
                pos = i,new_board.play(player,i)
                max_value = self.max_value(new_board,max_exploration,current_exploration+1,player*-1,alpha,beta,initial_player,pos,number_of_move+1)
                v = min(v,max_value)
                if v <= alpha:
                    return v #Alpha cut
                beta = min(beta,v)
            return v

    def cost(self,board,player,pos): #Here is our heuristic, the main part of our AI
        cost = 0
        #Our heuristic is mainly composed of two components, we attribute a coefficient to each one
        C_alignment = 20
        C_central = 1
        tests = []
        #Looping over rows and columns and thanks to our additional function, we test each block of 4 squares
        # and we check if it's occupied by a team + empty (If there is only a color and empty blocks, the team with this color can expect 
        # connect 4). If it's the case we had to the heuristic, a bonus proportional to the number of blocks of one's color. 
        for y in range(6):
            tests.append(board.getRow(y))
            tests.append(board.getCol(y))
        for test in tests:
            if any(test):
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]

        if(any(board.getCol(6))):
            sizes =  self.longest_by_players(board.getCol(6))
            cost += (sum(sizes[player])>=4)*C_alignment*sizes[player][0]
            cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]
                
        #We make the same for diagonal
        tests = []
        for d in range(0,7):
            tests.append(board.getDiagonal(False,d))
            tests.append(board.getDiagonal(True,d))
        for d in range(6,13):
            tests.append(board.getDiagonal(False,d))
        for d in range(-6,0):
            tests.append(board.getDiagonal(True,d))
        for test in tests:
            if any(test):
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]
        
        #Secondly, we attribute to each square a value, because central squares are more important than those on sides.
        values_by_rows = [15,20,15,12,4,0]
        values_by_col = [0,2,10,15,10,2,0]
        cost += np.dot(np.dot(values_by_rows,np.array(board.board).T),values_by_col)*C_central*player
        return cost
    
    #This function takes a list of squares and return the best sequence of following colored-squares or empty-squares for each player. 
    #The resulting dictionnary is like : {color:[colored_squres_best_sequence,empty_squares_best_sequence]}
    #For example : for a sequence like : o| |x|x| |x, the dict is like {'o':[1,1],'x':[3,1]}
    def longest_by_players(self,seq):
        best = {-1 : [0,0],1:[0,0]}
        curr = {-1 : [0,0],1:[0,0]}
        for v in seq:
            if v == 0:
                curr[-1][1] += 1
                curr[1][1] += 1
            else:
                curr[v][0] += 1
                curr[-1*v][0] = 0
                curr[-1*v][1] = 0
            if curr[-1][0]>=best[-1][0] and sum(curr[-1]) > sum(best[-1]):
                best[-1] = curr[-1]
            if curr[1][0]>=best[-1][0] and sum(curr[1]) > sum(best[1]):
                best[1] = curr[1]            
        return best

    #Test if one the player has won the game
    def hasWon(self,board,player,pos):
        tests = []
        tests.append(board.getCol(pos[0]))
        tests.append(board.getRow(pos[1]))
        tests.append(board.getDiagonal(True, pos[0] - pos[1]))
        tests.append(board.getDiagonal(False, pos[0] + pos[1]))
        for test in tests:
            color, size = utils.longest(test)
            if size >= 4:
                if player == color:
                    return math.inf
                else:
                    return -math.inf
        return None