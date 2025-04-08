import pygame
import random
import time
import sys
import os
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen setup
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("One Night at Elektryk")

# Game states
MENU = 0
GAME = 1
JUMPSCARE = 2
WIN = 3
game_state = MENU

# Office states
OFFICE_NORMAL = 0
OFFICE_ANIMATRONIC = 1
OFFICE_TRAPPED = 2
OFFICE_FALSE_ALARM = 3
OFFICE_DARK = 4
office_state = OFFICE_DARK

# Timer
night_duration = 120
start_time = 0
current_time = 0

# Flash effect
flash_alpha = 0
is_flashing = False
flash_timer = 0
flash_duration = 0.5
fade_in_duration = 0.1
fade_out_duration = 0.4

# Sound flags
door_sound_played = False
jingle_played = False

# Load images
def load_image(name, size=None):
    try:
        img = pygame.image.load(f"assets/{name}")
        return img if not size else pygame.transform.scale(img, size)
    except:
        print(f"Failed to load image: assets/{name}, creating placeholder")
        surf = pygame.Surface(size if size else (100, 100))
        surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        return surf

# Load all images
images = {
    'menu_bg': load_image("menu_bg.png"),
    'office': [
        load_image("office_normal.png"),
        load_image("office_animatronic.png"),
        load_image("office_trapped.png"),
        load_image("office_false_alarm.png"),
        load_image("office_dark.png")
    ],
    'camera_bg': load_image("camera_bg.png", (WIDTH, HEIGHT)),
    'cam_showstage_empty': load_image("cam_showstage_empty.png", (600, 400)),
    'cam_showstage_anim': load_image("cam_showstage_anim.png", (600, 400)),
    'cam_dining_empty': load_image("cam_dining_empty.png", (600, 400)),
    'cam_dining_anim': load_image("cam_dining_anim.png", (600, 400)),
    'cam_backstage_empty': load_image("cam_backstage_empty.png", (600, 400)),
    'cam_backstage_anim': load_image("cam_backstage_anim.png", (600, 400)),
    'jumpscare': load_image("jumpscare.png", (WIDTH, HEIGHT)),
    'door_button': load_image("door_button.png", (150, 70)),
    'door_button_closed': load_image("door_button_closed.png", (150, 70)),
    'cam_button': load_image("cam_button.png", (100, 50)),
    'cam_button_active': load_image("cam_button_active.png", (100, 50)),
    'menu_button': load_image("menu_button.png", (200, 50)),
    'cam_select_button': load_image("cam_select_button.png", (90, 40))
}

# Load sounds with error handling
def load_sound(name, path):
    try:
        if os.path.exists(path):
            sound = mixer.Sound(path)
            print(f"Successfully loaded sound: {path}")
            return sound
        else:
            print(f"Sound file not found: {path}")
    except Exception as e:
        print(f"Error loading sound {path}: {str(e)}")
    # Return silent sound if loading fails
    return mixer.Sound(buffer=bytearray(1000))

# Load sounds with your specified filenames
sounds = {
    'menu_ambient': load_sound("Tape.ogg", "assets/Tape.ogg"),
    'office_ambient': load_sound("ambient.ogg", "assets/ambient.ogg"),
    'camera_on': load_sound("camIN.ogg", "assets/camIN.ogg"),
    'camera_off': load_sound("camOUT.ogg", "assets/camOUT.ogg"),
    'camera_switch': load_sound("click.ogg", "assets/click.ogg"),
    'door_close': load_sound("steps.ogg", "assets/steps.ogg"),
    'jumpscare_sound': load_sound("jumpscare.ogg", "assets/jumpscare.ogg"),
    'flash': load_sound("shutter.ogg", "assets/shutter.ogg"),
    'end_jingle': load_sound("6am.ogg", "assets/6am.ogg")
}

# Set volume levels
sounds['menu_ambient'].set_volume(0.5)
sounds['office_ambient'].set_volume(1.0)

# Buttons
door_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 100, 150, 70)
cam_button = pygame.Rect(WIDTH - 150, HEIGHT - 100, 100, 50)
cam_off_button = pygame.Rect(WIDTH - 150, HEIGHT - 100, 100, 50)  # Same position as cam_button
cam_select_buttons = [
    pygame.Rect(WIDTH - 120, 150 + i * 60, 90, 40) for i in range(3)
]

# Menu buttons
start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)

# Game variables
door_closed = False
power = 100
cam_active = False
current_cam = 0
cam_locations = ["Show Stage", "Dining Area", "Backstage"]
animatronic_location = 0
animatronic_movement_timer = 0
jumpscare_timer = 0
animatronic_in_office = False
animatronic_in_office_timer = 0
office_warning_time = 3.0
trapped_timer = 0
trapped_duration = 5.0
is_trapped = False

