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


def button_click(rect, pos):
    x, y = pos
    if x >= rect.x and x <= rect.x + rect.width and \
            y >= rect.y and y <= rect.y + rect.height:
        return True
    return False


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
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 200
        text_coord += intro_rect.height
        if line_count == 1:
            start_rect = intro_rect
        elif line_count == 3:
            end_rect = intro_rect
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and\
                    button_click(start_rect, event.pos):
                return  # начинаем игру
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    button_click(end_rect, event.pos):
                terminate()  # завершаем игру
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(level):
    snake, apple, x, y = None, None, None, None
    for y in range(2):
        for x in range(2):
            Tile('tile','grass', x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            # if level[y][x] == '.':
            #     Tile('empty', x, y)
            if level[y][x] == '#':
                walls_group.add(Tile('tile', 'wall', x, y))
            # elif level[y][x] == '@':
            #     Tile('empty', x, y)
            #     new_player = Player(x, y)
    a_x = random.randint(1, 18)
    a_y = random.randint(1, 18)
    apple = Apple(a_x, a_y)
    snake = Snake()
    return snake, apple, x, y


def show_info(score, level):
    font = pygame.font.Font(None, 30)
    text = font.render(f"Score: {str(score)}", 1, (100, 255, 100))
    screen.blit(text, (405, 50))
    text2 = font.render(f"Level: {str(level)}", 1, (100, 255, 100))
    screen.blit(text2, (405, 100))


class Tile(pygame.sprite.Sprite):
    def __init__(self, group, tile_type, pos_x, pos_y):
        if group == 'snake':
            tile_group = snake_group
            images = snake_images
        else:
            tile_group = tiles_group
            images = tile_images
        super().__init__(tile_group, all_sprites)
        self.image = images[tile_type]
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
        self.pos = pos_x, pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect().move(
            tile_width * pos[0], tile_height * pos[1])


class Snake:
    def __init__(self):
        # важные переменные - позиция головы змеи и его тела
        self.snake_head_pos = [10, 5]
        # начальное тело змеи состоит из трех сегментов
        # голова змеи - первый элемент, хвост - последний
        self.snake_body = [[10, 5, 0], [9, 5, 0], [8, 5, 0]]
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
        self.speed = 0

    def validate_direction_and_change(self):
        """Изменияем направление движения змеи только в том случае,
        если оно не прямо противоположно текущему"""
        if any((self.change_to == "RIGHT" and not self.direction == "LEFT",
                self.change_to == "LEFT" and not self.direction == "RIGHT",
                self.change_to == "UP" and not self.direction == "DOWN",
                self.change_to == "DOWN" and not self.direction == "UP")):
            if self.change_to == "UP" and self.direction == "RIGHT" or\
                    self.change_to == "LEFT" and self.direction == "UP" or\
                    self.change_to == "DOWN" and self.direction == "LEFT" or\
                    self.change_to == "RIGHT" and self.direction == "DOWN":
                self.snake_body[0][2].image = pygame.transform.rotate(
                    self.snake_body[0][2].image, 90)
            if self.change_to == "DOWN" and self.direction == "RIGHT" or \
                    self.change_to == "LEFT" and self.direction == "DOWN" or \
                    self.change_to == "UP" and self.direction == "LEFT" or \
                    self.change_to == "RIGHT" and self.direction == "UP":
                self.snake_body[0][2].image = pygame.transform.rotate(
                    self.snake_body[0][2].image, 270)
            self.direction = self.change_to

    def change_head_position(self):
        """Изменяем положение головы змеи"""
        # Делаем задержку перемещения
        sp = 200 // level
        self.speed += 1
        if self.speed > sp:
            self.speed = 0
        self.speed2 = self.speed // sp
        if self.direction == "RIGHT":
            self.snake_head_pos[0] += self.speed2
        elif self.direction == "LEFT":
            self.snake_head_pos[0] -= self.speed2
        elif self.direction == "UP":
            self.snake_head_pos[1] -= self.speed2
        elif self.direction == "DOWN":
            self.snake_head_pos[1] += self.speed2

    def snake_body_mechanism(self, score, level, food_pos):
        # если вставлять просто snake_head_pos,
        # то на всех трех позициях в snake_body
        # окажется один и тот же список с одинаковыми координатами
        # и мы будем управлять змеей из одного квадрата
        if self.speed2 > 0:
            self.snake_body.insert(0, list(self.snake_head_pos + [self.snake_body[0][2]]))
            for i in range(1, len(self.snake_body) - 1):
                self.snake_body[i][2] = self.snake_body[i + 1][2]
            # если съели еду
            if (self.snake_head_pos[0] == food_pos[0] and
                    self.snake_head_pos[1] == food_pos[1]):
                # если съели еду то задаем новое положение еды случайным
                # образом и увеличивем score на один
                food_pos = [random.randrange(1, 18), random.randrange(1, 18)]
                score += 1
                if score % 10 == 0:
                    level += 1
                # добавим изображение элемента хвоста в конец.
                i = len(self.snake_body) - 1
                x, y = self.snake_body[i][0], self.snake_body[i][1]
                body = Tile('snake', 'body', x, y)
                self.snake_body[i][2] = body
                snake_group.add(body)
            else:
                # если не нашли еду, то убираем последний сегмент,
                # если этого не сделать, то змея будет постоянно расти
                self.snake_body.pop()
        return score, level, food_pos

    def draw_snake(self):
        """Отображаем все сегменты змеи"""
        # Сперва отобразим голову
        x, y = self.snake_body[0][0], self.snake_body[0][1]
        head = Tile('snake', 'head', x, y)
        self.snake_body[0][2] = head
        snake_group.add(head)
        # затем остальное тело
        for i in range(1, len(self.snake_body)):
            x, y = self.snake_body[i][0], self.snake_body[i][1]
            body = Tile('snake', 'body', x, y)
            self.snake_body[i][2] = body
            snake_group.add(body)

    def update_draw(self):
        for i in range(len(self.snake_body)):
            x, y = self.snake_body[i][0], self.snake_body[i][1]
            self.snake_body[i][2].rect = \
                self.snake_body[i][2].image.get_rect().move(
                    tile_width * x, tile_height * y)

if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = 500, 400
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра Змейка')

    clock = pygame.time.Clock()
    score = 0
    level = 1

    start_screen()

    tile_images = {
        'wall': load_image('wall.png'),
        'grass': load_image('grass.png')
    }
    snake_images = {
        'head': load_image('head.png'),
        'body': load_image('body.png')
    }
    apple_image = load_image('apple.png')

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
    snake.draw_snake()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                snake.change_to = "RIGHT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                snake.change_to = "LEFT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                snake.change_to = "DOWN"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                snake.change_to = "UP"
            snake.validate_direction_and_change()
        screen.fill('black')
        snake.change_head_position()
        food_pos = apple.pos
        score, level, food_pos = snake.snake_body_mechanism(score, level, food_pos)
        snake.update_draw()
        apple.update(food_pos)
        show_info(score, level)
        all_sprites.draw(screen)
        pygame.display.flip()
