#! /usr/bin/env python

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

import go
import tui
import sys

if len(sys.argv) < 2:
    board = go.Board()
else :
    board = go.Board(int(sys.argv[1]))

tui.display(board)

try:
    while True:

        try:
            move = tui.read_move()
        except tui.ExitException:
            sys.exit(0)
        except ValueError as v:
            print "Illegal input"
            continue
  
        try:
            board.place(move)
        except go.IllegalMoveError as i:
            print "Illegal move:", i
            continue

        tui.display(board)
        print "score: ", board.score()

except KeyboardInterrupt:
    print ""
    sys.exit(0)
