import json
import os
import sys
import pygame

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((800, 60 * 8))
pygame.display.set_caption("Python Chess Game")

from modules.board import *
from modules.computer import *

bg = pygame.image.load("assets/chessboard.png").convert()
sidebg = pygame.image.load("assets/woodsidemenu.jpg").convert()
player = 1
myfont = pygame.font.Font("assets/Roboto-Black.ttf", 30)
clippy = pygame.image.load("assets/Clippy.png").convert_alpha()
clippy = pygame.transform.scale(clippy, (320, 240))
playeravatar = None

board = Board()

global all_sprites_list, sprites
all_sprites_list = pygame.sprite.Group()
sprites = [piece for row in board.array for piece in row if piece]
all_sprites_list.add(sprites)

all_sprites_list.draw(screen)

clock = pygame.time.Clock()

STATS_FILE = "leaderboard.json"


def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"human_wins": 0, "ai_wins": 0}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


def record_win(winner):
    stats = load_stats()
    if winner == "Human":
        stats["human_wins"] += 1
    elif winner == "AI":
        stats["ai_wins"] += 1
    save_stats(stats)


def select_piece(color):
    pos = pygame.mouse.get_pos()
    clicked_sprites = [s for s in sprites if s.rect.collidepoint(pos)]

    if len(clicked_sprites) == 1 and clicked_sprites[0].color == color:
        clicked_sprites[0].highlight()
        return clicked_sprites[0]


def select_square():
    x, y = pygame.mouse.get_pos()
    x = x // 60
    y = y // 60
    return (y, x)


