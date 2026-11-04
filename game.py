"""Midnight Dash: a small three-lane runner made with Pygame Zero."""

WIDTH = 720
HEIGHT = 560
TITLE = "Midnight Dash"

LANE_X = (220, 360, 500)
PLAYER_Y = 420
TRACK_TOP = 54
TRACK_BOTTOM = 548
ENEMY_PASS_CLEARANCE = 84
COLLISION_Y_DISTANCE = 56
RUN_SECONDS = 45.0
STARTING_HEALTH = 3
HIT_COOLDOWN = 1.0

ROAD = "#242a43"
ROAD_EDGE = "#58627e"
LANE_LINE = "#56617c"
CYAN = "#63f2dc"
PINK = "#ff6c9b"
WHITE = "#f5f7ff"
MUTED = "#aab4d0"


class Button:
    """A simple clickable menu button drawn with Pygame Zero."""

    def __init__(self, label, x, y, width, height, action):
        self.label = label
        self.rect = Rect((x, y), (width, height))
        self.action = action

    def draw(self):
        screen.draw.filled_rect(self.rect, "#26334e")
        screen.draw.rect(self.rect, "#71809d")
        screen.draw.text(
            self.label,
            center=self.rect.center,
            fontsize=25,
            color=WHITE,
        )

    def contains(self, point):
        return self.rect.collidepoint(point)


class AnimatedSprite:
    """Cycles through image files for idle and moving character states."""

    def __init__(self, idle_frames, moving_frames, position, frame_delay=0.14):
        self.actor = Actor(idle_frames[0], pos=position)
        self.frames = {"idle": idle_frames, "moving": moving_frames}
        self.state = "idle"
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_delay = frame_delay

    def set_position(self, position):
        self.actor.pos = position

    def update(self, dt, state=None):
        if state is not None and state != self.state:
            self.state = state
            self.frame_index = 0
            self.frame_timer = 0.0
            self.actor.image = self.frames[self.state][0]

        self.frame_timer += dt
        while self.frame_timer >= self.frame_delay:
            self.frame_timer -= self.frame_delay
            self.frame_index = (self.frame_index + 1) % len(
                self.frames[self.state]
            )
            self.actor.image = self.frames[self.state][self.frame_index]

    def draw(self):
        self.actor.draw()


class Player:
    """The runner: lane changes, health, collision grace time, and animation."""

    def __init__(self):
        self.sprite = AnimatedSprite(
            ["hero_idle_0", "hero_idle_1"],
            ["hero_run_0", "hero_run_1", "hero_run_2", "hero_run_3"],
            (LANE_X[1], PLAYER_Y),
            0.11,
        )
        self.lane = 1
        self.health = STARTING_HEALTH
        self.invulnerable = 0.0

    def reset(self):
        self.lane = 1
        self.health = STARTING_HEALTH
        self.invulnerable = 0.0
        self.sprite.set_position((LANE_X[self.lane], PLAYER_Y))
        self.sprite.update(0.0, "moving")

    def change_lane(self, direction):
        self.lane = max(0, min(len(LANE_X) - 1, self.lane + direction))
        self.sprite.set_position((LANE_X[self.lane], PLAYER_Y))

    def update(self, dt, moving=True):
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.sprite.update(dt, "moving" if moving else "idle")

    def take_hit(self):
        if self.invulnerable > 0.0:
            return False
        self.health -= 1
        self.invulnerable = HIT_COOLDOWN
        if audio_enabled:
            sounds.crash.play()
        return True

    def draw(self):
        if self.invulnerable <= 0.0 or int(self.invulnerable * 12) % 2 == 0:
            self.sprite.draw()


class Enemy:
    """A distinct enemy that zigzags within its assigned lane zone."""

    def __init__(self, idle_frames, moving_frames, lanes, y, speed, direction):
        self.lanes = lanes
        self.route_index = 0 if lanes[0] == 0 else len(lanes) - 1
        self.lane = lanes[self.route_index]
        self.y = y
        self.top = 92
        # Turn after passing the runner so a lane switch cannot hit at the
        # exact moment the enemy reaches the runner's depth.
        self.bottom = PLAYER_Y + ENEMY_PASS_CLEARANCE
        self.speed = speed
        self.direction = direction
        self.pause_timer = 0.0
        self.sprite = AnimatedSprite(
            idle_frames,
            moving_frames,
            (LANE_X[self.lane], self.y),
            0.15,
        )

    def change_patrol_lane(self):
        self.route_index = (self.route_index + 1) % len(self.lanes)
        self.lane = self.lanes[self.route_index]

    def update(self, dt):
        if self.pause_timer > 0.0:
            self.pause_timer = max(0.0, self.pause_timer - dt)
            self.sprite.update(dt, "idle")
            return

        self.y += self.speed * self.direction * dt
        if self.y >= self.bottom:
            self.y = self.bottom
            self.direction = -1
            self.change_patrol_lane()
            self.pause_timer = 0.38
        elif self.y <= self.top:
            self.y = self.top
            self.direction = 1
            self.change_patrol_lane()
            self.pause_timer = 0.38

        self.sprite.set_position((LANE_X[self.lane], self.y))
        self.sprite.update(dt, "idle" if self.pause_timer > 0.0 else "moving")

    def draw(self):
        self.sprite.draw()

    def touches(self, player):
        return (
            self.lane == player.lane
            and abs(self.sprite.actor.x - player.sprite.actor.x) < 72
            and abs(self.y - player.sprite.actor.y) < COLLISION_Y_DISTANCE
        )


