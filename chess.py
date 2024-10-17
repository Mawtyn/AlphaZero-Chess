class ChessGame:
    def __init__(self):
        # Initialize a simple chess board with w for white pieces and b for black pieces
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],  # Black pieces
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Black pawns
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],  # Empty rows
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],          
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],          
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],          
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # White pawns
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],  # White pieces
        ]
        self.turn = "white"  # White moves first
        self.en_passant_target = None  # Track if en passant is possible
        
        # Track king positions
        self.white_king_position = (7, 4)  # Initial position of white king
        self.black_king_position = (0, 4)  # Initial position of black king
        
        # Tracking for castling eligibility
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_moved = {"left": False, "right": False}
        self.black_rook_moved = {"left": False, "right": False}
        
        
        # Add a list to store board positions
        self.position_history = []

    def print_board(self):
        print(" ")
        # Print the column numbers with proper spacing
        print("    0   1   2   3   4   5   6   7")  
        print("  +---+---+---+---+---+---+---+---+")  # Column borders
        # Print the board with row numbers and borders
        for i, row in enumerate(self.board):
            print(f"{i}| {'| '.join(row)} |")  # Row number with pieces
            print("  +---+---+---+---+---+---+---+---+")
        print("    0   1   2   3   4   5   6   7")  
        print(" ")
        
    def get_board_state(self):
        # Convert the current board state to a tuple of tuples (immutable)
        return tuple(tuple(row) for row in self.board)

    def update_position_history(self):
        # Add the current board state to the position history
        self.position_history.append(self.get_board_state())

    def is_threefold_repetition(self):
        current_state = self.get_board_state()
        return self.position_history.count(current_state) >= 3

    def is_valid_position(self, row, col):
        # Check if the row and column are within bounds of the 8x8 board
        return 0 <= row < 8 and 0 <= col < 8

    def is_piece_at_position(self, row, col):
        # Check if there's a piece at the given position (not an empty space '  ')
        return self.board[row][col] != "  "

    def is_own_piece(self, row, col):
        # Check if the selected piece belongs to the current player
        piece = self.board[row][col]
        if self.turn == "white" and piece.startswith('w'):
            return True
        elif self.turn == "black" and piece.startswith('b'):
            return True
        return False

    def get_legal_moves_for_pawn(self, row, col, piece):
        moves = set()
        direction = -1 if piece == "wp" else 1  # White pawns move up, black pawns move down
        
        # Regular forward move
        if self.is_valid_position(row + direction, col) and not self.is_piece_at_position(row + direction, col):
            moves.add((row + direction, col))
            # Double forward move on the first turn
            if (piece == "wp" and row == 6) or (piece == "bp" and row == 1):
                if not self.is_piece_at_position(row + 2 * direction, col):
                    moves.add((row + 2 * direction, col))
        
        # Capturing diagonally
        for diag_col in [col - 1, col + 1]:
            if self.is_valid_position(row + direction, diag_col):
                if self.is_piece_at_position(row + direction, diag_col):
                    if piece == "wp" and self.board[row + direction][diag_col].startswith('b'):
                        moves.add((row + direction, diag_col))
                    elif piece == "bp" and self.board[row + direction][diag_col].startswith('w'):
                        moves.add((row + direction, diag_col))
        
        # En passant
        if self.en_passant_target:
            if self.en_passant_target == (row + direction, col - 1) or self.en_passant_target == (row + direction, col + 1):
                moves.add(self.en_passant_target)

        return moves

    def get_legal_moves_for_king(self, row, col, piece):
        moves = set()
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Vertical and horizontal
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col):
                if not self.is_piece_at_position(new_row, new_col) or not self.is_own_piece(new_row, new_col):
                    moves.add((new_row, new_col))
        
        # Add castling moves
        moves.update(self.get_castling_moves())
        
        return moves
    
    
    def get_legal_moves_for_queen(self, row, col, piece):
        moves = set()
        
        # Directions: vertical, horizontal, and diagonal movements
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Vertical and horizontal
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            # Keep moving in the same direction until blocked or reaching the edge
            while self.is_valid_position(new_row, new_col):
                if not self.is_piece_at_position(new_row, new_col):  # Empty square
                    moves.add((new_row, new_col))
                elif not self.is_own_piece(new_row, new_col):  # Capture opponent's piece
                    moves.add((new_row, new_col))
                    break
                else:
                    break  # Blocked by own piece
                new_row += d_row
                new_col += d_col

        return moves
    
    def get_legal_moves_for_bishop(self, row, col, piece):
        moves = set()
        # Directions: Diagonal movements
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            while self.is_valid_position(new_row, new_col):
                if not self.is_piece_at_position(new_row, new_col):
                    moves.add((new_row, new_col))
                elif not self.is_own_piece(new_row, new_col):
                    moves.add((new_row, new_col))
                    break
                else:
                    break
                new_row += d_row
                new_col += d_col
        
        return moves
    
    
    def get_legal_moves_for_knight(self, row, col, piece):
        moves = set()
        # Possible knight moves (L-shaped)
        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),  # Vertical L-shapes
            (-1, -2), (-1, 2), (1, -2), (1, 2)   # Horizontal L-shapes
        ]
        
        for d_row, d_col in knight_moves:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col):
                if not self.is_piece_at_position(new_row, new_col) or not self.is_own_piece(new_row, new_col):
                    moves.add((new_row, new_col))
        
        return moves
    
    
    def get_legal_moves_for_rook(self, row, col, piece):
        moves = set()
        # Directions: Vertical and horizontal movements
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Vertical and horizontal
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            while self.is_valid_position(new_row, new_col):
                if not self.is_piece_at_position(new_row, new_col):
                    moves.add((new_row, new_col))
                elif not self.is_own_piece(new_row, new_col):
                    moves.add((new_row, new_col))
                    break
                else:
                    break
                new_row += d_row
                new_col += d_col
        
        return moves


    def get_legal_moves(self, row, col):
        piece = self.board[row][col]
        pseudo_legal_moves = set()

        if piece == "wp" or piece == "bp":
            pseudo_legal_moves = self.get_legal_moves_for_pawn(row, col, piece)
        elif piece == "wk" or piece == "bk":
            pseudo_legal_moves = self.get_legal_moves_for_king(row, col, piece)
        elif piece == "wq" or piece == "bq":
            pseudo_legal_moves = self.get_legal_moves_for_queen(row, col, piece)
        elif piece == "wr" or piece == "br":
            pseudo_legal_moves = self.get_legal_moves_for_rook(row, col, piece)
        elif piece == "wb" or piece == "bb":
            pseudo_legal_moves = self.get_legal_moves_for_bishop(row, col, piece)
        elif piece == "wn" or piece == "bn":
            pseudo_legal_moves = self.get_legal_moves_for_knight(row, col, piece)

        # Filter out moves that would put the king in check
        legal_moves = set()
        for move in pseudo_legal_moves:
            if self.is_move_safe(row, col, move[0], move[1]):
                legal_moves.add(move)

        return legal_moves
    
    def is_move_safe(self, src_row, src_col, dest_row, dest_col):
        # Save the current state
        piece = self.board[src_row][src_col]
        captured_piece = self.board[dest_row][dest_col]
        original_king_pos = self.white_king_position if piece.startswith('w') else self.black_king_position

        # Make the move
        self.board[dest_row][dest_col] = piece
        self.board[src_row][src_col] = "  "

        # Update king position if king is moved
        if piece in ["wk", "bk"]:
            if piece == "wk":
                self.white_king_position = (dest_row, dest_col)
            else:
                self.black_king_position = (dest_row, dest_col)

        # Check if the king is in check after the move
        king_in_check = self.is_king_in_check()

        # Undo the move
        self.board[src_row][src_col] = piece
        self.board[dest_row][dest_col] = captured_piece
        if piece in ["wk", "bk"]:
            if piece == "wk":
                self.white_king_position = original_king_pos
            else:
                self.black_king_position = original_king_pos

        # Return True if the move is safe (doesn't put or leave the king in check)
        return not king_in_check



    def move_piece(self, src_row, src_col, dest_row, dest_col):
        if not self.is_valid_position(src_row, src_col) or not self.is_valid_position(dest_row, dest_col):
            print("Invalid position. Try again.")
            return False

        piece = self.board[src_row][src_col]
        
        if piece == "  ":
            print("No piece at the source position. Try again.")
            return False
        
        if (self.turn == "white" and not piece.startswith('w')) or (self.turn == "black" and not piece.startswith('b')):
            print(f"It's {self.turn}'s turn. You can only move your own pieces.")
            return False

        legal_moves = self.get_legal_moves(src_row, src_col)
        if (dest_row, dest_col) not in legal_moves:
            print("Illegal move. Try again.")
            return False

        # Perform the move
        captured_piece = self.board[dest_row][dest_col]
        self.board[dest_row][dest_col] = piece
        self.board[src_row][src_col] = "  "

        # Handle castling
        if piece in ["wk", "bk"] and abs(dest_col - src_col) == 2:
            # Kingside castling
            if dest_col > src_col:
                rook_src_col, rook_dest_col = 7, 5
            # Queenside castling
            else:
                rook_src_col, rook_dest_col = 0, 3
            
            rook = self.board[src_row][rook_src_col]
            self.board[src_row][rook_dest_col] = rook
            self.board[src_row][rook_src_col] = "  "

        # Update king position
        if piece == "wk":
            self.white_king_position = (dest_row, dest_col)
        elif piece == "bk":
            self.black_king_position = (dest_row, dest_col)

        # Update castling eligibility
        if piece == "wk":
            self.white_king_moved = True
        elif piece == "bk":
            self.black_king_moved = True
        elif piece == "wr":
            if src_col == 0:
                self.white_rook_moved["left"] = True
            elif src_col == 7:
                self.white_rook_moved["right"] = True
        elif piece == "br":
            if src_col == 0:
                self.black_rook_moved["left"] = True
            elif src_col == 7:
                self.black_rook_moved["right"] = True

        # Handle en passant capture
        if self.en_passant_target and (dest_row, dest_col) == self.en_passant_target:
            if piece == "wp":
                self.board[dest_row + 1][dest_col] = "  "  # Remove black pawn
            elif piece == "bp":
                self.board[dest_row - 1][dest_col] = "  "  # Remove white pawn

        # Set up en passant target
        if piece in ["wp", "bp"] and abs(dest_row - src_row) == 2:
            self.en_passant_target = (int((src_row + dest_row) / 2), src_col)
        else:
            self.en_passant_target = None

        # Handle promotion
        if piece == "wp" and dest_row == 0:
            self.promote_pawn(dest_row, dest_col, "w")
        elif piece == "bp" and dest_row == 7:
            self.promote_pawn(dest_row, dest_col, "b")

        # Update position history for threefold repetition check
        self.update_position_history()

        # Switch turns
        self.turn = "black" if self.turn == "white" else "white"

        return True

    def promote_pawn(self, row, col, color):
        # Ask the player what piece they want to promote to
        while True:
            choice = input(f"Promote pawn at {row}{col} to (q)ueen, (n)ight, (r)ook, or (b)ishop: ").lower()
            if choice in ["q", "n", "r", "b"]:
                self.board[row][col] = color + choice
                break
            else:
                print("Invalid choice, please choose q, n, r, or b.")
                
    def get_all_possible_moves(self):
        all_moves = {}
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (self.turn == "white" and piece.startswith('w')) or (self.turn == "black" and piece.startswith('b')):
                    legal_moves = self.get_legal_moves(row, col)
                    if legal_moves:
                        all_moves[(row, col)] = legal_moves
        return all_moves

    def display_possible_moves(self):
        all_moves = self.get_all_possible_moves()
        print(f"\nPossible moves for {self.turn.capitalize()}:")
        for src, moves in all_moves.items():
            src_notation = f"{src[0]}{src[1]}"
            moves_notation = [f"{move[0]}{move[1]}" for move in moves]
            print(f"Piece at {src_notation}: {', '.join(moves_notation)}")
                
                
    def is_king_in_check(self):
        king_position = self.white_king_position if self.turn == "white" else self.black_king_position
        enemy_color = "b" if self.turn == "white" else "w"

        # Check for knight threats
        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for d_row, d_col in knight_moves:
            new_row, new_col = king_position[0] + d_row, king_position[1] + d_col
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == enemy_color + "n":
                return True

        # Check for rook and queen threats (horizontal and vertical)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in directions:
            new_row, new_col = king_position[0] + d_row, king_position[1] + d_col
            while self.is_valid_position(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece != "  ":
                    if piece[0] == enemy_color and piece[1] in "rq":
                        return True
                    break
                new_row += d_row
                new_col += d_col

        # Check for bishop and queen threats (diagonals)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d_row, d_col in directions:
            new_row, new_col = king_position[0] + d_row, king_position[1] + d_col
            while self.is_valid_position(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece != "  ":
                    if piece[0] == enemy_color:
                        if piece[1] in "bq":
                            return True
                        if piece[1] == "p" and abs(new_row - king_position[0]) == 1:
                            return True
                    break
                new_row += d_row
                new_col += d_col

        return False

    def get_moves_out_of_check(self):
        all_moves = self.get_all_possible_moves()
        moves_out_of_check = {}

        for src, moves in all_moves.items():
            for move in moves:
                # Simulate the move
                piece = self.board[src[0]][src[1]]
                captured_piece = self.board[move[0]][move[1]]
                self.board[move[0]][move[1]] = piece
                self.board[src[0]][src[1]] = "  "

                # Update king position if king is moved
                original_king_pos = None
                if piece == "wk":
                    original_king_pos = self.white_king_position
                    self.white_king_position = move
                elif piece == "bk":
                    original_king_pos = self.black_king_position
                    self.black_king_position = move

                # Check if the king is still in check after the move
                if not self.is_king_in_check():
                    if src not in moves_out_of_check:
                        moves_out_of_check[src] = set()
                    moves_out_of_check[src].add(move)

                # Undo the move
                self.board[src[0]][src[1]] = piece
                self.board[move[0]][move[1]] = captured_piece
                if original_king_pos:
                    if piece == "wk":
                        self.white_king_position = original_king_pos
                    else:
                        self.black_king_position = original_king_pos

        return moves_out_of_check

    def display_moves_out_of_check(self, moves):
        print(f"\nMoves to get out of check for {self.turn.capitalize()}:")
        for src, dest_moves in moves.items():
            src_notation = f"{src[0]}{src[1]}"
            moves_notation = [f"{move[0]}{move[1]}" for move in dest_moves]
            print(f"Piece at {src_notation}: {', '.join(moves_notation)}")

    def is_stalemate(self):
        if self.is_king_in_check():
            return False
        
        all_moves = self.get_all_possible_moves()
        return len(all_moves) == 0
    
    def is_square_under_attack(self, row, col, attacking_color):
        # Check for pawn attacks
        pawn_direction = 1 if attacking_color == 'w' else -1
        for d_col in [-1, 1]:
            if self.is_valid_position(row + pawn_direction, col + d_col):
                piece = self.board[row + pawn_direction][col + d_col]
                if piece == attacking_color + 'p':
                    return True

        # Check for knight attacks
        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for d_row, d_col in knight_moves:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == attacking_color + 'n':
                return True

        # Check for king attacks
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for d_row, d_col in king_moves:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == attacking_color + 'k':
                return True

        # Check for rook/queen attacks (horizontal and vertical)
        rook_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in rook_directions:
            new_row, new_col = row + d_row, col + d_col
            while self.is_valid_position(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece != "  ":
                    if piece[0] == attacking_color and piece[1] in "rq":
                        return True
                    break
                new_row += d_row
                new_col += d_col

        # Check for bishop/queen attacks (diagonals)
        bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d_row, d_col in bishop_directions:
            new_row, new_col = row + d_row, col + d_col
            while self.is_valid_position(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece != "  ":
                    if piece[0] == attacking_color and piece[1] in "bq":
                        return True
                    break
                new_row += d_row
                new_col += d_col

        return False
    
    
    def is_path_clear(self, start_col, end_col, row):
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if self.board[row][col] != "  ":
                return False
        return True

    def is_castling_safe(self, king_row, start_col, end_col):
        enemy_color = 'b' if self.turn == 'white' else 'w'
        step = 1 if end_col > start_col else -1
        for col in range(start_col, end_col + step, step):
            if self.is_square_under_attack(king_row, col, enemy_color):
                return False
        return True

    def get_castling_moves(self):
        castling_moves = set()
        king_row = 7 if self.turn == 'white' else 0
        king_col = 4

        # Kingside castling
        if not (self.white_king_moved if self.turn == 'white' else self.black_king_moved) and \
           not (self.white_rook_moved["right"] if self.turn == 'white' else self.black_rook_moved["right"]) and \
           self.is_path_clear(king_col, 7, king_row) and \
           self.is_castling_safe(king_row, king_col, king_col + 2):
            castling_moves.add((king_row, king_col + 2))

        # Queenside castling
        if not (self.white_king_moved if self.turn == 'white' else self.black_king_moved) and \
           not (self.white_rook_moved["left"] if self.turn == 'white' else self.black_rook_moved["left"]) and \
           self.is_path_clear(king_col, 0, king_row) and \
           self.is_castling_safe(king_row, king_col, king_col - 2):
            castling_moves.add((king_row, king_col - 2))
            
        return castling_moves
    
    
    def is_checkmate(self, color):
        if not self.is_king_in_check():
            return False
        
        # Check if any move can get the king out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (color == 'white' and piece.startswith('w')) or (color == 'black' and piece.startswith('b')):
                    legal_moves = self.get_legal_moves(row, col)
                    if legal_moves:
                        return False  # If there's any legal move, it's not checkmate
        
        return True  # No legal moves to escape check

    def is_game_over(self):
        if self.is_checkmate('white'):
            print("Checkmate! Black wins!")
            return True
        elif self.is_checkmate('black'):
            print("Checkmate! White wins!")
            return True
        elif self.is_stalemate():
            print("Stalemate! The game is a draw.")
            return True
        elif self.is_threefold_repetition():
            print("Threefold repetition! The game is a draw.")
            return True
        return False


    def play(self):
        # Main game loop
        while True:
            self.print_board()  # Print the board before each move
            
            
            if self.is_game_over():
                break
            
            # Check if the current player's king is in check
            if self.is_king_in_check():
                print(f"{self.turn.capitalize()}'s king is in check!")
                moves_out_of_check = self.get_moves_out_of_check()
                if not moves_out_of_check:
                    print(f"Checkmate! {self.turn.capitalize()} has no legal moves. {'Black' if self.turn == 'white' else 'White'} wins!")
                    break
                self.display_moves_out_of_check(moves_out_of_check)
            else:
                # Check for stalemate
                if self.is_stalemate():
                    print(f"Stalemate! {self.turn.capitalize()} has no legal moves. The game is a draw.")
                    break
                # Display all possible moves when not in check
                self.display_possible_moves()
            
            try:
                # Ask for the source position (row and column) as a combined input like "66"
                src = input(f"{self.turn.capitalize()}'s move: Select piece to move (e.g., '66'): ")
                if len(src) != 2 or not src.isdigit():
                    raise ValueError
                src_row, src_col = int(src[0]), int(src[1])

                # Check if there's a piece at the selected source position
                if not self.is_piece_at_position(src_row, src_col):
                    print("No piece at the selected location. Try again.")
                    continue

                # Check if the selected piece belongs to the current player
                if not self.is_own_piece(src_row, src_col):
                    print(f"Invalid move: You must select your own piece. It's {self.turn}'s turn.")
                    continue

                # Get legal moves for the selected piece
                if self.is_king_in_check():
                    legal_moves = moves_out_of_check.get((src_row, src_col), set())
                else:
                    legal_moves = self.get_legal_moves(src_row, src_col)

                legal_moves_notation = {f"{r}{c}" for r, c in legal_moves}
                print(f"Legal moves for the selected piece at ({src_row}{src_col}): {legal_moves_notation}")

                # Ask for the destination position (row and column) as a combined input like "44"
                dest = input(f"Move piece from ({src_row}{src_col}) to (e.g., '44'): ")
                if len(dest) != 2 or not dest.isdigit():
                    raise ValueError
                dest_row, dest_col = int(dest[0]), int(dest[1])

                # Check if the destination is a legal move
                if (dest_row, dest_col) not in legal_moves:
                    print("Invalid move: Not a legal move.")
                    continue

            except (ValueError, IndexError):
                print("Invalid input. Please enter two digits (e.g., '66').")
                continue

            # Move the piece and check for validity
            if not self.move_piece(src_row, src_col, dest_row, dest_col):
                print("Try again.")
        
if __name__ == "__main__":
    game = ChessGame()
    game.play()