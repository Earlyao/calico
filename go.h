/*
 * Copyright (C) 2011 Nick Johnson <nickbjohnson4224 at gmail.com>
 * 
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#ifndef GO_H
#define GO_H

#include <stdint.h>

#define PASS (-1)

#define WHITE (-1)
#define BLACK 1
#define EMPTY 0
#define INVAL 2

#define GO_DIM 9

struct go_piece {
	int16_t group;
	int16_t libs;
	int8_t color;
	int8_t rank;
};

struct go_board {
	struct go_piece pos[GO_DIM * GO_DIM];
	int ko;
	int player;
	int last;
};

struct go_board *new_board  (void);
struct go_board *clone_board(const struct go_board *board);

int get_pos(int x, int y);
int get_color(const struct go_board *board, int pos);
int get_libs(struct go_board *board, int pos);

int gen_adj(void);
int get_adj(int pos, int dir);

int place(struct go_board *board, int pos, int player);
int check(struct go_board *board, int pos, int player);
int score(struct go_board *board);

void print(struct go_board *board);

#endif/*GO_H*/