def run_game():
    global player, playeravatar, clippy, board, all_sprites_list, sprites

    board = Board()
    all_sprites_list = pygame.sprite.Group()
    sprites = [piece for row in board.array for piece in row if piece]
    all_sprites_list.add(sprites)

    playeravatar = pygame.image.load("assets/avatar.png").convert_alpha()
    playeravatar = pygame.transform.scale(playeravatar, (320, 240))
    update_sidemenu("Your Turn!", (255, 255, 255))

    gameover = False
    selected = False
    trans_table = dict()
    checkWhite = False

    while not gameover:
        if player == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and not selected:
                    piece = select_piece("w")

                    if piece != None:
                        player_moves = piece.gen_legal_moves(board)
                        selected = True

                elif event.type == pygame.MOUSEBUTTONDOWN and selected:
                    square = select_square()
                    special_moves = special_move_gen(board, "w")

                    if square in player_moves:
                        oldx = piece.x
                        oldy = piece.y
                        dest = board.array[square[0]][square[1]]

                        pawn_promotion = board.move_piece(
                            piece, square[0], square[1]
                        )

                        if pawn_promotion:
                            all_sprites_list.add(pawn_promotion[0])
                            sprites.append(pawn_promotion[0])
                            all_sprites_list.remove(pawn_promotion[1])
                            sprites.remove(pawn_promotion[1])

                        if type(piece) == King or type(piece) == Rook:
                            piece.moved = True
                        if dest:
                            all_sprites_list.remove(dest)
                            sprites.remove(dest)

                        attacked = move_gen(board, "b", True)
                        if (
                            board.white_king.y,
                            board.white_king.x,
                        ) not in attacked:
                            selected = False
                            player = "AI"
                            update_sidemenu("CPU Thinking...", (255, 255, 255))

                            if dest:
                                board.score -= board.pvalue_dict[type(dest)]

                        else:
                            board.move_piece(piece, oldy, oldx)
                            if type(piece) == King or type(piece) == Rook:
                                piece.moved = False
                            board.array[square[0]][square[1]] = dest
                            if dest:
                                all_sprites_list.add(dest)
                                sprites.append(dest)
                            if pawn_promotion:
                                all_sprites_list.add(pawn_promotion[1])
                                sprites.append(pawn_promotion[1])
                            piece.highlight()

                            if checkWhite:
                                update_sidemenu(
                                    "You have to get out\nof check!",
                                    (255, 0, 0),
                                )
                                pygame.display.update()
                                pygame.time.wait(1000)
                                update_sidemenu(
                                    "Your Turn: Check!", (255, 0, 0)
                                )
                            else:
                                update_sidemenu(
                                    "This move would put\nyou in check!",
                                    (255, 0, 0),
                                )
                                pygame.display.update()
                                pygame.time.wait(1000)
                                update_sidemenu("Your turn!", (255, 255, 255))

                    elif (piece.y, piece.x) == square:
                        piece.unhighlight()
                        selected = False

                    elif special_moves and square in special_moves:
                        special = special_moves[square]
                        if (
                            special == "CR" or special == "CL"
                        ) and type(piece) == King:
                            board.move_piece(
                                piece, square[0], square[1], special
                            )
                            selected = False
                            player = "AI"

                        else:
                            update_sidemenu("Invalid move!", (255, 0, 0))
                            pygame.display.update()
                            pygame.time.wait(1000)
                            if checkWhite:
                                update_sidemenu(
                                    "Your Turn: Check!", (255, 0, 0)
                                )
                            else:
                                update_sidemenu("Your turn!", (255, 255, 255))

                    else:
                        update_sidemenu("Invalid move!", (255, 0, 0))
                        pygame.display.update()
                        pygame.time.wait(1000)
                        if checkWhite:
                            update_sidemenu("Your Turn: Check!", (255, 0, 0))
                        else:
                            update_sidemenu("Your turn!", (255, 255, 255))

        elif player == "AI":
            value, move = minimax(
                board, 3, float("-inf"), float("inf"), True, trans_table
            )

            if value == float("-inf") and move == 0:
                print(value)
                print(move)
                gameover = True
                player = 1
                record_win("Human")
                update_sidemenu(
                    "Checkmate!\nYou Win!\nPress any key",
                    (255, 255, 0),
                )

            else:
                start = move[0]
                end = move[1]
                piece = board.array[start[0]][start[1]]
                dest = board.array[end[0]][end[1]]

                pawn_promotion = board.move_piece(piece, end[0], end[1])
                if pawn_promotion:
                    all_sprites_list.add(pawn_promotion[0])
                    sprites.append(pawn_promotion[0])
                    all_sprites_list.remove(pawn_promotion[1])
                    sprites.remove(pawn_promotion[1])

                if dest:
                    all_sprites_list.remove(dest)
                    sprites.remove(dest)
                    board.score += board.pvalue_dict[type(dest)]

                player = 1

                attacked = move_gen(board, "b", True)
                if (board.white_king.y, board.white_king.x) in attacked:
                    update_sidemenu("Your Turn: Check!", (255, 0, 0))
                    checkWhite = True
                else:
                    update_sidemenu("Your Turn!", (255, 255, 255))
                    checkWhite = False

            if value == float("inf"):
                print("Player checkmate")
                gameover = True
                player = "AI"
                record_win("AI")
                update_sidemenu(
                    "Checkmate!\nCPU Wins!\nPress any key",
                    (255, 255, 0),
                )

        screen.blit(bg, (0, 0))
        all_sprites_list.draw(screen)
        pygame.display.update()
        clock.tick(60)


def show_leaderboard():
    menubg = pygame.image.load("assets/menubg.jpg").convert()
    screen.blit(menubg, (0, 0))

    title_font = pygame.font.Font("assets/Roboto-Black.ttf", 60)
    score_font = pygame.font.Font("assets/Roboto-Black.ttf", 40)

    stats = load_stats()

    textsurface = title_font.render("LEADERBOARD", False, (255, 215, 0))
    screen.blit(textsurface, (200, 40))

    human_text = score_font.render(
        f"Human Wins: {stats['human_wins']}", False, (255, 255, 255)
    )
    screen.blit(human_text, (200, 180))

    ai_text = score_font.render(
        f"Computer Bot (AI) Wins: {stats['ai_wins']}", False, (255, 255, 255)
    )
    screen.blit(ai_text, (200, 260))

    subtext = myfont.render(
        "Press any key to return to Main Menu...", False, (200, 200, 200)
    )
    screen.blit(subtext, (150, 400))

    pygame.display.update()
    pygame.time.wait(500)
    pygame.event.clear()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                return 
            elif event.type == pygame.QUIT:
                sys.exit()


