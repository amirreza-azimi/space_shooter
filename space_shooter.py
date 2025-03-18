import pygame
import os
from random import randint, choice

# general setup
pygame.init()
window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Space Shooter')
clock = pygame.time.Clock()

# high score
def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            return int(file.read().strip())
    return 0

def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

high_score = load_high_score()

# importing player
player = pygame.image.load('images2/space_ship.png')
player = pygame.transform.scale(player, (80, 80))  # تغییر اندازه به ۸۰×۸۰ پیکسل
player_rect = player.get_rect(center=(window_width / 2, window_height / 2))
player_speed = 300

# cooldown
can_shoot = True
laser_shoot_time = 0
cooldown_duration = 400
lasers = []
laser_speed = 500

# importing meteor
meteor = pygame.image.load('images2/meteor.png')
meteor = pygame.transform.scale(meteor, (60, 120))
meteors = []
meteor_speed = 300

# importing laser
laser = pygame.image.load('images2/laser.png')
laser = pygame.transform.scale(laser, (60, 120))

# meteor event for appearinf
meteor_event = pygame.USEREVENT + 1
pygame.time.set_timer(meteor_event, 500)

# game mode
game_active = False  
game_start = False
game_state = 'menu'

# score
score = 0

# fonts
font_score = pygame.font.Font('images2/arcadeclassic.ttf', 40)
font_large = pygame.font.Font('images2/arcadeclassic.ttf', 100)
font_small = pygame.font.Font('images2/arcadeclassic.ttf', 50)

# changing music
def change_music(music_file, loop=True):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1 if loop else 0)
    pygame.mixer.music.set_volume(0.05)

# start page
def show_start_screen():
    background = pygame.image.load('images2/star_bg.jpg')
    background = pygame.transform.scale(background, (window_width, window_height))
    display_surface.blit(background, (0, 0))
    
    title_text = font_large.render("SPACE     SHOOTER", True, (0, 255, 255))
    start_text = font_small.render("Press     ENTER     to     Start", True, (200, 200, 200))
    quit_text = font_small.render("Press     ESC     to     Quit", True, (200, 200, 200))
    
    display_surface.blit(title_text, (window_width//2 - title_text.get_width()//2, window_height//3))
    display_surface.blit(start_text, (window_width//2 - start_text.get_width()//2, window_height//2))
    display_surface.blit(quit_text, (window_width//2 - quit_text.get_width()//2, window_height//1.7))

    change_music('audio/start_menu_music.mp3')

    pygame.display.update()

# game over page
def show_game_over():

    global high_score

    display_surface.fill('black')

    if score > high_score:
        high_score = score
        save_high_score(high_score)
    
    game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
    final_score_text = font_small.render(f"Score         {score}", True, (255, 255, 0))
    high_score_text = font_small.render(f"High     Score     {high_score}", True, (0, 255, 0))
    restart_text = font_small.render("Press     ENTER     to     Retart", True, (200, 200, 200))
    quit_text = font_small.render("Press     ESC     to     Quit", True, (200, 200, 200))
    
    display_surface.blit(game_over_text, (window_width//2 - game_over_text.get_width()//2, window_height//3))
    display_surface.blit(final_score_text, (window_width//2 - final_score_text.get_width()//2, window_height//5))
    display_surface.blit(high_score_text, (window_width//2 - high_score_text.get_width()//2, window_height//4))
    display_surface.blit(restart_text, (window_width//2 - restart_text.get_width()//2, window_height//2))
    display_surface.blit(quit_text, (window_width//2 - quit_text.get_width()//2, window_height//1.7))

    pygame.display.update()

# keys for start page
show_start_screen()
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_state == 'menu':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_start = True
                    game_active = True
                    game_state = 'playing'
                    change_music('audio/game_music.wav')
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

while True:

    if game_active or game_state == 'playing':
        
        display_surface.fill('#380F30')

        # time
        dt = clock.tick(60) / 1000

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == meteor_event:
                new_meteor = meteor.get_rect(midtop=(randint(0, window_width), 0))
                meteor_speed_x = choice([-100, -50, 0, 50, 100])  
                meteors.append({"rect": new_meteor, "speed_x": meteor_speed_x})

        # meteor
        for meteor_obj in meteors:
            meteor_obj["rect"].y += meteor_speed * dt
            meteor_obj["rect"].x += meteor_obj["speed_x"] * dt

            if meteor_obj["rect"].left < 0:
                meteor_obj["rect"].left = 0
            elif meteor_obj["rect"].right > window_width:
                meteor_obj["rect"].right = window_width

        meteors = [m for m in meteors if m["rect"].top < window_height and 0 <= m["rect"].x <= window_width]

        # destroying meteor
        for laser_rect in lasers[:]:
            for meteor_obj in meteors[:]:
                if laser_rect.colliderect(meteor_obj["rect"]):
                    pygame.mixer.Sound('audio/explosion.wav').play()
                    lasers.remove(laser_rect)
                    meteors.remove(meteor_obj)
                    score += 10
                    break

        # losing
        for meteor_obj in meteors:
            if meteor_obj["rect"].colliderect(player_rect):
                game_active = False  
                game_state = 'game_over'

        #movement of player
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]), int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]))
        if direction.length() > 0:
            direction = direction.normalize()
        
        new_y = player_rect.centery + direction.y * player_speed * dt
        new_x = player_rect.centerx + direction.x * player_speed * dt
        player_rect.centerx = max(player_rect.width // 2, min(window_width - player_rect.width // 2, new_x))
        player_rect.centery = max(player_rect.height // 2, min(window_height - player_rect.height // 2, new_y))

        # laser
        if keys[pygame.K_SPACE] and can_shoot:
            pygame.mixer.Sound('audio/laser.wav').play()
            new_laser = laser.get_rect(midbottom=player_rect.midtop)
            lasers.append(new_laser)
            can_shoot = False
            laser_shoot_time = pygame.time.get_ticks()

        for laser_rect in lasers:
            laser_rect.y -= laser_speed * dt
        lasers = [laser for laser in lasers if laser.bottom > 0]

        if not can_shoot:
            if pygame.time.get_ticks() - laser_shoot_time >= cooldown_duration:
                can_shoot = True

        # drawing the game
        background = pygame.image.load('images2/bg.png')
        background = pygame.transform.scale(background, (window_width, window_height))
        display_surface.blit(background, (1, 5))

        for laser_rect in lasers:
            display_surface.blit(laser, laser_rect)

        for meteor_obj in meteors:
            display_surface.blit(meteor, meteor_obj["rect"])

        display_surface.blit(player, player_rect.topleft)

        # showing score
        score_text = font_score.render(str(score), True, ('white'))
        score_x = (window_width - score_text.get_width()) // 2
        score_y = window_height - score_text.get_height() - 20
        display_surface.blit(score_text, (score_x, score_y))

        pygame.display.update()

    elif game_state == 'game_over':
        show_game_over()
        change_music('audio/game_over.mp3', loop=False)
        # waiting for quit or restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        player_rect.center = (window_width / 2, window_height / 2)
                        meteors.clear()
                        lasers.clear()
                        score = 0
                        change_music('audio/game_music.wav')
                        game_active = True
                        game_state = 'playing'
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