# Font
font = pygame.font.SysFont('Courier New', 22)

def reset_game():
    global door_closed, power, cam_active, current_cam
    global animatronic_location, animatronic_movement_timer, start_time, game_state
    global office_state, animatronic_in_office, is_trapped, trapped_timer, animatronic_in_office_timer
    global flash_alpha, is_flashing, flash_timer, door_sound_played, jingle_played

    door_closed = False
    power = 100
    cam_active = False
    current_cam = 0
    animatronic_location = 0
    animatronic_movement_timer = 0
    animatronic_in_office = False
    office_state = OFFICE_DARK
    is_trapped = False
    trapped_timer = 0
    animatronic_in_office_timer = 0
    flash_alpha = 0
    is_flashing = False
    flash_timer = 0
    door_sound_played = False
    jingle_played = False
    start_time = time.time()
    game_state = GAME
    
    # Stop all sounds and start office ambient
    for sound in sounds.values():
        sound.stop()
    sounds['office_ambient'].play(-1)  # Loop office ambient

def draw_menu():
    screen.blit(images['menu_bg'], (0, 0))
    screen.blit(images['menu_button'], start_button)
    screen.blit(font.render("START NIGHT 1", True, (0, 0, 0)), (start_button.x + 20, start_button.y + 10))
    screen.blit(images['menu_button'], quit_button)
    screen.blit(font.render("QUIT", True, (0, 0, 0)), (quit_button.x + 70, quit_button.y + 10))

def draw_office():
    # Draw dark office as base
    screen.blit(images['office'][OFFICE_DARK], (0, 0))
    
    # If flashing, overlay current state
    if is_flashing:
        current_state_img = images['office'][office_state].copy()
        current_state_img.set_alpha(flash_alpha)
        screen.blit(current_state_img, (0, 0))
    
    # Draw buttons (always visible except camera off button when in cams)
    screen.blit(images['door_button_closed'] if door_closed else images['door_button'], door_button)
    
    # Draw appropriate camera button
    if cam_active:
        screen.blit(images['cam_button_active'], cam_button)
    else:
        screen.blit(images['cam_button'], cam_button)
    
    # Draw UI (always visible)
    screen.blit(font.render(f"Power: {int(power)}%", True, (255, 255, 255)), (20, 20))
    screen.blit(font.render(f"Time: {int(night_duration - current_time)}", True, (255, 255, 255)), (WIDTH - 180, 20))

