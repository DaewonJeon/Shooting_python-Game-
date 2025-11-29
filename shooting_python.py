import pygame
import random
import sys

# --- 초기화 ---
pygame.init()
pygame.mixer.init() 
pygame.font.init() 

# --- 색상 정의 (RGB) ---
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)     
RED = (255, 60, 60)      
BLUE = (60, 120, 255)    
YELLOW = (255, 255, 0)   
GREY = (100, 100, 100)   
GREEN = (50, 200, 80)    
GOLD = (255, 215, 0)     
ORANGE = (255, 165, 0)   

# 버튼용 색상
BTN_RED = (255, 107, 107)    
BTN_GREEN = (78, 205, 196)   
BTN_BLUE = (50, 150, 255)    
BTN_YELLOW = (255, 230, 109) 

# --- 게임 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooting Python")
clock = pygame.time.Clock()

# 폰트 설정
font_title = pygame.font.SysFont("arial", 70, True)
font_btn = pygame.font.SysFont("arial", 40, True)
font_sub = pygame.font.SysFont("arial", 40)
font_info = pygame.font.SysFont("arial", 25)
font_ui = pygame.font.SysFont("arial", 30, True)

# --- 물리 엔진 상수 ---
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_FORCE = 16       
BULLET_SPEED = 15     
ENEMY_SPEED = 3       

# --- 게임 상태 상수 ---
STATE_MENU = 0      
STATE_GUIDE = 1     
STATE_OPTION = 2    
STATE_PLAYING = 3   
STATE_GAMEOVER = 4  
STATE_PAUSE = 5     

# === [버튼 클래스] ===
class Button:
    def __init__(self, text, x, y, width, height, color, text_color=BLACK):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        current_color = self.color
        draw_rect = self.rect.copy()

        if self.hovered:
            scale = 5
            draw_rect = pygame.Rect(self.x - scale, self.y - scale, self.width + scale*2, self.height + scale*2)
            current_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))

        pygame.draw.rect(screen, current_color, draw_rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, draw_rect, 3, border_radius=15)

        text_surf = font_btn.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False

# === [파티클 클래스] ===
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.life = random.randint(20, 40)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1
        self.size -= 0.1 
        
    def draw(self, surface, shake_x=0, shake_y=0):
        if self.size > 0:
            rect = (self.x + shake_x, self.y + shake_y, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect)

# === [배경 별 클래스] ===
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 1.0)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        pygame.draw.circle(surface, (200, 200, 255), (int(self.x), int(self.y)), self.size)

