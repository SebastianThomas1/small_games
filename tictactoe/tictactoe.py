# Sebastian Thomas (coding at sebastianthomas dot de)

# type hints
from typing import NoReturn, Union

# iteration
from itertools import product as cart


class TicTacToe:
    """Implements the classical tic-tac-toe game."""

    def __init__(self):
        """Initializes tic-tac-toe game."""
        self._board: list[list[Union[None, bool]]] = [[None]*3
                                                      for _ in range(3)]
        self._first_player_active = True
        # (whether player 1 has won, whether player 2 has won)
        self._status = (False, False)

    @staticmethod
    def _pos(row_idx: int, col_idx: int) -> int:
        return row_idx * 3 + col_idx + 1

    @staticmethod
    def _index(pos: int) -> tuple[int, int]:
        return divmod(pos - 1, 3)

    def _print_board(self) -> NoReturn:
        print('\n'.join(' '.join(str(self._pos(row_idx, col_idx))
                                 if self._board[row_idx][col_idx] is None
                                 else ('X' if self._board[row_idx][col_idx]
                                       else 'O')
                                 for col_idx in range(3))
                        for row_idx in range(3)))

    def _is_finished(self) -> bool:
        return self._status[0] or self._status[1]

    def _is_free(self, pos: int) -> bool:
        row_idx, col_idx = self._index(pos)
        return self._board[row_idx][col_idx] is None

    def _is_valid(self, pos_rep: str) -> bool:
        return (pos_rep.isdigit() and len(pos_rep) == 1
                and self._is_free(int(pos_rep)))

    def _ask_for_position(self) -> int:
        while True:
            pos_rep = input('Player {}, where will you play? '
                            .format('1 (X)' if self._first_player_active
                                    else '2 (O)'))
            if self._is_valid(pos_rep):
                return int(pos_rep)
            else:
                print('Invalid input!')

    def _update_board(self, pos: int) -> NoReturn:
        row_idx, col_idx = self._index(pos)
        self._board[row_idx][col_idx] = self._first_player_active

    def _is_won(self, pos: int) -> bool:
        row_idx, col_idx = self._index(pos)

        # check row and column of pos
        result = (all(self._board[row_idx][c] == self._first_player_active
                      for c in range(3))
                  or all(self._board[r][col_idx] == self._first_player_active
                         for r in range(3)))

        # check main diagonal if pos is on main diagonal
        if not result and row_idx == col_idx:
            result = (result
                      or all(self._board[idx][idx] == self._first_player_active
                             for idx in range(3)))
        # check side diagonal if pos is on side diagonal
        if not result and row_idx == 2 - col_idx:
            result = (result
                      or all(self._board[idx][2 - idx]
                             == self._first_player_active
                             for idx in range(3)))

        return result

    def _is_tie(self):
        return all(self._board[row_idx][col_idx] is not None
                   for (row_idx, col_idx) in cart(range(3), range(3)))

    def _update_status(self, pos):
        if self._is_won(pos):
            self._status = ((True, False) if self._first_player_active
                            else (False, True))
        elif self._is_tie():
            self._status = (True, True)

    def _print_result(self):
        if self._status == (True, True):
            print('\nGame resulted in a tie... like usual.')
        elif self._status == (True, False):
            print('\nPlayer 1 Wins!!')
        elif self._status == (False, True):
            print('\nPlayer 2 Wins!!')

    def run(self):
        print('TicTacToe')
        print('---------\n')

        self._print_board()

        while not self._is_finished():
            pos = self._ask_for_position()
            self._update_board(pos)
            self._print_board()
            self._update_status(pos)
            self._first_player_active = not self._first_player_active

        self._print_result()

        # reset instance fields
        self.__init__()


if __name__ == '__main__':
    TicTacToe().run()
