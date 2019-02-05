from player import Player
import random
import copy
import math
import utils

class AIPlayer(Player):
    """This player should implement a heuristic along with a min-max or alpha
    beta search to """


    def __init__(self):
        super().__init__()
        self.name = "AlphaConnect4"

    def getColumn(self, board):
        # TODO(student): implement this!
        max_eploration =3  #MUST BE AN ODD NUMBER
        max_value = -math.inf
        best_move = board.getPossibleColumns()[0]
        alpha = -math.inf
        beta = math.inf
        for i in board.getPossibleColumns():
            new_board = copy.deepcopy(board)
            pos = i,new_board.play(self.color,i)
            min_value_found = self.min_value(new_board,max_eploration,0,self.color*-1,alpha,beta,self.color,pos)
            print(str(i) + ' : ' + str(min_value_found))
            if min_value_found > max_value:
                best_move = i
                max_value = min_value_found
        return best_move
        

    def max_value(self,board,max_eploration,current_exploration,player,alpha,beta,initial_player,last_move):
        hasWon = self.hasWon(board,initial_player,last_move)
        if hasWon:
            return hasWon
        if current_exploration >= max_eploration or board.isFull():
            cost = self.cost(board,initial_player,last_move)
            return cost
        else:
            v = -math.inf
            for i in board.getPossibleColumns():
                new_board = copy.deepcopy(board)
                pos = i,new_board.play(player,i)
                min_value = self.min_value(new_board,max_eploration,current_exploration+1,player*-1,alpha,beta,initial_player,pos)
                v = max(v,min_value)
                if v >= beta:
                    return v
                alpha = max(alpha,v)
            return v


    def min_value(self,board,max_eploration,current_exploration,player,alpha,beta,initial_player,last_move):
        hasWon = self.hasWon(board,initial_player,last_move)
        if hasWon:
            return hasWon
        if current_exploration >= max_eploration or board.isFull():
            cost = self.cost(board,initial_player,last_move)
            return cost
        else:
            v = math.inf
            for i in board.getPossibleColumns():
                new_board = copy.deepcopy(board)
                pos = i,new_board.play(player,i)
                v = min(v,self.max_value(new_board,max_eploration,current_exploration+1,player*-1,alpha,beta,initial_player,pos))
                if v <= alpha:
                    return v
                beta = min(beta,v)
            return v

    def cost(self,board,player,pos):
        cost = 0
        C_alignment = 1
        C_controled_blank = 1
        tests = []
        for y in range(board.num_rows):
            tests.append(board.getRow(y))
            for test in tests:
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]

        tests= []
        for x in range(board.num_cols):
            tests.append(board.getCol(x))
            for test in tests:
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]

        tests = []
        for d in range(board.num_cols + board.num_rows):
            tests.append(board.getDiagonal(False,d))
            for test in tests:
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*0.5*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*sizes[-1*player][0]

        tests = []
        for d in range(-board.num_rows,board.num_cols):
            tests.append(board.getDiagonal(True,d))
            for test in tests:
                sizes =  self.longest_by_players(test)
                cost += (sum(sizes[player])>=4)*C_alignment*0.5*sizes[player][0]
                cost -= (sum(sizes[-1*player])>=4)*C_alignment*0.5*sizes[-1*player][0]

        return cost
    
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
                curr[-1*v][1] =0
            if sum(curr[-1]) > sum(best[-1]):
                best[-1] = curr[-1]
            if sum(curr[1]) > sum(best[1]):
                best[1] = curr[1]            
        return best

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