player = Player()
enemies = []
game_state = "menu"
audio_enabled = True
elapsed_time = 0.0
road_offset = 0.0

menu_buttons = [
    Button("START GAME", 235, 236, 250, 54, "start"),
    Button("MUSIC AND SOUNDS: ON", 190, 306, 340, 54, "audio"),
    Button("EXIT", 235, 376, 250, 54, "exit"),
]
result_buttons = [
    Button("PLAY AGAIN", 235, 346, 250, 54, "restart"),
    Button("MAIN MENU", 235, 414, 250, 54, "menu"),
]

menu_player = AnimatedSprite(
    ["hero_idle_0", "hero_idle_1"],
    ["hero_run_0", "hero_run_1", "hero_run_2", "hero_run_3"],
    (360, 482),
    0.2,
)
menu_enemy_one = AnimatedSprite(
    ["hopper_idle_0", "hopper_idle_1"],
    ["hopper_run_0", "hopper_run_1", "hopper_run_2", "hopper_run_3"],
    (125, 482),
    0.2,
)
menu_enemy_two = AnimatedSprite(
    ["bat_idle_0", "bat_idle_1"],
    ["bat_run_0", "bat_run_1", "bat_run_2", "bat_run_3"],
    (595, 482),
    0.2,
)


def make_enemies():
    return [
        Enemy(
            ["hopper_idle_0", "hopper_idle_1"],
            ["hopper_run_0", "hopper_run_1", "hopper_run_2", "hopper_run_3"],
            (0, 1),
            178,
            142,
            1,
        ),
        Enemy(
            ["bat_idle_0", "bat_idle_1"],
            ["bat_run_0", "bat_run_1", "bat_run_2", "bat_run_3"],
            (1, 2),
            315,
            184,
            -1,
        ),
    ]


def update_audio_button():
    menu_buttons[1].label = (
        "MUSIC AND SOUNDS: ON" if audio_enabled else "MUSIC AND SOUNDS: OFF"
    )


def start_game():
    global game_state, elapsed_time, road_offset, enemies
    player.reset()
    enemies = make_enemies()
    elapsed_time = 0.0
    road_offset = 0.0
    game_state = "playing"
    if audio_enabled:
        music.play("midnight_run")


def finish_game(result):
    global game_state
    game_state = result
    player.sprite.set_position((360, 518))
    music.stop()
    if audio_enabled:
        if result == "won":
            sounds.win.play()
        else:
            sounds.lose.play()


def return_to_menu():
    global game_state
    game_state = "menu"
    music.stop()


def toggle_audio():
    global audio_enabled
    audio_enabled = not audio_enabled
    update_audio_button()
    if not audio_enabled:
        music.stop()
    elif game_state == "playing":
        music.play("midnight_run")
        sounds.click.play()


def on_key_down(key):
    if game_state == "playing":
        if key == keys.LEFT:
            player.change_lane(-1)
        elif key == keys.RIGHT:
            player.change_lane(1)
    elif game_state == "menu" and key == keys.RETURN:
        start_game()
    elif game_state in ("won", "lost") and key == keys.RETURN:
        start_game()


def on_mouse_down(pos, button):
    if button != mouse.LEFT or game_state == "playing":
        return

    visible_buttons = menu_buttons if game_state == "menu" else result_buttons
    for menu_button in visible_buttons:
        if menu_button.contains(pos):
            action = menu_button.action
            if action != "audio" and audio_enabled:
                sounds.click.play()
            if action == "start" or action == "restart":
                start_game()
            elif action == "audio":
                toggle_audio()
            elif action == "menu":
                return_to_menu()
            elif action == "exit":
                exit()
            return


def update(dt):
    global elapsed_time, road_offset
    if game_state == "menu":
        menu_player.update(dt, "idle")
        menu_enemy_one.update(dt, "idle")
        menu_enemy_two.update(dt, "idle")
        return

    if game_state != "playing":
        player.update(dt, False)
        return

    elapsed_time += dt
    road_offset = (road_offset + 210 * dt) % 62
    player.update(dt, True)
    for enemy in enemies:
        enemy.update(dt)
        if enemy.touches(player) and player.take_hit():
            if player.health <= 0:
                finish_game("lost")
                return

    if elapsed_time >= RUN_SECONDS:
        finish_game("won")