# === [아이템 클래스] ===
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.item_type = item_type # "speed", "shield", "heart"

        # 아이템 이미지 생성 (투명 배경)
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)

        if item_type == "speed":
            self.draw_shoe(self.image, (80, 180, 255))
        elif item_type == "shield":
            self.draw_shield(self.image, (255, 255, 120))
        elif item_type == "heart":
            self.draw_heart(self.image, (255, 70, 100))

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 2 # 천천히 떨어짐
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    # ❤️ 하트 모양 그리기
    def draw_heart(self, surface, color):
        pygame.draw.circle(surface, color, (10, 12), 8)
        pygame.draw.circle(surface, color, (22, 12), 8)
        pygame.draw.polygon(surface, color, [(4, 16), (28, 16), (16, 30)])

    # 👟 신발 모양 그리기
    def draw_shoe(self, surface, color):
        pygame.draw.rect(surface, color, (5, 20, 22, 7))
        pygame.draw.rect(surface, (255, 255, 255), (5, 23, 22, 3))
        pygame.draw.polygon(surface, color, [(7, 20), (20, 10), (27, 12), (25, 20)])
        pygame.draw.line(surface, (255, 255, 255), (12, 17), (20, 14), 2)

    # 🛡 쉴드 모양 그리기
    def draw_shield(self, surface, color):
        pygame.draw.polygon(surface, color, [(16, 4), (26, 14), (20, 26), (12, 26), (6, 14)])
        pygame.draw.circle(surface, (255, 255, 255, 80), (14, 12), 4)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50)) 
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True 
        self.recoil_timer = 0
        self.invincible = False      
        self.invincible_timer = 0    
        self.visible = True          

        # [아이템 능력치]
        self.speed_buff = 0       # 속도 버프 남은 시간
        self.shield = False       # 쉴드 보유 여부

    def update(self, platforms):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.visible = True
            else:
                if self.invincible_timer % 10 < 5:
                    self.visible = False
                else:
                    self.visible = True
        
        # [속도 버프 처리]
        current_speed = PLAYER_SPEED
        if self.speed_buff > 0:
            current_speed = PLAYER_SPEED * 1.5 # 1.5배 빨라짐
            self.speed_buff -= 1

        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -current_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            dx = current_speed
            self.facing_right = True
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False

        self.vel_y += GRAVITY
        
        self.rect.x += dx
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

        self.rect.y += self.vel_y

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom < platform.rect.bottom + self.vel_y:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        
        if self.recoil_timer > 0:
            self.recoil_timer -= 1

    def shoot(self):
        self.recoil_timer = 5 
        direction = 1 if self.facing_right else -1
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        return bullet
    
    def get_hit(self):
        # [쉴드가 있으면 쉴드만 깨지고 데미지 없음]
        if self.shield:
            self.shield = False
            self.invincible = True
            self.invincible_timer = 60 # 쉴드 깨질 땐 짧게 무적 (1초)
            return False # 데미지 입지 않음 (False 반환)

        if not self.invincible:
            self.invincible = True
            self.invincible_timer = 120 
            return True # 데미지 입음 (True 반환)
        return False 

    def draw_custom(self, surface, shake_x=0, shake_y=0):
        if not self.visible: return 

        draw_rect = self.rect.move(shake_x, shake_y)
        pygame.draw.rect(surface, BLUE, draw_rect)
        eye_x_offset = 15 if self.facing_right else 5
        pygame.draw.rect(surface, WHITE, (draw_rect.x + eye_x_offset, draw_rect.y + 10, 10, 10))
        pygame.draw.rect(surface, RED, (draw_rect.x, draw_rect.y + 5, 30, 5))
        gun_x = draw_rect.right if self.facing_right else draw_rect.left - 15
        if self.recoil_timer > 0: 
            gun_x -= 5 if self.facing_right else -5
        pygame.draw.rect(surface, GREY, (gun_x - (5 if self.facing_right else -5), draw_rect.centery, 15, 8))

        # [쉴드 이펙트 그리기]
        if self.shield:
            cx = draw_rect.x + draw_rect.width // 2
            cy = draw_rect.y + draw_rect.height // 2
            radius = max(draw_rect.width, draw_rect.height)
            shield_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, 100), (radius * 2, radius * 2), radius + 5, width=3)
            surface.blit(shield_surf, (cx - radius * 2, cy - radius * 2))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREY):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        pygame.draw.rect(self.image, (200, 200, 200), (0, 0, width, 4)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((16, 8))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = BULLET_SPEED * direction

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.image = pygame.Surface((35, 35))
        self.image.fill(RED) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.player = player
        self.vel_y = 0
    
    def update(self, platforms, enemies):
        dist_x = self.player.rect.centerx - self.rect.centerx
        dist_y = self.player.rect.centery - self.rect.centery

        if abs(dist_x) > 5:
            if dist_x > 0: self.rect.x += ENEMY_SPEED
            else: self.rect.x -= ENEMY_SPEED
        elif abs(dist_y) > 50:
            if self.rect.centerx < SCREEN_WIDTH // 2:
                self.rect.x += ENEMY_SPEED
            else:
                self.rect.x -= ENEMY_SPEED
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0

        for other in enemies:
            if other != self: 
                if self.rect.colliderect(other.rect):
                    if self.rect.centerx < other.rect.centerx:
                        self.rect.x -= ENEMY_SPEED 
                    else:
                        self.rect.x += ENEMY_SPEED 
    
    def draw_custom(self, surface, shake_x=0, shake_y=0):
        draw_rect = self.rect.move(shake_x, shake_y)
        pygame.draw.rect(surface, RED, draw_rect)
        pygame.draw.rect(surface, BLACK, (draw_rect.x + 5, draw_rect.y + 10, 8, 8))
        pygame.draw.rect(surface, BLACK, (draw_rect.right - 13, draw_rect.y + 10, 8, 8))
        pygame.draw.line(surface, BLACK, (draw_rect.x + 2, draw_rect.y + 8), (draw_rect.x + 15, draw_rect.y + 15), 3)
        pygame.draw.line(surface, BLACK, (draw_rect.right - 2, draw_rect.y + 8), (draw_rect.right - 15, draw_rect.y + 15), 3)


def init_game():
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    items = pygame.sprite.Group() # [아이템 그룹]

    platforms.add(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20, GREEN))
    platforms.add(Platform(50, 450, 150, 20))
    platforms.add(Platform(0, 350, 100, 20))
    platforms.add(Platform(SCREEN_WIDTH - 200, 450, 150, 20))
    platforms.add(Platform(SCREEN_WIDTH - 100, 350, 100, 20))
    platforms.add(Platform(300, 250, 200, 20))
    platforms.add(Platform(250, 520, 50, 60))
    platforms.add(Platform(500, 520, 50, 60))
    platforms.add(Platform(300, 420, 200, 20))

    for p in platforms:
        all_sprites.add(p)

    player = Player(SCREEN_WIDTH // 2, 200)
    all_sprites.add(player)

    return player, all_sprites, platforms, bullets, enemies, items

def draw_text_center(surf, text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset)
    surf.blit(text_surface, rect)

def draw_hearts(surf, lives):
    for i in range(lives):
        x = 10 + (i * 40)
        y = 50 
        pygame.draw.circle(surf, RED, (x + 10, y + 10), 10)
        pygame.draw.circle(surf, RED, (x + 25, y + 10), 10)
        pygame.draw.polygon(surf, RED, [(x, y + 15), (x + 35, y + 15), (x + 17, y + 35)])

def main():
    game_state = STATE_MENU 
    
    player = None
    all_sprites = None
    platforms = None
    bullets = None
    enemies = None
    items = None

    score = 0
    start_ticks = 0 
    final_time = 0  
    high_scores = [0, 0, 0] 
    player_lives = 3 

    particles = []          
    screen_shake = 0        
    background_stars = [Star() for _ in range(50)] 

    ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ENEMY_SPAWN_EVENT, 1500) 

    # [아이템 생성 타이머 (7초마다)]
    ITEM_SPAWN_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(ITEM_SPAWN_EVENT, 7000)

    current_volume = 0.5
    try:
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.set_volume(current_volume)
        pygame.mixer.music.play(-1)
        print("배경음악 재생 성공")
    except:
        print("주의: music.mp3 파일을 찾을 수 없습니다.")

    # === 버튼 생성 ===
    btn_width, btn_height = 250, 60
    center_x = SCREEN_WIDTH // 2 - btn_width // 2
    
    btn_start = Button("GAME START", center_x, 250, btn_width, btn_height, BTN_RED)
    btn_guide = Button("HOW TO PLAY", center_x, 330, btn_width, btn_height, BTN_GREEN)
    btn_option = Button("OPTION", center_x, 410, btn_width, btn_height, BTN_BLUE)
    btn_exit = Button("EXIT", center_x, 490, btn_width, btn_height, BTN_YELLOW)
    
    menu_buttons = [btn_start, btn_guide, btn_option, btn_exit]

    btn_back = Button("BACK", center_x, 500, btn_width, btn_height, GREY, WHITE)
    btn_vol_down = Button("-", center_x - 80, 300, 60, 60, GREY, WHITE)
    btn_vol_up = Button("+", center_x + 270, 300, 60, 60, GREY, WHITE)
    btn_pause_exit = Button("EXIT GAME", center_x, 400, btn_width, btn_height, BTN_YELLOW)

    running = True

    while running:
        clock.tick(FPS)

        if screen_shake > 0:
            screen_shake -= 1
        
        shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0

        # === 이벤트 처리 ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == STATE_MENU:
                if btn_start.is_clicked(event):
                    player, all_sprites, platforms, bullets, enemies, items = init_game()
                    score = 0
                    player_lives = 3 
                    start_ticks = pygame.time.get_ticks()
                    particles = []
                    game_state = STATE_PLAYING
                elif btn_guide.is_clicked(event):
                    game_state = STATE_GUIDE
                elif btn_option.is_clicked(event):
                    game_state = STATE_OPTION
                elif btn_exit.is_clicked(event):
                    running = False

            elif game_state == STATE_GUIDE:
                if btn_back.is_clicked(event):
                    game_state = STATE_MENU

            elif game_state == STATE_OPTION:
                if btn_back.is_clicked(event):
                    game_state = STATE_MENU
                
                if btn_vol_down.is_clicked(event):
                    current_volume = max(0.0, current_volume - 0.1)
                    pygame.mixer.music.set_volume(current_volume)
                elif btn_vol_up.is_clicked(event):
                    current_volume = min(1.0, current_volume + 0.1)
                    pygame.mixer.music.set_volume(current_volume)

            elif game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        if player: 
                            bullet = player.shoot()
                            all_sprites.add(bullet)
                            bullets.add(bullet)
                            screen_shake = 2
                    elif event.key == pygame.K_ESCAPE:
                        game_state = STATE_PAUSE
                
                if event.type == ENEMY_SPAWN_EVENT:
                    spawn_x = random.randint(0, SCREEN_WIDTH)
                    enemy = Enemy(spawn_x, -50, player)
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                
                # [아이템 생성 이벤트]
                if event.type == ITEM_SPAWN_EVENT:
                    ix = random.randint(50, SCREEN_WIDTH - 50)
                    item_type = random.choice(["speed", "shield", "heart"])
                    new_item = Item(ix, -30, item_type)
                    all_sprites.add(new_item)
                    items.add(new_item)

            elif game_state == STATE_PAUSE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_PLAYING
                
                if btn_vol_down.is_clicked(event):
                    current_volume = max(0.0, current_volume - 0.1)
                    pygame.mixer.music.set_volume(current_volume)
                elif btn_vol_up.is_clicked(event):
                    current_volume = min(1.0, current_volume + 0.1)
                    pygame.mixer.music.set_volume(current_volume)
                elif btn_pause_exit.is_clicked(event):
                    game_state = STATE_MENU

            elif game_state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player, all_sprites, platforms, bullets, enemies, items = init_game()
                        score = 0
                        player_lives = 3 
                        start_ticks = pygame.time.get_ticks()
                        particles = []
                        game_state = STATE_PLAYING
                    elif event.key == pygame.K_m: 
                        game_state = STATE_MENU

        # === 화면 그리기 ===
        screen.fill(BLACK)

        for star in background_stars:
            star.update()
            star.draw(screen)

        if game_state == STATE_MENU:
            draw_text_center(screen, "Shooting Python", font_title, BLUE, -200)
            for btn in menu_buttons:
                btn.draw(screen)

        elif game_state == STATE_GUIDE:
            draw_text_center(screen, "HOW TO PLAY", font_title, BTN_GREEN, -150)
            guide_rect = pygame.Rect(150, 200, 500, 250)
            pygame.draw.rect(screen, (30, 30, 40), guide_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, guide_rect, 2, border_radius=10)
            
            instructions = ["MOVE: Arrow Keys", "JUMP: Space", "SHOOT: Z Key", "RESTART: R Key"]
            for i, line in enumerate(instructions):
                text_surf = font_ui.render(line, True, WHITE)
                screen.blit(text_surf, (200, 230 + i*50))
            btn_back.draw(screen)

        elif game_state == STATE_OPTION:
            draw_text_center(screen, "OPTIONS", font_title, BTN_BLUE, -150)
            draw_text_center(screen, "MUSIC VOLUME", font_sub, WHITE, -50)
            bar_width = 300
            bar_height = 30
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = 315
            pygame.draw.rect(screen, GREY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            fill_width = int(bar_width * current_volume)
            pygame.draw.rect(screen, BTN_BLUE, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3, border_radius=5)
            vol_percent = int(current_volume * 100)
            draw_text_center(screen, f"{vol_percent}%", font_ui, WHITE, 20)
            btn_vol_down.draw(screen)
            btn_vol_up.draw(screen)
            btn_back.draw(screen)

        elif game_state == STATE_PLAYING:
            player.update(platforms)
            bullets.update()
            enemies.update(platforms, enemies)
            items.update() 

            for p in particles[:]:
                p.update()
                if p.life <= 0 or p.size <= 0:
                    particles.remove(p)

            # [아이템 획득 처리] (하트 먹고 죽는 버그 수정됨)
            item_hits = pygame.sprite.spritecollide(player, items, True)
            for item in item_hits:
                if item.item_type == "speed":
                    player.speed_buff = FPS * 5 # 5초간 지속
                elif item.item_type == "shield":
                    player.shield = True
                elif item.item_type == "heart":
                    # [버그 수정] 목숨 최대 3개까지만 증가 (3개 미만일 때만 +1)
                    if player_lives < 3:
                        player_lives += 1

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for enemy, bullet_list in hits.items():
                score += 100
                screen_shake = 10 
                for _ in range(10):
                    particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, ORANGE))
                    particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, RED))
            
            if pygame.sprite.spritecollide(player, enemies, False):
                if player.get_hit(): # 데미지를 입었으면 (쉴드 X, 무적 X)
                    player_lives -= 1
                    screen_shake = 30 
                    
                    for _ in range(20):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, BLUE))

                    if player_lives <= 0:
                        final_time = (pygame.time.get_ticks() - start_ticks) / 1000
                        high_scores.append(score)
                        high_scores.sort(reverse=True)
                        high_scores = high_scores[:3]
                        game_state = STATE_GAMEOVER
                else:
                    # [수정됨] 쉴드 깨질 때 노란 파편 효과 삭제 (코드 제거됨)
                    pass

            for sprite in all_sprites:
                if sprite != player and sprite not in enemies and sprite not in items:
                    screen.blit(sprite.image, (sprite.rect.x + shake_x, sprite.rect.y + shake_y))
            
            for item in items: # 아이템 그리기
                screen.blit(item.image, (item.rect.x + shake_x, item.rect.y + shake_y))

            for bullet in bullets:
                 screen.blit(bullet.image, (bullet.rect.x + shake_x, bullet.rect.y + shake_y))

            player.draw_custom(screen, shake_x, shake_y)
            for enemy in enemies:
                enemy.draw_custom(screen, shake_x, shake_y)

            for p in particles:
                p.draw(screen, shake_x, shake_y)

            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
            score_text = font_ui.render(f"Score: {score}", True, WHITE)
            time_text = font_ui.render(f"Time: {elapsed_seconds:.1f}s", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(time_text, (10, 85)) 
            
            draw_hearts(screen, player_lives)

        elif game_state == STATE_PAUSE:
            for sprite in all_sprites:
                if sprite != player and sprite not in enemies:
                    screen.blit(sprite.image, sprite.rect)
            for bullet in bullets:
                 screen.blit(bullet.image, bullet.rect)
            for item in items:
                screen.blit(item.image, item.rect)
            player.draw_custom(screen)
            for enemy in enemies:
                enemy.draw_custom(screen)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            draw_text_center(screen, "PAUSED", font_title, WHITE, -150)
            
            draw_text_center(screen, "MUSIC VOLUME", font_sub, WHITE, -50)
            bar_width = 300
            bar_height = 30
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = 315
            pygame.draw.rect(screen, GREY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            fill_width = int(bar_width * current_volume)
            pygame.draw.rect(screen, BTN_BLUE, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3, border_radius=5)
            vol_percent = int(current_volume * 100)
            draw_text_center(screen, f"{vol_percent}%", font_ui, WHITE, 20)

            btn_vol_down.draw(screen)
            btn_vol_up.draw(screen)
            btn_pause_exit.draw(screen)

        elif game_state == STATE_GAMEOVER:
            for p in platforms:
                screen.blit(p.image, p.rect)
            player.draw_custom(screen)
            for enemy in enemies:
                enemy.draw_custom(screen)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            draw_text_center(screen, "GAME OVER", font_title, RED, -200)
            result_text = f"YOUR SCORE: {score}    TIME: {final_time:.1f}s"
            draw_text_center(screen, result_text, font_ui, WHITE, -130)

            draw_text_center(screen, "--- TOP 3 HIGH SCORES ---", font_ui, GOLD, -60)
            for i, rank_score in enumerate(high_scores):
                rank_text = f"{i+1}. {rank_score} point"
                color = YELLOW if rank_score == score and score > 0 else WHITE
                draw_text_center(screen, rank_text, font_ui, color, -20 + (i * 40))

            draw_text_center(screen, "Press 'R' to Restart", font_sub, BLUE, 120)
            draw_text_center(screen, "Press 'M' for Main Menu", font_info, GREY, 170)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()