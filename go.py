# Copyright (C) 2011 Nick Johnson <nickbjohnson4224 at gmail.com>
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# piece states / player colors
EMPTY = 0
BLACK = 1
WHITE = -1

class IllegalMoveError(Exception):

    def __init__(self, pos, player, reason):
        self.pos = pos
        self.reason = reason
        self.player = player

    def __str__(self):

        if self.player == WHITE:
            player_name = "white"
        elif self.player == BLACK:
            player_name = "black"
        elif self.player == EMPTY:
            player_name = "empty"
        else:
            player_name = "invalid"
        
        return "(%d %d %s) : %s" % (self.pos[0], self.pos[1], player_name, self.reason)

# represents a piece on the board
class Piece:

    def __init__(self, color = EMPTY):

        self.color = color
        self.group = self
        self.libs = 0
        self.rank = 0

    def get_libs(self):
        return self.get_group().libs

    def set_libs(self, libs = 0):
        self.get_group().libs = libs

    def add_libs(self, libs = 0):
        self.get_group().libs += libs

    def set_group(self, group = None):
        if not group: group = self
        self.group = group

    def get_group(self):

        if self.group != self:
            self.group = self.group.get_group()
            return self.group
        else:
            return self

    def merge_group(self, group):

        group1 = self.get_group()
        group2 = group.get_group()

        if group1 != group2:
            libs = group1.libs + group2.libs;

            if group1.rank < group2.rank:
                group1.group = group2
                group2.libs += group1.libs
            elif group2.rank < group1.rank:
                group2.group = group1
                group1.libs += group2.libs
            else:
                group1.group = group2
                group2.libs += group1.libs
                group2.rank += 1

