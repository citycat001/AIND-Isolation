"""Implement your own custom search agent using any combination of techniques
you choose.  This agent will compete against other students (and past
champions) in a tournament.

         COMPLETING AND SUBMITTING A COMPETITION AGENT IS OPTIONAL
"""
import random

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
        
def custom_score_improve(game, player):
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

class CustomPlayer:
    """Game-playing agent to use in the optional player vs player Isolation
    competition.

    You must at least implement the get_move() method and a search function
    to complete this class, but you may use any of the techniques discussed
    in lecture or elsewhere on the web -- opening books, MCTS, etc.

    **************************************************************************
          THIS CLASS IS OPTIONAL -- IT IS ONLY USED IN THE ISOLATION PvP
        COMPETITION.  IT IS NOT REQUIRED FOR THE ISOLATION PROJECT REVIEW.
    **************************************************************************

    Parameters
    ----------
    data : string
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted.  Note that
        the PvP competition uses more accurate timers that are not cross-
        platform compatible, so a limit of 1ms (vs 10ms for the other classes)
        is generally sufficient.
    """

    def __init__(self, data=None, timeout=10.):
        self.score = custom_score_improve
        self.search_depth = 100
        self.time_left = None
        self.TIMER_THRESHOLD = timeout  
        self.mirrortable = dict()

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
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
        # OPTIONAL: Finish this function!
        self.time_left = time_left
        
        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        m = (-1, -1)
        lm = game.get_legal_moves()
        if not lm:
            return m

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            for i in range(0, self.search_depth): 
                self.mirrortable.clear()
                m = self.alphabeta(game, i)

        except SearchTimeout:
             # Handle any actions required after timeout as needed
            if m == (-1, -1):
                m = random.choice(lm)
        return m

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
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
            value, move = self.__retrieve(game)
            if value:
                return move, value
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
            value, move = self.__retrieve(game)
            if value:
                return move, value            
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
        self.__update(game, v, best_move)
        return best_move, v    
    
    def __normalhash(self, game):
        h = 0
        for i in range(len(game._board_state) - 3):
            h = h + 2 ^ i * game._board_state[i]
        return (h, game._board_state[-1], game._board_state[-2])
    
    def __updownmirror(self, game):
        h = 0
        mirror = [0] * (len(game._board_state) - 3)
        for i in range(len(game._board_state) - 3):
            x = i % game.height
            y = game.height - 1 - i // game.height
            mirror[x + y * game.height] = 1            
        for i in range(len(mirror)):
            h = h + 2 ^ i * mirror[i]
            
        x = game._board_state[-1] % game.height
        y = game.height - 1 - game._board_state[-1] // game.height
        p1 = x + y * game.height
        
        x = game._board_state[-2] % game.height
        y = game.height - 1 - game._board_state[-2] // game.height
        p2 = x + y * game.height        
        
        return (h, p1, p2)   

    def __leftrightmirror(self, game):
        h = 0
        mirror = [0] * (len(game._board_state) - 3)
        for i in range(len(game._board_state) - 3):
            x = game.width - 1 - i % game.height
            y = i // game.height
            mirror[x + y * game.height] = 1            
        for i in range(len(mirror)):
            h = h + 2 ^ i * mirror[i]   
            
        x = game.width - 1 - game._board_state[-1] % game.height
        y = game._board_state[-1] // game.height
        p1 = x + y * game.height
        
        x = game.width - 1 - game._board_state[-2] % game.height
        y = game._board_state[-2] // game.height
        p2 = x + y * game.height
            
        return (h, p1, p2)  

    def __diagonalmirror(self, game):  
        h = 0
        mirror = [0] * (len(game._board_state) - 3)
        for i in range(len(game._board_state) - 3):
            x = i // game.height
            y = i % game.height
            mirror[x + y * game.height] = 1 
        for i in range(len(mirror)):
            h = h + 2 ^ i * mirror[i]
            
        x = game._board_state[-1] // game.height
        y = game._board_state[-1] % game.height
        p1 = x + y * game.height
        
        x = game._board_state[-2] // game.height
        y = game._board_state[-2] % game.height
        p2 = x + y * game.height            
            
        return (h, p1, p2)  

    def __reversediagmirror(self, game):  
        h = 0
        mirror = [0] * (len(game._board_state) - 3)
        for i in range(len(game._board_state) - 3):
            x = game.height - 1 - i // game.height
            y = game.width - 1 - i % game.height
            mirror[x + y * game.height] = 1 
        for i in range(len(mirror)):
            h = h + 2 ^ i * mirror[i]
            
        x = game.height - 1 - game._board_state[-1] // game.height
        y = game.width - 1 - game._board_state[-1] % game.height
        p1 = x + y * game.height
        
        x = game.height - 1 - game._board_state[-2] // game.height
        y = game.width - 1 - game._board_state[-2] % game.height
        p2 = x + y * game.height   
            
        return (h, p1, p2)  
    
    def __retrieve(self, game):
        #in mirrortable, {normalhash, value}
        if game._board_state[-1] == None or game._board_state[-2] == None \
                or game._board_state[:-3].count(1) > 3:
            return [False, None]
        ha = [self.__normalhash(game), self.__updownmirror(game),
              self.__leftrightmirror(game), self.__diagonalmirror(game),
              self.__reversediagmirror(game)]
        for i in range(len(ha)):
            if ha[i] in self.mirrortable.keys():                
                return self.mirrortable[ha[i]]        
        return [False, None] 
         
    def __update(self, game, value, move):
        if game._board_state[-1] == None or game._board_state[-2] == None \
            or game._board_state[:-3].count(1) > 3:
            return
        ha = [self.__normalhash(game), self.__updownmirror(game),
              self.__leftrightmirror(game), self.__diagonalmirror(game),
              self.__reversediagmirror(game)]
        for i in range(len(ha)):
            if ha[i] in self.mirrortable.keys(): 
                self.mirrortable[ha[i]] = [value, move]
                return
        self.mirrortable[self.__normalhash(game)] = [value, move]      