import pygame
import sys
import random

"""
TO DO
winner screen
double jumps
Big chungus
print move indicators
add score gui???
Turn system
"""

# Setup of the Game Window
pygame.init()

ROWS, COLS = 8, 8
TILE_SIZE = 80
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

# Game Parameters
LIGHT_SQUARE = (237, 214, 176)
DARK_SQUARE = (184, 135, 98)
HIGHLIGHT_COLOR = (219, 195, 74)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers!")

# Initializing the Sprites
light_pieces_image = pygame.transform.scale(pygame.image.load("sprites/white.png").convert_alpha(), (TILE_SIZE - 10, TILE_SIZE - 10))
light_king_image = pygame.transform.scale(pygame.image.load("sprites/white_king.png").convert_alpha(), (TILE_SIZE - 10, TILE_SIZE - 10))
dark_pieces_image = pygame.transform.scale(pygame.image.load("sprites/black.png").convert_alpha(), (TILE_SIZE - 10, TILE_SIZE - 10))
dark_king_image = pygame.transform.scale(pygame.image.load("sprites/black_king.png").convert_alpha(), (TILE_SIZE - 10, TILE_SIZE - 10))
move_indicator_image = pygame.image.load("sprites/move_indicator.png").convert_alpha()

# Setting up the starting board state. 0 = empty, 1 = player 1, and 2 = player 2. 3 and 4 are player 1 and 2 but a king piece
board_state = [
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2 ,0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1 ,0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],  
    [1, 0, 1, 0, 1 ,0, 1, 0] 
    ]



# Game Functions
def draw_board():
    # Draws the squares on the board
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 0:
                color = LIGHT_SQUARE
            else:
                color = DARK_SQUARE

            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

def draw_pieces():
    # Draws the pieces based on what the board state shows
    for row in range(ROWS):
        for col in range(COLS):
            piece = board_state[row][col]
            if piece != 0:
                x = col * TILE_SIZE + 5
                y = row * TILE_SIZE + 5
                
                if piece == 1:
                    screen.blit(dark_pieces_image, (x, y))
                elif piece == 2:
                    screen.blit(light_pieces_image, (x, y))
                elif piece == 3:
                    screen.blit(dark_king_image, (x, y))
                elif piece == 4:
                    screen.blit(light_king_image, (x, y))

def get_square_from_mouse(pos):
    # Returns the row and col that the mouse is on
    x, y = pos
    row = y // TILE_SIZE
    col = x // TILE_SIZE
    return row, col