def draw_background():
    screen.fill("#171d35")

    # A quiet city skyline frames the road without requiring extra assets.
    buildings = ((8, 82, 184), (625, 86, 228), (78, 44, 122), (590, 38, 148))
    for x, width, height in buildings:
        building = Rect((x, TRACK_BOTTOM - height), (width, height))
        screen.draw.filled_rect(building, "#202945")
        for window_y in range(TRACK_BOTTOM - height + 18, TRACK_BOTTOM - 10, 28):
            for window_x in range(x + 13, x + width - 8, 22):
                screen.draw.filled_rect(Rect((window_x, window_y), (5, 8)), "#53607b")

    screen.draw.filled_rect(
        Rect((125, TRACK_TOP), (470, TRACK_BOTTOM - TRACK_TOP)), ROAD
    )
    screen.draw.filled_rect(
        Rect((125, TRACK_TOP), (8, TRACK_BOTTOM - TRACK_TOP)), ROAD_EDGE
    )
    screen.draw.filled_rect(
        Rect((587, TRACK_TOP), (8, TRACK_BOTTOM - TRACK_TOP)), ROAD_EDGE
    )

    for divider_x in (LANE_X[0] + 70, LANE_X[1] + 70):
        for dash_y in range(-62, HEIGHT + 62, 62):
            y = (dash_y + road_offset) % (HEIGHT + 62) - 31
            screen.draw.filled_rect(Rect((divider_x - 2, y), (4, 30)), LANE_LINE)

    for star_x, star_y in ((49, 44), (93, 232), (667, 58), (647, 310), (35, 350)):
        screen.draw.filled_circle((star_x, star_y), 2, "#b4c7ee")


def draw_hud():
    screen.draw.filled_rect(Rect((0, 0), (WIDTH, 48)), "#11162b")
    screen.draw.text("MIDNIGHT DASH", (22, 15), fontsize=22, color=CYAN)
    screen.draw.text(
        "HEALTH  " + str(player.health) + " / " + str(STARTING_HEALTH),
        center=(360, 23),
        fontsize=21,
        color=PINK,
    )
    remaining = max(0, int(RUN_SECONDS - elapsed_time + 0.99))
    screen.draw.text("TIME  " + str(remaining), (592, 15), fontsize=22, color=WHITE)

    bar = Rect((125, 523), (470, 9))
    screen.draw.filled_rect(bar, "#12182c")
    progress_width = int(470 * min(1.0, elapsed_time / RUN_SECONDS))
    if progress_width > 0:
        screen.draw.filled_rect(Rect((125, 523), (progress_width, 9)), CYAN)


def draw_menu():
    screen.draw.text("MIDNIGHT", center=(360, 105), fontsize=66, color=WHITE)
    screen.draw.text("DASH", center=(360, 164), fontsize=42, color=CYAN)
    screen.draw.text(
        "DODGE THE NIGHT CREATURES. REACH THE FINISH.",
        center=(360, 205),
        fontsize=17,
        color=MUTED,
    )
    for menu_button in menu_buttons:
        menu_button.draw()
    menu_enemy_one.draw()
    menu_player.draw()
    menu_enemy_two.draw()
    screen.draw.text("HOPPER", center=(125, 540), fontsize=14, color=MUTED)
    screen.draw.text("RUNNER", center=(360, 540), fontsize=14, color=MUTED)
    screen.draw.text("NIGHT BAT", center=(595, 540), fontsize=14, color=MUTED)


def draw_result():
    won = game_state == "won"
    heading = "YOU MADE IT!" if won else "NIGHT CAUGHT YOU"
    subtitle = "The finish line is yours." if won else "Try another route through the lanes."
    color = CYAN if won else PINK
    screen.draw.text(heading, center=(360, 215), fontsize=43, color=color)
    screen.draw.text(subtitle, center=(360, 267), fontsize=21, color=WHITE)
    screen.draw.text(
        "SURVIVED 45 SECONDS" if won else "OUT OF HEALTH",
        center=(360, 306),
        fontsize=18,
        color=MUTED,
    )
    player.sprite.draw()
    for result_button in result_buttons:
        result_button.draw()


def draw():
    draw_background()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        for enemy in enemies:
            enemy.draw()
        player.draw()
        screen.draw.text(
            "LEFT / RIGHT TO CHANGE LANES",
            center=(360, 502),
            fontsize=16,
            color=MUTED,
        )
        draw_hud()
    else:
        draw_result()
