from board import Board
# from fcsolver import Solver
from macsolver import Solver

if __name__ == '__main__':
    n = input().split()
    solver = Solver(n[0])
    board = Board(int(n[0]), solver)
    solver.set_board(board)
    solved = solver.solve()
    if solved:
        for i in range(int(n[0])):
            for j in range(int(n[0])):
                print(board.board[i, j].value, end=' ')
            print()
    else:
        print('No way!')
