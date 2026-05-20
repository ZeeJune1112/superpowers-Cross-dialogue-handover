import pytest
from game import Game2048


def test_init_spawns_two_tiles():
    game = Game2048()
    non_zero = sum(1 for r in range(4) for c in range(4) if game.grid[r][c] != 0)
    assert non_zero == 2


def test_init_score_zero():
    game = Game2048()
    assert game.score == 0


def test_spawn_adds_tile_on_empty_grid():
    game = Game2048()
    game.grid = [[0] * 4 for _ in range(4)]
    game.spawn()
    non_zero = sum(1 for r in range(4) for c in range(4) if game.grid[r][c] != 0)
    assert non_zero == 1


def test_spawn_values_are_2_or_4():
    game = Game2048()
    game.grid = [[0] * 4 for _ in range(4)]
    for _ in range(50):
        game.grid = [[0] * 4 for _ in range(4)]
        game.spawn()
        val = next(v for row in game.grid for v in row if v != 0)
        assert val in (2, 4)


def test_move_left_merges_equal_tiles():
    game = Game2048()
    game.grid = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(0)
    assert game.grid[0][0] == 4
    assert game.score == 4


def test_move_left_slides_tiles():
    game = Game2048()
    game.grid = [[0, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.move(0)
    assert game.grid[0][0] == 2


def test_move_right_merges_equal_tiles():
    game = Game2048()
    game.grid = [[0, 0, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(1)
    assert game.grid[0][3] == 4
    assert game.score == 4


def test_move_up_merges_equal_tiles():
    game = Game2048()
    game.grid = [[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(2)
    assert game.grid[0][0] == 4
    assert game.score == 4


def test_move_down_merges_equal_tiles():
    game = Game2048()
    game.grid = [[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(3)
    assert game.grid[3][0] == 4
    assert game.score == 4


def test_no_merge_different_values():
    game = Game2048()
    game.grid = [[2, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.move(0)
    assert game.grid[0][0] == 2
    assert game.grid[0][1] == 4


def test_double_merge_in_one_move():
    game = Game2048()
    game.grid = [[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(0)
    assert game.grid[0][0] == 4
    assert game.grid[0][1] == 4
    assert game.score == 8


def test_triple_merge_left():
    """2,2,2,0 sliding left -> 4,2,0,0 (first pair merges, third stays)"""
    game = Game2048()
    game.grid = [[2, 2, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.score = 0
    game.move(0)
    assert game.grid[0][0] == 4
    assert game.grid[0][1] == 2
    assert game.score == 4


def test_move_returns_true_when_grid_changes():
    game = Game2048()
    game.grid = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert game.move(3)  # move down, tile slides


def test_move_returns_false_when_no_change():
    game = Game2048()
    game.grid = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert not game.move(0)  # move left, tile already at leftmost


def test_move_spawns_new_tile_when_changed():
    game = Game2048()
    game.grid = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    game.move(3)  # move down
    non_zero = sum(1 for r in range(4) for c in range(4) if game.grid[r][c] != 0)
    assert non_zero == 2  # original + new spawn


def test_is_game_over_false_initially():
    game = Game2048()
    assert not game.is_game_over()


def test_is_game_over_true_when_full_no_moves():
    game = Game2048()
    game.grid = [
        [2, 4, 8, 16],
        [16, 8, 4, 2],
        [2, 4, 8, 16],
        [16, 8, 4, 2],
    ]
    assert game.is_game_over()


def test_is_game_over_false_when_merge_possible():
    game = Game2048()
    game.grid = [
        [2, 4, 8, 16],
        [16, 8, 4, 2],
        [2, 4, 8, 16],
        [16, 8, 2, 2],
    ]
    assert not game.is_game_over()


def test_has_won_detects_2048():
    game = Game2048()
    game.grid = [
        [2048, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    assert game.has_won()


def test_has_won_detects_super_tile():
    game = Game2048()
    game.grid = [
        [4096, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    assert game.has_won()