def show_developers():
    menubg = pygame.image.load("assets/menubg.jpg").convert()
    screen.blit(menubg, (0, 0))

    title_font = pygame.font.Font("assets/Roboto-Black.ttf", 50)
    info_font = pygame.font.Font("assets/Roboto-Black.ttf", 28)

    textsurface = title_font.render("DEVELOPERS", False, (255, 215, 0))
    screen.blit(textsurface, (250, 40))

    developers = [
        ("Azizul Hakim", "20245103360"),
        ("MD. Manzilur Rahman", "20245103358"),
        ("Wahidul Haque Navid", "20245103395"),
    ]

    start_y = 150
    for name, dev_id in developers:
        dev_text = info_font.render(
            f"• {name}  (ID: {dev_id})", False, (255, 255, 255)
        )
        screen.blit(dev_text, (160, start_y))
        start_y += 60

    subtext = myfont.render(
        "Press any key to return to Main Menu...", False, (200, 200, 200)
    )
    screen.blit(subtext, (150, 400))

    pygame.display.update()
    pygame.time.wait(500)
    pygame.event.clear()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                return
            elif event.type == pygame.QUIT:
                sys.exit()


def game_over():
    board.print_to_terminal()
    crown = pygame.image.load("assets/crown.png").convert_alpha()
    crown = pygame.transform.scale(crown, (80, 60))
    screen.blit(crown, (520, 20))
    pygame.display.update()
    pygame.time.wait(1000)
    pygame.event.clear()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                waiting = False
            elif event.type == pygame.QUIT:
                sys.exit()


def update_sidemenu(message, colour):
    screen.blit(sidebg, (480, 0))
    global playeravatar, clippy

    if player == 1:
        screen.blit(playeravatar, (480, 0))

    elif player == "AI":
        screen.blit(clippy, (480, 0))

    message = message.splitlines()
    c = 0
    for m in message:
        textsurface = myfont.render(m, False, colour)
        screen.blit(textsurface, (500, 250 + c))
        c += 40


def welcome():
    menubg = pygame.image.load("assets/menubg.jpg").convert()
    bigfont = pygame.font.Font("assets/Roboto-Black.ttf", 70)
    medfont = pygame.font.Font("assets/Roboto-Black.ttf", 40)
    btn_font = pygame.font.Font("assets/Roboto-Black.ttf", 25)

    play_btn = pygame.Rect(250, 210, 300, 50)
    leaderboard_btn = pygame.Rect(250, 280, 300, 50)
    dev_btn = pygame.Rect(250, 350, 300, 50)

    while True:
        screen.blit(menubg, (0, 0))

        title = bigfont.render("Smart Chess Arena", False, (255, 255, 255))
        screen.blit(title, (110, 20))

        subtitle = medfont.render("CSE 322 Final Project", False, (200, 200, 250))
        screen.blit(subtitle, (200, 110))

        mouse_pos = pygame.mouse.get_pos()

        play_color = (60, 140, 220) if play_btn.collidepoint(mouse_pos) else (40, 90, 160)
        pygame.draw.rect(screen, play_color, play_btn, border_radius=10)
        play_text = btn_font.render("PLAY GAME", True, (255, 255, 255))
        screen.blit(play_text, (play_btn.x + 85, play_btn.y + 12))

        lb_color = (60, 140, 220) if leaderboard_btn.collidepoint(mouse_pos) else (40, 90, 160)
        pygame.draw.rect(screen, lb_color, leaderboard_btn, border_radius=10)
        lb_text = btn_font.render("LEADERBOARD", True, (255, 255, 255))
        screen.blit(lb_text, (leaderboard_btn.x + 65, leaderboard_btn.y + 12))

        dev_color = (60, 140, 220) if dev_btn.collidepoint(mouse_pos) else (40, 90, 160)
        pygame.draw.rect(screen, dev_color, dev_btn, border_radius=10)
        dev_text = btn_font.render("DEVELOPERS", True, (255, 255, 255))
        screen.blit(dev_text, (dev_btn.x + 75, dev_btn.y + 12))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(event.pos):
                    return "play"
                elif leaderboard_btn.collidepoint(event.pos):
                    return "leaderboard"
                elif dev_btn.collidepoint(event.pos):
                    return "developers"


if __name__ == "__main__":
    while True:
        choice = welcome()

        if choice == "play":
            run_game()
            game_over()
            show_leaderboard() 
        elif choice == "leaderboard":
            show_leaderboard()
        elif choice == "developers":
            show_developers()