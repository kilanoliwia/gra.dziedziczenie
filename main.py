import pygame
import sys

pygame.init()

window_size = 800
square_size = window_size // 8
black = (0, 0, 0)
pink = (232, 64, 170)
white = (255, 255, 255)
red = (255, 0, 0) # podswietlenie pionka
piece_radius = square_size // 2 - 10

screen = pygame.display.set_mode((window_size, window_size))
pygame.display.set_caption("WARCABY")

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = 0
        self.y = 0
        self.selected = False
        self.king = False
        self.calc_pos()

    def calc_pos(self): #oblicza wierszy kolumny x,y
        self.x = square_size * self.col + square_size // 2
        self.y = square_size * self.row + square_size // 2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), piece_radius)
        if self.selected:
            pygame.draw.circle(screen, red, (self.x, self.y), piece_radius + 2, 2)
        if self.king:
            pygame.draw.circle(screen, (255, 215, 0),(self.x, self.y), piece_radius - 10) #złoty obrys dla damki

    def move(self, row, col): #przesuwa pionek na inna pozycje
        self.row = row
        self.col = col
        self.calc_pos()

    def make_king(self):
        self.king = True

class Board:
    def __init__(self):
        self.board = []
        self.selected_piece = None
        self.pink_turn = True #rozowe zaczynja
        self.valid_moves = {}
        self.create_board()

    def create_board(self): #ustawia pionki
        for row in range(8):
            self.board.append([])
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, white))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, pink))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, screen): #rysuje plansze i pionki
        self.draw_squares(screen)
        self.draw_pieces(screen)
        self.draw_valid_moves(screen)

    def draw_squares(self, screen): #rysujeszachownice
        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = row * square_size
                color = pink if (row + col) % 2 == 0 else black
                pygame.draw.rect(screen, color, (x, y, square_size, square_size))

    def draw_pieces(self, screen):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None:
                    piece.draw(screen)

    def draw_valid_moves(self, screen): #podswietla mozliwe ruchy dla gracza
        for move, captured in self.valid_moves.items():
            row, col = move
            pygame.draw.circle(screen, red, (col * square_size + square_size //2,
                                             row * square_size + square_size // 2), 15)

    def get_piece(self, row, col): #zwraca pionej z pozycji
        if 0 <= row < 8 and 0 <= col <8:
            return self.board[row][col]
        return None

    def move(self, piece, row, col): #ruch pionka
        self.board[piece.row][piece.col], self.board[row][col] = None, piece
        captured = self.valid_moves[(row, col)]
        piece.move(row, col)

        if row == 0 and piece.color == pink:
            piece.make_king()
        if row == 7 and piece.color == white:
            piece.make_king()

        for capture in captured:
            middle_row, middle_col = capture
            self.board[middle_row][middle_col] = None


    def get_valid_moves(self, piece): #zwraca slownik mozliwych ruchow dla danego pionka
        moves = {}
        row = piece.row
        col = piece.col

        if piece.king:
            directions = [(1,1), (1, -1), (-1, 1), (-1, -1)]
            for direction in directions:
                self._check_king_moves(piece.row, piece.col, direction, moves)
        else:
            #kierunek ruchu góra/dół w zal. od koloru
            direction = -1 if piece.color == pink else 1
            #sprawdz ruchy po skosie
            self._check_diagonal_moves(row, col, direction, moves)
            #sprawdz mozliwe bicia
            self._check_jumps(row, col, direction, moves)

        return moves

    def _check_king_moves(self, row, col, direction, moves): #sprawdza ruchy dla damki
        dr, dc = direction
        cur_row, cur_col = row + dr, col + dc
        while self._is_valid_position(cur_row, cur_col):
            current_piece = self.get_piece(cur_row, cur_col)
            if current_piece is None: #puste pole- mozliwy ruch
                moves[(cur_row, cur_col)] = []
            elif current_piece.color == self.get_piece(row, col).color:
                break # pionek tego samego koloru - przerywamy
            else:
                #pionek przeciwnika - sprawdzamy mozliwosc bicia
                jump_row, jump_col = cur_row + dr, cur_col + dc
                if (self._is_valid_position(jump_row, jump_col) and
                        self.get_piece(jump_row, jump_col) is None):
                    moves[(jump_row, jump_col)] = [(cur_row, cur_col)]
                break
            cur_row += dr
            cur_col += dc

    def _check_diagonal_moves(self, row, col, direction, moves): #sprawdza mozliwe ruchy po skosie
        for dc in [-1, 1]:
            new_row = row + direction
            new_col = col + dc
            if self._is_valid_position(new_row, new_col) and self.get_piece(new_row, new_col) is None:
                moves[(new_row, new_col)] = []

    def _check_jumps(self, row, col, direction, moves): #sprawdza mozliwe bicia

        piece = self.get_piece(row, col)

        for dc in [-1, 1]:
            mid_row = row + direction
            mid_col = col + dc
            end_row = mid_row + direction
            end_col = mid_col + dc

            if self._is_valid_position(end_row, end_col):
                mid_piece = self.get_piece(mid_row, mid_col)
                end_piece = self.get_piece(end_row, end_col)

                if (mid_piece is not None and
                        mid_piece.color != self.get_piece(row, col).color and
                        end_piece is None):
                    moves[(end_row, end_col)] = [(mid_row, mid_col)]

    def _is_valid_position(self, row, col): #sprawdza czy pozycja jest na planszy
        return 0 <= row < 8 and 0 <= col < 8

    def select(self, row, col): #obsluguje wybor pionka i wyk. ruchu
        piece = self.get_piece(row, col)

        #jesli jest juz wybrany
        if self.selected_piece:
            result = self._move(row, col) #wyk. ruch
            if not result: #jesli sie nie udal, wyb nowy pionek
                self.selected_piece = None
                self.select(row, col)
            return

        #wyb. nowy pionek
        if piece is not None and piece.color == (pink if self.pink_turn else white):
            self.selected_piece = piece
            piece.selected = True
            self.valid_moves = self.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col): #probuje wykonac ruch na wybrana pozycje
        piece = self.selected_piece

        if piece and (row, col) in self.valid_moves:
            self.move(piece, row, col)
            self.pink_turn = not self.pink_turn
            self.selected_piece.selected = False
            self.selected_piece = None
            self.valid_moves = {}
            return True
        return False

    def show_simple_popup(self, screen, winner_text):
        popup_width, popup_height = 300, 150
        popup_color = (236, 109, 170)
        shadow_color = (236, 211, 225)
        text_color = (255, 255, 255)
        button_color = (255, 176, 225)
        button_hover_color = (250, 221, 225)
        button_text_color = (255, 255, 255)
        button_shadow_color = (250, 221, 225)

        # rozmieszczenie okienka
        popup_x = (screen.get_width() - popup_width) // 2
        popup_y = (screen.get_height() - popup_height) // 2

        # przycisk kontynuuj
        continue_button_rect = pygame.Rect(popup_x + 30, popup_y + 80, 100, 40)
        # przycisk zakoncz
        exit_button_rect = pygame.Rect(popup_x + 170, popup_y + 80, 100, 40)

        font = pygame.font.Font(None, 36)
        button_font = pygame.font.Font(None, 28)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button_rect.collidepoint(event.pos):
                        return "continue"
                    elif exit_button_rect.collidepoint(event.pos):
                        return "exit"

            pygame.draw.rect(screen, shadow_color, (popup_x + 5, popup_y + 5, popup_width, popup_height))

            # rysowanie popupu
            pygame.draw.rect(screen, popup_color, (popup_x, popup_y, popup_width, popup_height))
            pygame.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, popup_width, popup_height), 2)
            # tekst zwycięzcy
            text_surface = font.render(winner_text, True, text_color)
            text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 40))
            screen.blit(text_surface, text_rect)

            pygame.draw.rect(screen, button_shadow_color, continue_button_rect.move(3, 3))
            # kontynuuj przycisk
            mouse_pos = pygame.mouse.get_pos()
            continue_color = button_hover_color if continue_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(screen, continue_color, continue_button_rect)
            continue_text = button_font.render("Kontynuuj", True, button_text_color)
            continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
            screen.blit(continue_text, continue_text_rect)

            pygame.draw.rect(screen, button_shadow_color, exit_button_rect.move(3, 3))

            exit_color = button_hover_color if exit_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(screen, exit_color, exit_button_rect)
            exit_text = button_font.render("Zakończ", True, button_text_color)
            exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
            screen.blit(exit_text, exit_text_rect)

            pygame.display.flip()


def get_row_col_from_mouse(pos): #konwertuje pozycje myszy na indeksy planszy
    x, y = pos
    row = y // square_size
    col = x // square_size
    return row, col


class Game:

    def __init__(self):
        self.board = Board()


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    self.board.select(row, col)
            screen.fill(white)
            self.board.draw(screen)
            pygame.display.flip()
        self.game_over_popup()

    def game_over_popup(self):
        result = self.board.show_simple_popup(screen, "Chcesz zakończyć gre?")
        if result == "continue":
            print("Kontynuujemy grę")
        elif result == "exit":
            print("Koniec gry.")
            pygame.quit()
            sys.exit()

        pygame.quit()
        sys.exit()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()