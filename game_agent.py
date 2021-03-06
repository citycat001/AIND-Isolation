"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
from math import *

ITER_NUM = 10000

class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass
    
def cornerpenalty(game, player):
    corners_2moves = [(0, 0), (game.width - 1, 0), (0, game.height - 1), (game.width - 1, game.height - 1)]
    corners_3moves = [(0, 1), (1, 0), (0, game.height - 2), (1, game.height - 1), 
                      (game.width - 2, 0), (game.width - 1, 1), (game.width - 1, game.height - 2),
                      (game.width - 2, game.height - 1)]
    
    if game.get_player_location(player) in corners_2moves:
        return -3
    elif game.get_player_location(player) in corners_3moves:
        return -2
    
    return 0

def movecount(m, game):
    r, c = m
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]
    return len([(r + dr, c + dc) for dr, dc in directions
                   if game.move_is_legal((r + dr, c + dc))])

class Node:
    def __init__(self, game, parent = None):
        self.move = game.get_player_location(game.inactive_player)
        self.parent = parent
        self.wincount = 0.
        self.visitcount = 0
        self.child = []
        self.notvisit = game.get_legal_moves()
        
    def selectchild(self):
        #use UCB1, apply a constant UCTK.
        return sorted(self.child, key = lambda n: n.wincount / n.visitcount 
                      + sqrt(2 * log(self.visitcount) / n.visitcount))[-1]
        
    def addchild(self, game):
        n = Node(game, self)
        self.notvisit.remove(game.get_player_location(game.inactive_player))
        self.child.append(n)
        return n
    
    def updatevalue(self, v):
        self.visitcount = self.visitcount + 1
        self.wincount = self.wincount + v

def mctsucb1(player, game, iternum = 100):
    rn = Node(game)

    if not game.get_legal_moves():
        return -1
    
    for i in range(iternum):
        if player.time_left() < player.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        n = rn
        g = game.copy()
        
        #select
        while not n.notvisit and n.child:
            if player.time_left() < player.TIMER_THRESHOLD:
                raise SearchTimeout()
            n = n.selectchild()
            g.apply_move(n.move)
            
        if n.notvisit:
            m = random.choice(n.notvisit)
            g.apply_move(m)
            n = n.addchild(g)
        
        while g.get_legal_moves(): #random.choice(g.get_legal_moves()))
            if player.time_left() < player.TIMER_THRESHOLD:
                raise SearchTimeout()
            g.apply_move(random.choice(g.get_legal_moves()))#max(g.get_legal_moves(), key = lambda v: self.score(g.forecast_move(v), g.inactive_player)))

        v = 0.
        if g.inactive_player == player:
            v = 1.
        while n:
            if player.time_left() < player.TIMER_THRESHOLD:
                raise SearchTimeout()            
            n.updatevalue(v)
            n = n.parent

    return sorted(rn.child, key = lambda n: n.visitcount)[-1].visitcount

def custom_score_mcts(game, player):
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")
    
    return mctsucb1(player, game, ITER_NUM)

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")
    
    wml = game.get_legal_moves(player)
    oml = game.get_legal_moves(game.get_opponent(player))

    own_moves = len(wml)
    opp_moves = len(oml)
    own_moves_next = 0
    opp_moves_next = 0
    
    for m in wml:
        own_moves_next = own_moves_next + movecount(m, game)
    for m in oml:
        opp_moves_next = opp_moves_next + movecount(m, game)
    
    return float(own_moves + own_moves_next - opp_moves - opp_moves_next + cornerpenalty(game, player))

def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    y1, x1 = game.get_player_location(game.get_opponent(player))
    y, x = game.get_player_location(player)
    return float(abs(y1 - y) + abs(x1 - x) + cornerpenalty(game, player))

def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    return float(own_moves - opp_moves + cornerpenalty(game, player))

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """
    
    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            # Handle any actions required after timeout as needed
            if game.get_legal_moves():
                return random.choice(game.get_legal_moves())
            else:
                return best_move

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        # TODO: finish this function!
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        if self.__terminal_test(game, depth):
            return (-1, -1)
        
        return max(game.get_legal_moves(),
                   key=lambda m: self.__min_value(game.forecast_move(m), depth - 1)) 

    def __terminal_test(self, game, depth):
        if depth > 0 and game.get_legal_moves(): #or reach the depth limit
            return False
        return True

    def __min_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()  
            
        state = []
        if self.__terminal_test(game, depth):
            return self.score(game, self)
        
        for m in game.get_legal_moves():
            gs = game.forecast_move(m)
            state.append(self.__max_value(gs, depth - 1))       
        return min(state)
    
    def __max_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout() 
            
        state = []
        if self.__terminal_test(game, depth):
            return self.score(game, self)
  
        for m in game.get_legal_moves():
            gs = game.forecast_move(m)
            state.append(self.__min_value(gs, depth - 1))
        return max(state)

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """    

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        
        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        m = (-1, -1)
        lm = game.get_legal_moves()
        if not lm:
            return m
        
        self.search_depth = 100

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            for i in range(0, self.search_depth): 
                m = self.alphabeta(game, i)

        except SearchTimeout:
             # Handle any actions required after timeout as needed
            if m == (-1, -1):
                m = random.choice(lm)
        return m

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        m, _ = self.__ab(game, depth, alpha, beta)
        return m
        
    def __ab(self, game, depth, alpha, beta):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # TODO: finish this function!
        best_move = (-1, -1)
        ml = game.get_legal_moves(game.active_player)
        
        if game.active_player == self:
            if not depth or not ml:
                return best_move, self.score(game, self)
            best_move = random.choice(ml)
            v = float("-inf")
            for m in ml:
                _, x = self.__ab(game.forecast_move(m), depth - 1, alpha, beta)
                if x > v:
                    v = x
                    best_move = m
                if v > alpha:
                    alpha = v
                    best_move = m
                if beta <= alpha:
                    break            
        else:
            if not depth or not ml:
                return best_move, self.score(game, game.inactive_player) 
            best_move = random.choice(ml)
            v = float("inf")        
            for m in ml:
                _, x = self.__ab(game.forecast_move(m), depth - 1, alpha, beta)
                if x < v:
                    v = x
                    best_move = m
                if v < beta:
                    beta = v
                    best_move = m
                if beta <= alpha:
                    break
        return best_move, v        