def move_piece(start_row, start_col, end_row, end_col):
    # Moves the value at the start pos to the end pos and empties the start pos
    piece = board_state[start_row][start_col]
    board_state[start_row][start_col] = 0

    # Logic if the move is a capture
    if is_capture(start_row, start_col, end_row, end_col, piece):
        board_state[(start_row + end_row) // 2][(start_col + end_col) // 2] = 0
    
    if is_promotion(end_row, piece):
        board_state[end_row][end_col] = piece + 2
    else:
        board_state[end_row][end_col] = piece

def is_legal_move(start_row, start_col, end_row, end_col, piece=0):
    # Checks if the proposed move is legal and returns True if it is legal and False if it isn't
    """
    Ways for a move to not be legal:
    - There is a piece on that square
    - The proposed move isn't a capture when one is avaliable
    - It is not a diagonal move (Remember that 3 and 4 are kings and can go backwards)
    """
    # If there is a piece on that square
    if board_state[end_row][end_col] > 0:
        return False
    # If the move is diagonal
    row_delta = end_row - start_row
    col_delta = end_col - start_col
    # Logic for the dark pieces, has to move forward and one square to the left or right
    if piece == 1:
        if (row_delta == -1 and abs(col_delta) == 1) or (row_delta == -2 and is_capture(start_row, start_col, end_row, end_col, piece)):
            return True
    if piece == 2:
        if (row_delta == 1 and abs(col_delta) == 1) or (row_delta == 2 and is_capture(start_row, start_col, end_row, end_col, piece)):
            return True
    # Logic for the kings
    if piece == 3 or piece == 4:
        if abs(row_delta) == 1 and abs(col_delta) == 1 or is_capture(start_row, start_col, end_row, end_col, piece):
            return True
    return False

def is_capture(start_row, start_col, end_row, end_col, piece):
    row_delta = end_row - start_row
    col_delta = end_col - start_col
    # Return False if there isn't at least 1 square inbetween the 2 squares
    if abs(row_delta) != 2 or abs(col_delta) != 2:
        return False
    target_square = board_state[(start_row + end_row) // 2][(start_col + end_col) // 2]
    if target_square == 0:
        return False
    # If the square inbetween the 2 squares contains a piece that isn't the same color or the same color king then return True
    if piece == 1 or piece == 2:
        if target_square != piece and target_square != piece + 2:
            return True
    if piece == 3 or piece == 4:
        if target_square != piece and target_square != piece - 2:
            return True
    return False

def get_legal_moves(player):
    captures, simple = [], []
    # Every destination that a piece could possibly reach
    offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1),
               (-2, -2), (-2, 2), (2, -2), (2, 2)]
    for row in range(ROWS):
        for col in range(COLS):
            piece = board_state[row][col]

            # Only look at this player's pieces
            if piece != player and piece != player + 2:
                continue

            for row_delta, col_delta in offsets:
                end_row, end_col = row + row_delta, col + col_delta

                # Skip off-board destinations
                if not (0 <= end_row < ROWS and 0 <= end_col < COLS):
                    continue

                # Skip non legal moves
                if not is_legal_move(row, col, end_row, end_col, piece):
                    continue

                move = (row, col, end_row, end_col)
                # Adds the move to the corresponding list based on the type of move
                if is_capture(row, col, end_row, end_col, piece):
                    captures.append(move)
                else:
                    simple.append(move)

    # Return captures with priority over the simple moves
    return captures if captures else simple

def ai_move():
    move = random.choice(legal_moves)
    move_piece(*move)
    end_turn()

def end_turn():
    global current_player, legal_moves, selected_piece, game_over, winner
    selected_piece = None
    current_player = 2 if current_player == 1 else 1
    legal_moves = get_legal_moves(current_player)

    if len(legal_moves) == 0:
        game_over = True
        winner = 1 if current_player == 2 else 2

def is_promotion(end_row, piece):
    if piece == 1 or piece == 2:
        if piece == 1 and end_row == 0:
            return True
        if piece == 2 and end_row == ROWS - 1:
            return True
    return False


# Setup of the Game Loop
run = True
current_player = 1                       
player_types = {1: "human", 2: "human"}
legal_moves = get_legal_moves(current_player)
selected_piece = None
game_over = False
winner = None
while run:
    # Setup of the Event Handler
    for event in pygame.event.get():
        # Listen for pressing the X button
        if event.type == pygame.QUIT:
            run = False

        # Listen for Left Click and that the game isn't over and that the current player is a human
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and player_types[current_player] == "human"):
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_square_from_mouse(mouse_pos)

                # Check boundaries to ensure click was inside the grid
                if 0 <= row < ROWS and 0 <= col < COLS:
                    # If there is a current selected piece, it moves the piece to the clicked location, otherwise it sets a new selected piece
                    if selected_piece == None:
                        if board_state[row][col] == current_player or board_state[row][col] == current_player + 2:
                            selected_piece = (row, col)
                    else:
                        move = selected_piece[0], selected_piece[1], row, col
                        if move in legal_moves:
                            move_piece(*move)
                            end_turn()
                        else:
                            selected_piece = None

    if not game_over and player_types[current_player] == "ai":
        pygame.time.wait(500)
        ai_move()
    
    # Rendering
    screen.fill((0, 0, 0))

    draw_board()
    draw_pieces()


    pygame.display.update()
pygame.quit()

