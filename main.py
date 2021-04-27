import pygame
import os
import sys
import random

FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["[Начать]",
                  "",
                  "[Выход]"]

    fon = pygame.transform.scale(load_image('snake-game.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 120
    line_count = 0
    for line in intro_text:
        line_count += 1
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        if line_count == 1:
            start_rect = intro_rect
        elif line_count == 3:
            end_rect = intro_rect
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 200
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(level):
    snake, apple, x, y = None, None, None, None
    for y in range(2):
        for x in range(2):
            Tile('grass', x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            # if level[y][x] == '.':
            #     Tile('empty', x, y)
            if level[y][x] == '#':
                walls_group.add(Tile('wall', x, y))
            # elif level[y][x] == '@':
            #     Tile('empty', x, y)
            #     new_player = Player(x, y)
    a_x = random.randint(1, 20)
    a_y = random.randint(1, 20)
    apple = Apple(a_x, a_y)
    return snake, apple, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        if tile_type == 'grass':
            self.rect = self.image.get_rect().move(
                200 * pos_x, 200 * pos_y)
        else:
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


class Apple(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(apple_group, all_sprites)
        self.image = apple_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Snake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(snake_group, all_sprites)
        # важные переменные - позиция головы змеи и его тела
        self.snake_head_pos = [10, 5]
        # начальное тело змеи состоит из трех сегментов
        # голова змеи - первый элемент, хвост - последний
        self.snake_body = [[10, 5], [9, 5], [8, 5]]
        # изображения головы и тела
        self.head_image = snake_images['head']
        self.rotated_head_image = self.head_image
        self.body_image = snake_images['body']
        # направление движение змеи, изначально
        # зададимся вправо
        self.direction = "RIGHT"
        # куда будет меняться напрвление движения змеи
        # при нажатии соответствующих клавиш
        self.change_to = self.direction

    def validate_direction_and_change(self):
        """Изменияем направление движения змеи только в том случае,
        если оно не прямо противоположно текущему"""
        if any((self.change_to == "RIGHT" and not self.direction == "LEFT",
                self.change_to == "LEFT" and not self.direction == "RIGHT",
                self.change_to == "UP" and not self.direction == "DOWN",
                self.change_to == "DOWN" and not self.direction == "UP")):
            self.direction = self.change_to

    def change_head_position(self):
        """Изменияем положение головы змеи"""
        if self.direction == "RIGHT":
            self.snake_head_pos[0] += 1
            self.rotated_head_image = self.head_image
        elif self.direction == "LEFT":
            self.snake_head_pos[0] -= 1
            self.rotated_head_image = self.head_image.transpose(Image.ROTATE_180)
        elif self.direction == "UP":
            self.snake_head_pos[1] -= 1
            self.rotated_head_image = self.head_image.transpose(Image.ROTATE_90)
        elif self.direction == "DOWN":
            self.snake_head_pos[1] += 1
            self.rotated_head_image = self.head_image.transpose(Image.ROTATE_270)

    def snake_body_mechanism(self, score, food_pos):
        # если вставлять просто snake_head_pos,
        # то на всех трех позициях в snake_body
        # окажется один и тот же список с одинаковыми координатами
        # и мы будем управлять змеей из одного квадрата
        self.snake_body.insert(0, list(self.snake_head_pos))
        # если съели еду
        if (self.snake_head_pos[0] == food_pos[0] and
                self.snake_head_pos[1] == food_pos[1]):
            # если съели еду то задаем новое положение еды случайным
            # образом и увеличивем score на один
            food_pos = [random.randrange(1, 20), random.randrange(1, 20)]
            score += 1
        else:
            # если не нашли еду, то убираем последний сегмент,
            # если этого не сделать, то змея будет постоянно расти
            self.snake_body.pop()
        return score, food_pos

    def draw_snake(self):
        """Отображаем все сегменты змеи"""
        # Сперва отобразим голову
        self.rect = self.rotated_head_image.get_rect().move(
            tile_width * self.snake_body[0][0],
            tile_height * self.snake_body[0][1])
        # затем остальное тело
        for pos in self.snake_body[1:]:
            self.rect = self.body_image.get_rect().move(
                tile_width * pos[0],
                tile_height * pos[1])



# class Player(pygame.sprite.Sprite):
#     def __init__(self, pos_x, pos_y):
#         super().__init__(player_group, all_sprites)
#         self.image = player_image
#         self.rect = self.image.get_rect().move(
#             tile_width * pos_x + 15, tile_height * pos_y + 5)
#
#     def update(self, direction_x, direction_y):
#         self.rect.x += tile_width * direction_x
#         self.rect.y += tile_height * direction_y
#         if pygame.sprite.spritecollideany(self, walls_group):
#             self.rect.x -= tile_width * direction_x
#             self.rect.y -= tile_height * direction_y


# class Camera:
#     def __init__(self):
#         self.dx = 0
#         self.dy = 0
#
#     def apply(self, obj):
#         obj.rect.x += self.dx
#         obj.rect.y += self.dy
#
#     def update(self, target):
#         self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
#         self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = 500, 400
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра Змейка')

    clock = pygame.time.Clock()

    start_screen()
    # terminate()

    tile_images = {
        'wall': load_image('wall.png'),
        'grass': load_image('grass.png')
    }
    snake_images = {
        'head': load_image('head.png'),
        'body': load_image('body.png')
    }
    apple_image = load_image('apple.png')
    # fon_image = load_image('grass.png')

    tile_width = tile_height = 20

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    snake_group = pygame.sprite.Group()
    apple_group = pygame.sprite.Group()

    level_name = 'level.txt'
    if not os.path.isfile(os.path.join('data', level_name)):
        print(f"Файл с изображением '{level_name}' не найден")
        terminate()
    snake, apple, level_x, level_y = generate_level(load_level(level_name))

    # camera = Camera()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                pass
                # player.update(1, 0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                pass
                # player.update(-1, 0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                pass
                # player.update(0, 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                pass
                # player.update(0, -1)
        screen.fill('black')
        # camera.update(player)
        # for sprite in all_sprites:
        #     camera.apply(sprite)
        all_sprites.draw(screen)
        snake_group.draw(screen)
        pygame.display.flip()