def draw_camera_view():
    # Draw fullscreen camera panel background
    screen.blit(images['camera_bg'], (0, 0))
    
    # Draw current camera feed (empty or with animatronic)
    cam_images = {
        0: 'cam_showstage_anim' if animatronic_location == 0 else 'cam_showstage_empty',
        1: 'cam_dining_anim' if animatronic_location == 1 else 'cam_dining_empty',
        2: 'cam_backstage_anim' if animatronic_location == 2 else 'cam_backstage_empty'
    }
    screen.blit(images[cam_images[current_cam]], (WIDTH//2 - 300, HEIGHT//2 - 200))
    
    # Draw camera label
    screen.blit(font.render(cam_locations[current_cam], True, (255, 255, 255)), (WIDTH//2 - 60, HEIGHT//2 - 240))

    # Draw camera select buttons
    for i, btn in enumerate(cam_select_buttons):
        screen.blit(images['cam_select_button'], btn)
        text = font.render(str(i+1), True, (255, 255, 255))
        screen.blit(text, (btn.x + btn.width//2 - text.get_width()//2, btn.y + btn.height//2 - text.get_height()//2))
    
    # Draw camera off button (visible only in camera view)
    screen.blit(images['cam_button_active'], cam_off_button)

def draw_jumpscare():
    screen.blit(images['jumpscare'], (0, 0))
    screen.blit(font.render("JUMPSCARE! YOU DIED!", True, (255, 255, 255)), (WIDTH//2 - 180, HEIGHT//2 - 20))

def draw_win():
    global jingle_played
    screen.fill((0, 0, 0))
    screen.blit(font.render("YOU SURVIVED THE NIGHT!", True, (255, 255, 255)), (WIDTH//2 - 180, HEIGHT//2 - 50))
    screen.blit(font.render("Click to return to menu", True, (255, 255, 255)), (WIDTH//2 - 170, HEIGHT//2 + 50))
    
    if not jingle_played:
        for sound in sounds.values():
            sound.stop()
        sounds['end_jingle'].play()
        jingle_played = True

def trigger_flash():
    global is_flashing, flash_timer, flash_alpha
    if not is_flashing:
        sounds['flash'].play()
        is_flashing = True
        flash_timer = time.time()
        flash_alpha = 0

def update_flash():
    global is_flashing, flash_alpha
    if is_flashing:
        elapsed = time.time() - flash_timer
        
        if elapsed < fade_in_duration:
            flash_alpha = int(255 * (elapsed / fade_in_duration))
        elif elapsed < fade_in_duration + fade_out_duration:
            fade_out_progress = (elapsed - fade_in_duration) / fade_out_duration
            flash_alpha = int(255 * (1 - fade_out_progress))
        else:
            is_flashing = False
            flash_alpha = 0

def update_game():
    global power, current_time, animatronic_location, animatronic_movement_timer
    global game_state, jumpscare_timer, current_cam, office_state, animatronic_in_office
    global door_closed, animatronic_in_office_timer, trapped_timer, is_trapped, door_sound_played

    current_time = time.time() - start_time
    
    # Update flash effect
    update_flash()
    
    # Drain power
    if door_closed:
        power -= 0.05
    if cam_active:
        power -= 0.03
    if is_flashing:
        power -= 0.1
    
    # Check for power outage
    if power <= 0:
        game_state = JUMPSCARE
        jumpscare_timer = time.time()
        sounds['jumpscare_sound'].play()
    
    # Check for win
    if current_time >= night_duration:
        game_state = WIN
    
    # Animatronic AI
    if not is_trapped:
        animatronic_movement_timer += 1
        if animatronic_movement_timer > 100:
            animatronic_movement_timer = 0
            if random.random() < 0.3:
                animatronic_location = min(animatronic_location + 1, 3)
    
    # Update office state
    if animatronic_location == 3:  # In office
        if not animatronic_in_office:
            animatronic_in_office = True
            animatronic_in_office_timer = time.time()
            is_trapped = False
        
        if door_closed:
            office_state = OFFICE_TRAPPED
            if not is_trapped:
                is_trapped = True
                trapped_timer = time.time()
                if not door_sound_played:
                    sounds['door_close'].play()
                    door_sound_played = True
            
            if time.time() - trapped_timer > trapped_duration:
                animatronic_location = 0
                animatronic_in_office = False
                door_closed = False
                is_trapped = False
                door_sound_played = False
        else:
            office_state = OFFICE_ANIMATRONIC
            is_trapped = False
            if time.time() - animatronic_in_office_timer > office_warning_time:
                game_state = JUMPSCARE
                jumpscare_timer = time.time()
                sounds['jumpscare_sound'].play()
    else:
        if animatronic_in_office:
            animatronic_in_office = False
            door_closed = False
            is_trapped = False
            door_sound_played = False
        elif door_closed:
            office_state = OFFICE_FALSE_ALARM
            if not door_sound_played:
                sounds['door_close'].play()
                door_sound_played = True
        else:
            office_state = OFFICE_NORMAL
            door_sound_played = False

# Main game loop
running = True
sounds['menu_ambient'].play(-1)  # Start menu music

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                animatronic_location = 2
            elif event.key == pygame.K_F2:
                animatronic_location = 3
            elif event.key == pygame.K_SPACE and game_state == GAME:
                trigger_flash()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_state == MENU:
                if start_button.collidepoint(mouse_pos):
                    sounds['menu_ambient'].stop()
                    reset_game()
                elif quit_button.collidepoint(mouse_pos):
                    running = False
            elif game_state == GAME:
                if door_button.collidepoint(mouse_pos):
                    door_closed = not door_closed
                    if door_closed:
                        sounds['door_close'].play()
                        door_sound_played = True
                    else:
                        door_sound_played = False
                elif not cam_active and cam_button.collidepoint(mouse_pos):
                    cam_active = True
                    sounds['camera_on'].play()
                    current_cam = 0
                elif cam_active and cam_off_button.collidepoint(mouse_pos):
                    cam_active = False
                    sounds['camera_off'].play()
                elif cam_active:
                    # Check camera select buttons
                    for i, btn in enumerate(cam_select_buttons):
                        if btn.collidepoint(mouse_pos) and i != current_cam:
                            current_cam = i
                            sounds['camera_switch'].play()
                            break
            elif game_state == JUMPSCARE and time.time() - jumpscare_timer > 2:
                game_state = MENU
                sounds['menu_ambient'].play(-1)
            elif game_state == WIN:
                game_state = MENU
                sounds['menu_ambient'].play(-1)

    if game_state == GAME:
        update_game()
    
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME:
        if cam_active:
            draw_camera_view()
        else:
            # Siema
            draw_office()
    elif game_state == JUMPSCARE:
        draw_jumpscare()
    elif game_state == WIN:
        draw_win()

    pygame.display.flip()
    pygame.time.delay(30)

# Clean up
for sound in sounds.values():
    sound.stop()
pygame.quit()
sys.exit()