# represents a Go board
class Board:
    
    def __init__(self, xdim = 19, ydim = 19):

        self.board = []
        self.xdim = xdim
        self.ydim = ydim
        self.last = None
        self.llast = None
        self.player = BLACK
        self.ko = None

        for i in range(0, xdim):
            self.board += [[]]
            for j in range(0, ydim):
                self.board[i] += [ Piece() ]

    def __copy__(self):
        
        new = Board(self.xdim, self.ydim)

        for x in range(1, self.xdim + 1):
            for y in range(1, self.ydim + 1):
                new.place_unchecked((x, y), self.get((x, y)).color)

        new.last = self.last
        new.llast = self.llast
        new.player = self.player
        new.ko = self.ko

        return new

    def get(self, pos): 

        return self.board[pos[0] - 1][pos[1] - 1]

    def validate_pos(self, pos):

        if not pos:
            return None

        if pos[0] < 1 or pos[1] < 1 or pos[0] > self.xdim or pos[1] > self.ydim:
            return None

        return pos

    _adj_table = [ [1, 0], [0, 1], [-1, 0], [0, -1] ]

    def get_adj_pos(self, pos, direction):
        
        if not pos:
            return None

        if direction == 0:
            return self.validate_pos((pos.x + 1, pos.y))
        if direction == 1:
            return self.validate_pos((pos.x, pos.y + 1))
        if direction == 2:
            return self.validate_pos((pos.x - 1, pos.y))
        if direction == 3:
            return self.validate_pos((pos.x, pos.y - 1))

    def get_adj_list(self, pos):
        
        adj = []

        if pos[0] < self.xdim:
            adj += [ (pos[0] + 1, pos[1]) ]

        if pos[1] < self.ydim:
            adj += [ (pos[0], pos[1] + 1) ]

        if pos[0] > 1:
            adj += [ (pos[0] - 1, pos[1]) ]

        if pos[1] > 1:
            adj += [ (pos[0], pos[1] - 1) ]

        return adj

    def capture(self, pos):

        if not self.get(pos):
            return

        color = self.get(pos).color
        self.get(pos).color = EMPTY
        self.get(pos).group = self.get(pos)
        self.get(pos).libs  = 0
        self.get(pos).rank  = 0

        for i in self.get_adj_list(pos):
            color1 = self.get(i).color
            if color1 == -color:
                self.get(i).add_libs(1)
            elif color1 == color:
                self.capture(i)
    
    def place_unchecked(self, pos, player):
        
        if not pos or not self.get(pos) or not player:
            return

        self.ko = None
        adj = []

        # get adjacent groups
        adj = self.get_adj_list(pos)

        # reduce liberties of all adjacent groups
        for i in adj:
            self.get(i).add_libs(-1)
        
        libs = 0
        for i in adj:
            color = self.get(i).color

            # capture all adjacent enemy groups with no liberties
            if color == -player:
                if self.get(i).get_libs() <= 0:
                    self.capture(i)
                    self.ko = pos
                    libs += 1

            # count liberties of added piece
            elif color == EMPTY:
                libs += 1
        
        self.get(pos).libs  = libs
        self.get(pos).color = player
        self.get(pos).group = self.get(pos)
        self.get(pos).rank  = 0

        # merge with adjacent allied groups
        for i in adj:
            if self.get(i).color == player:
                self.get(pos).merge_group(self.get(i))
                self.ko = None

        self.llast = self.last
        self.last = pos

    def check(self, pos, player):

        if not pos: return

        if not self.validate_pos(pos):
            raise IllegalMoveError(pos, player, "position not on board")

        # make sure space is open
        if self.get(pos).color != EMPTY:
            raise IllegalMoveError(pos, player, "position not empty")

        # make sure there are no ko captures
        if self.ko and self.get(self.ko).get_libs() == 1:
            for i in self.get_adj_list(pos):
                if i == self.ko:
                    raise IllegalMoveError(pos, player, "ko capture")

        # make sure there is no suicide
        for i in self.get_adj_list(pos):

            if self.get(i).color == EMPTY:
                return
            
            libs_taken = 0

            for j in self.get_adj_list(pos):
                if self.get(j).group == self.get(i).group:
                    libs_taken += 1
            
            if self.get(i).color == player:
                if libs_taken < self.get(i).get_libs():
                    return

            elif self.get(i).color == -player:
                if libs_taken == self.get(i).get_libs():
                    return
        
        raise IllegalMoveError(pos, player, "suicide move")

    def check_fast(self, pos, player):

        if not pos: return True

        if not self.validate_pos(pos):
            return False

        # make sure space is open
        if self.get(pos).color != EMPTY:
            return False

        # make sure there are no ko captures
        if self.ko and self.get(self.ko).get_libs() == 1:
            for i in self.get_adj_list(pos):
                if i == self.ko: return False

        # make sure there is no suicide
        for i in self.get_adj_list(pos):

            if self.get(i).color == EMPTY:
                return True
            
            libs_taken = 0

            for j in self.get_adj_list(pos):
                if self.get(j).group == self.get(i).group:
                    libs_taken += 1
            
            if self.get(i).color == player:
                if libs_taken < self.get(i).get_libs():
                    return True

            elif self.get(i).color == -player:
                if libs_taken == self.get(i).get_libs():
                    return True
        
        return False

    def place(self, pos, player = None):
        
        if not player: player = self.player

        if not player in ( BLACK, WHITE ):
            raise IllegalMoveError(pos, player, "invalid player")

        self.check(pos, player)
        self.place_unchecked(pos, player)
        self.player = -player

    def score(self):
        
        b = 0
        w = 0
        for x in range(1, self.xdim + 1):
            for y in range(1, self.ydim + 1):
                pos = (x, y)

                if self.get(pos).color == WHITE:
                    w += 1
                elif self.get(pos).color == BLACK:
                    b += 1
                else:
                    for j in self.get_adj_list(pos):
                        if self.get(j).color == BLACK:
                            b += 1
                        elif self.get(j).color == WHITE:
                            w += 1

        return [ b - w, b, w ]
