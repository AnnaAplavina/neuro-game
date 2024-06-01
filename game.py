import pygame
import random
import csv

pygame.init()

width, height = 800, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("EMG Controlled Arcade Game")

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

player_image = pygame.image.load("spaceship.png")
enemy_image = pygame.image.load("asteroid.png")

player_size = 50
player_image = pygame.transform.scale(player_image, (player_size, player_size))

enemy_size = 50
enemy_image = pygame.transform.scale(enemy_image, (enemy_size, enemy_size))

player_pos = [width // 2, height - 2 * player_size]
player_speed = 10
player_lives = 3

enemy_pos = [random.randint(0, width - enemy_size), 0]
enemy_speed = 10
enemy_speed_increment = 0.05

num_stars = 100
stars = [[random.randint(0, width), random.randint(0, height)] for _ in range(num_stars)]

font = pygame.font.SysFont("monospace", 35)

def draw_stars(star_list):
    for star in star_list:
        pygame.draw.circle(win, white, star, 2)

def drop_enemies(enemy_list):
    delay = random.random()
    if len(enemy_list) < 10 and delay < 0.1:
        x_pos = random.randint(0, width - enemy_size)
        y_pos = 0
        enemy_list.append([x_pos, y_pos])

def draw_enemies(enemy_list):
    for enemy_pos in enemy_list:
        win.blit(enemy_image, (enemy_pos[0], enemy_pos[1]))

def update_enemy_positions(enemy_list):
    for idx, enemy_pos in enumerate(enemy_list):
        if enemy_pos[1] >= 0 and enemy_pos[1] < height:
            enemy_pos[1] += enemy_speed
        else:
            enemy_list.pop(idx)

def detect_collision(player_pos, enemy_pos):
    p_x, p_y = player_pos
    e_x, e_y = enemy_pos
    if (e_x >= p_x and e_x < (p_x + player_size)) or (p_x >= e_x and p_x < (e_x + enemy_size)):
        if (e_y >= p_y and e_y < (p_y + player_size)) or (p_y >= e_y and p_y < (e_y + enemy_size)):
            return True
    return False

def collision_check(enemy_list, player_pos):
    for enemy_pos in enemy_list:
        if detect_collision(player_pos, enemy_pos):
            return True
    return False

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# Чтение данных ЭМГ из файла
emg_data = []
with open('throws.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        try:
            time = float(row[0])
            signal = float(row[1])
            emg_data.append((time, signal))
        except ValueError:
            continue

if not emg_data:
    print("Error: No EMG data loaded.")
    pygame.quit()
    exit()

emg_index = 0
# Функция для получения текущей амплитуды ЭМГ
def get_emg_amplitude(emg_data, emg_index):
    slice = emg_data[emg_index:emg_index+20]
    max_signal = 0
    min_signal = 0
    for time, signal in slice:
        max_signal = max(max_signal, signal)
        min_signal = min(min_signal, signal)
    return max_signal - min_signal

# Основной цикл игры
game_over = False
clock = pygame.time.Clock()
points = 0

enemy_list = [enemy_pos]

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    win.fill(black)
    draw_stars(stars)

    # Получение амплитуды ЭМГ и обновление позиции игрока
    emg_index = emg_index + 20
    emg_amplitude = get_emg_amplitude(emg_data, emg_index)
    print(emg_amplitude)
    player_pos[0] += (emg_amplitude - 2.5) * player_speed  # смещение на основе амплитуды, центр в 2.5

    if player_pos[0] < 0:
        player_pos[0] = 0
    elif player_pos[0] > width - player_size:
        player_pos[0] = width - player_size

    drop_enemies(enemy_list)
    update_enemy_positions(enemy_list)

    if collision_check(enemy_list, player_pos):
        player_lives -= 1
        if player_lives == 0:
            game_over = True
            break
        else:
            enemy_list = []

    draw_enemies(enemy_list)

    win.blit(player_image, (player_pos[0], player_pos[1]))

    enemy_speed += enemy_speed_increment
    points += 1

    draw_text(f"Lives: {player_lives}", font, white, win, 10, 10)
    draw_text(f"Points: {points}", font, white, win, width - 500, 10)

    clock.tick(30)
    pygame.display.update()

pygame.quit()
