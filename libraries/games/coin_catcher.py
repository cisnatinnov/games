#!/usr/bin/env python3
# coin_catcher_arcade.py — Enhanced single-file Coin Catcher (no external assets)
# Features:
# - Start / Pause / Game Over screens
# - Lives, progressive difficulty, power-ups (gold, slow, heart)
# - Animated coins (spin + shine), gradient background, HUD
# - Procedural arcade-style sounds embedded (no files)
# - PyInstaller-friendly and robust audio fallback

import math
import os
import random
import sys
import time
import io
import struct
import wave

try:
    import pygame
except Exception as e:
    print("This game requires pygame. Install with: pip install pygame")
    raise

# ---------- Config ----------
WIDTH, HEIGHT = 900, 640
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 120, 20
PLAYER_Y = HEIGHT - 50

COIN_RADIUS = 16
COIN_BASE_SPEED = 160.0
COIN_SPEED_PER_SCORE = 1.4

START_SPAWN_INTERVAL = 0.95
MIN_SPAWN_INTERVAL = 0.2
SPAWN_ACCEL_PER_SCORE = 0.005

LIVES_START = 3
SLOW_TIME_DURATION = 4.0
SLOW_TIME_FACTOR = 0.48

P_GOLDEN = 0.12
P_SLOW = 0.08
P_HEART = 0.05

# Colors
WHITE = (245, 245, 245)
BLACK = (12, 12, 16)
BG1 = (20, 34, 78)
BG2 = (25, 95, 153)
GOLD = (255, 210, 50)
GOLD_DARK = (200, 160, 12)
RED = (235, 64, 52)
GREEN = (60, 200, 120)
CYAN = (0, 210, 255)
GRAY = (190, 190, 200)

# ---------- Utilities ----------
def resource_path(rel_path: str) -> str:
    """Compat helper for PyInstaller; not used for assets but kept for completeness."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

def clamp(x, a, b):
    return max(a, min(b, x))

def draw_text(surface, text, font, color, pos, center=True, shadow=True):
    if shadow:
        s = font.render(text, True, (10, 10, 10))
        rect = s.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        rect.move_ip(2, 2)
        surface.blit(s, rect)
    t = font.render(text, True, color)
    rect = t.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(t, rect)

def circle(surface, color, center, radius, width=0):
    pygame.draw.circle(surface, color, center, radius, width)

# ---------- Audio helpers (procedural WAV generation) ----------
def generate_sine_wav(frequency=440.0, duration=0.2, volume=0.6, sample_rate=44100):
    """Generate PCM16 WAV bytes for a sine tone."""
    n_samples = int(sample_rate * duration)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            v = volume * math.sin(2 * math.pi * frequency * t)
            # apply linear fade in/out to reduce clicks
            fade = 1.0
            fs = 0.02
            if t < fs:
                fade = t / fs
            elif t > duration - fs:
                fade = max(0.0, (duration - t) / fs)
            sample = int(32767 * v * fade)
            frames += struct.pack('<h', sample)
        wf.writeframes(frames)
    buf.seek(0)
    return buf

def make_sound_from_wav_bytes(buf):
    """Return pygame Sound from BytesIO WAV (if mixer available)."""
    try:
        return pygame.mixer.Sound(file=buf)
    except Exception:
        return None

def build_procedural_sounds():
    """Return dict of Sound objects or None if audio unavailable."""
    sounds = {}
    try:
        # Coin pickup: short bright arpeggio
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            frames = bytearray()
            notes = [880, 1100, 1320]  # quick arpeggio
            dur = 0.06
            for n in notes:
                samples = int(44100 * dur)
                for i in range(samples):
                    t = i / 44100
                    v = 0.7 * math.sin(2 * math.pi * n * t) * (1 - t/dur)
                    sample = int(32767 * v)
                    frames += struct.pack('<h', sample)
            wf.writeframes(frames)
        buf.seek(0)
        sounds['coin'] = pygame.mixer.Sound(file=buf)

        # Miss sound: low blip
        buf = generate_sine_wav(140.0, 0.18, 0.6)
        sounds['miss'] = make_sound_from_wav_bytes(buf)

        # Win / game over jingle (short)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            frames = bytearray()
            melody = [440, 660, 880, 1320]
            dur = 0.16
            for idx, n in enumerate(melody):
                samples = int(44100 * dur)
                for i in range(samples):
                    t = i / 44100
                    v = 0.6 * math.sin(2 * math.pi * n * t) * (1 - (idx / len(melody)) * 0.1)
                    sample = int(32767 * v * (1 - (i/samples)*0.2))
                    frames += struct.pack('<h', sample)
            wf.writeframes(frames)
        buf.seek(0)
        sounds['gameover'] = make_sound_from_wav_bytes(buf)

        # Background loop: simple repeating chiptune-ish bass + arpeggio assembled into a Sound and looped.
        # We'll create a 2-second clip and loop it
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            frames = bytearray()
            total_dur = 2.0
            sr = 44100
            for i in range(int(sr * total_dur)):
                t = i / sr
                # bass: saw-like using multiple sines
                bass = 0.2 * (math.sin(2 * math.pi * 110 * t) + 0.5 * math.sin(2 * math.pi * 220 * t))
                # arp: square-ish higher notes every 0.25s
                arp = 0.0
                beat = int((t * 4) % 4)
                if int(t * 4) % 2 == 0:
                    arp = 0.08 * math.sin(2 * math.pi * 660 * t)
                else:
                    arp = 0.05 * math.sin(2 * math.pi * 880 * t)
                sample = int(32767 * clamp(bass + arp, -1, 1))
                frames += struct.pack('<h', sample)
            wf.writeframes(frames)
        buf.seek(0)
        sounds['music'] = make_sound_from_wav_bytes(buf)
    except Exception:
        # Any audio error -> return empty mapping; game will continue without audio
        return {}
    return sounds

# ---------- Entities ----------
class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = PLAYER_Y
        self.speed = 520.0

    def update(self, dt, keys, mouse_pos):
        # keyboard or mouse control
        if mouse_pos is not None:
            self.rect.centerx = clamp(mouse_pos[0], self.rect.width // 2, WIDTH - self.rect.width // 2)
        else:
            vx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            self.rect.x += int(vx * self.speed * dt)
            self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)

    def render(self, surf, shake=(0,0)):
        r = self.rect.move(int(shake[0]), int(shake[1]))
        pygame.draw.rect(surf, (245,245,250), r, border_radius=12)
        pygame.draw.rect(surf, (170,180,210), r.inflate(-8, -8), border_radius=8)

class Coin:
    def __init__(self, x, y, speed):
        self.x = float(x)
        self.y = float(y)
        self.r = COIN_RADIUS
        self.speed = speed
        self.dead = False
        self.spin = random.uniform(0, math.tau)
        self.kind = "normal"

    def update(self, dt, slow_factor=1.0):
        self.y += self.speed * dt * slow_factor
        self.spin += dt * 6.0
        if self.y - self.r > HEIGHT + 50:
            self.dead = True

    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), int(self.r*2), int(self.r*2))

    def on_catch(self, game):
        game.score += self.value()

    def value(self):
        return 1

    def color(self):
        return GOLD

    def render(self, surf, shake=(0,0)):
        cx = int(self.x + shake[0])
        cy = int(self.y + shake[1])
        # glow
        for i in range(3, 0, -1):
            a = max(0, 60 - i*18)
            pygame.gfxdraw_filled_circle = getattr(pygame, "gfxdraw", None)
        # base coin
        pygame.draw.circle(surf, self.color(), (cx, cy), self.r)
        pygame.draw.circle(surf, GOLD_DARK, (cx, cy), self.r, 2)
        # inner shine arcs
        angle = (math.sin(self.spin) + 1) * 0.5 * math.pi * 0.9
        for i in range(2):
            rr = self.r - 3 - i*4
            if rr > 2:
                start = -angle * 0.5
                end = start + angle
                pygame.draw.arc(surf, WHITE, (cx-rr, cy-rr, rr*2, rr*2), start, end, 2)

class GoldenCoin(Coin):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed*0.9)
        self.kind = "golden"
        self.r = int(COIN_RADIUS * 1.25)

    def value(self):
        return 3

    def color(self):
        return (255, 235, 80)

class SlowCoin(Coin):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.kind = "slow"
        self.r = int(COIN_RADIUS * 1.15)

    def color(self):
        return CYAN

    def on_catch(self, game):
        game.slow_time_until = time.time() + SLOW_TIME_DURATION
        game.score += self.value()

class HeartCoin(Coin):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed*0.86)
        self.kind = "heart"
        self.r = int(COIN_RADIUS * 1.15)

    def color(self):
        return (255, 100, 130)

    def on_catch(self, game):
        game.lives = clamp(game.lives + 1, 0, 6)
        game.score += self.value()

# ---------- Game ----------
class Game:
    def __init__(self):
        pygame.init()
        # try to init mixer, but don't crash if it fails
        self.audio_available = True
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
        except Exception:
            self.audio_available = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Coin Catcher — Arcade")
        self.clock = pygame.time.Clock()

        # fonts
        self.big = pygame.font.SysFont("bahnschrift", 64, bold=True)
        self.med = pygame.font.SysFont("bahnschrift", 34)
        self.small = pygame.font.SysFont("bahnschrift", 20)

        # sounds
        self.sounds = {}
        if self.audio_available:
            try:
                self.sounds = build_procedural_sounds()
                # background music loop (if available)
                if 'music' in self.sounds and self.sounds.get('music'):
                    self.sounds['music'].set_volume(0.16)
                    self.sounds['music'].play(loops=-1)
            except Exception:
                self.sounds = {}
                self.audio_available = False

        # state
        self.state = 'menu'  # menu, play, pause, gameover
        self.reset()
        self.shake_time = 0.0
        self.shake_intensity = 0.0

    def reset(self):
        self.player = Player()
        self.coins = []
        self.score = 0
        self.lives = LIVES_START
        self.spawn_timer = 0.0
        self.spawn_interval = START_SPAWN_INTERVAL
        self.last_time = time.time()
        self.slow_time_until = 0.0
        self.mouse_control = True

    def spawn_coin(self):
        x = random.randint(30, WIDTH - 30)
        speed = COIN_BASE_SPEED + self.score * COIN_SPEED_PER_SCORE
        r = random.random()
        if r < P_HEART:
            c = HeartCoin(x, -COIN_RADIUS*2, speed * 0.9)
        elif r < P_HEART + P_SLOW:
            c = SlowCoin(x, -COIN_RADIUS*2, speed)
        elif r < P_HEART + P_SLOW + P_GOLDEN:
            c = GoldenCoin(x, -COIN_RADIUS*2, speed * 1.05)
        else:
            c = Coin(x, -COIN_RADIUS*2, speed)
        self.coins.append(c)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            if self.state == 'menu':
                self.render_menu()
            elif self.state == 'play':
                self.update_play(dt)
                self.render_play()
            elif self.state == 'pause':
                self.render_pause()
            elif self.state == 'gameover':
                self.render_gameover()
            pygame.display.flip()

    def handle_events(self):
        mouse_pos = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if self.state == 'menu':
                    if e.key == pygame.K_SPACE:
                        self.reset(); self.state = 'play'
                elif self.state == 'play':
                    if e.key == pygame.K_p:
                        self.state = 'pause'
                    if e.key == pygame.K_m:
                        # toggle mouse/keyboard
                        self.mouse_control = not self.mouse_control
                elif self.state == 'pause':
                    if e.key == pygame.K_p:
                        self.state = 'play'
                elif self.state == 'gameover':
                    if e.key in (pygame.K_r, pygame.K_SPACE):
                        self.reset(); self.state = 'play'
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'menu':
                    self.reset(); self.state = 'play'

        if self.mouse_control:
            mouse_pos = pygame.mouse.get_pos()
        self._mouse_pos = mouse_pos

        # keyboard pause toggle while playing (quick)
        keys = pygame.key.get_pressed()
        if self.state == 'play' and keys[pygame.K_p]:
            self.state = 'pause'

    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self._mouse_pos)

        slow_factor = SLOW_TIME_FACTOR if time.time() < self.slow_time_until else 1.0

        # spawn logic
        self.spawn_timer += dt
        target_interval = max(MIN_SPAWN_INTERVAL, START_SPAWN_INTERVAL - self.score * SPAWN_ACCEL_PER_SCORE)
        # smooth approach to target interval
        self.spawn_interval += (target_interval - self.spawn_interval) * 0.6 * dt * 60
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            self.spawn_coin()

        # update coins
        missed = 0
        for coin in self.coins:
            coin.update(dt, slow_factor)

        # collision detection
        caught = []
        for coin in self.coins:
            if coin.rect().colliderect(self.player.rect):
                # caught
                if self.audio_available and 'coin' in self.sounds and self.sounds['coin']:
                    try: self.sounds['coin'].play()
                    except: pass
                coin.on_catch(self)
                coin.dead = True
                self.shake(6.0, 0.06)

        # remove dead and count missed
        alive = []
        for coin in self.coins:
            if coin.dead:
                continue
            if coin.y - coin.r > HEIGHT + 10:
                missed += 1
            else:
                alive.append(coin)
        self.coins = alive

        if missed > 0:
            # penalize for missed coins
            self.lives -= missed
            if self.audio_available and 'miss' in self.sounds and self.sounds['miss']:
                try: self.sounds['miss'].play()
                except: pass
            self.shake(14.0 + 3 * missed, 0.24)
            if self.lives <= 0:
                self.state = 'gameover'
                if self.audio_available and 'gameover' in self.sounds and self.sounds['gameover']:
                    try: self.sounds['gameover'].play()
                    except: pass

        # update screen shake decay
        self.update_shake(dt)

    # screen shake
    def shake(self, intensity, duration):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_time = max(self.shake_time, duration)

    def update_shake(self, dt):
        if self.shake_time > 0:
            self.shake_time = max(0.0, self.shake_time - dt)
            self.shake_intensity *= math.exp(-6.0 * dt)
        else:
            self.shake_intensity = 0.0

    def get_shake_offset(self):
        if self.shake_time <= 0 or self.shake_intensity <= 0:
            return (0, 0)
        angle = random.random() * math.tau
        r = random.random() * self.shake_intensity
        return (math.cos(angle) * r, math.sin(angle) * r)

    # rendering
    def gradient_bg(self):
        # simple vertical gradient
        for i in range(0, HEIGHT, 4):
            t = i / HEIGHT
            c = (
                int(BG1[0] * (1 - t) + BG2[0] * t),
                int(BG1[1] * (1 - t) + BG2[1] * t),
                int(BG1[2] * (1 - t) + BG2[2] * t),
            )
            pygame.draw.rect(self.screen, c, pygame.Rect(0, i, WIDTH, 4))

    def render_menu(self):
        self.gradient_bg()
        draw_text(self.screen, "COIN CATCHER", self.big, WHITE, (WIDTH//2, HEIGHT//2 - 100))
        draw_text(self.screen, "Move: Mouse or ← → / A D   Pause: P   Toggle mouse: M", self.small, GRAY, (WIDTH//2, HEIGHT//2))
        draw_text(self.screen, "Catch coins. Missed coins cost lives.", self.small, GRAY, (WIDTH//2, HEIGHT//2 + 34))
        draw_text(self.screen, "Power-ups: Golden(×3), Cyan(Slow), Heart(+1 life)", self.small, GRAY, (WIDTH//2, HEIGHT//2 + 68))
        draw_text(self.screen, "Press SPACE or Click to Start", self.med, GREEN, (WIDTH//2, HEIGHT//2 + 140))

    def render_hud(self):
        # score
        draw_text(self.screen, f"Score: {self.score}", self.med, WHITE, (110, 32), center=False)

        # lives hearts
        for i in range(self.lives):
            x = WIDTH - 30 - i * 28
            draw_heart(self.screen, (x, 28), 10, RED)

        # slow-time indicator
        if time.time() < self.slow_time_until:
            tleft = max(0, self.slow_time_until - time.time())
            draw_text(self.screen, f"Slow: {tleft:0.1f}s", self.small, CYAN, (WIDTH//2, 28))

    def render_play(self):
        self.gradient_bg()
        shake = self.get_shake_offset()

        # render coins
        for coin in self.coins:
            coin.render(self.screen, shake)

        # render player
        self.player.render(self.screen, shake)

        # HUD
        self.render_hud()

    def render_pause(self):
        self.render_play()
        draw_text(self.screen, "PAUSED", self.big, WHITE, (WIDTH//2, HEIGHT//2 - 40))
        draw_text(self.screen, "Press P to Resume", self.med, WHITE, (WIDTH//2, HEIGHT//2 + 16))

    def render_gameover(self):
        self.gradient_bg()
        draw_text(self.screen, "GAME OVER", self.big, WHITE, (WIDTH//2, HEIGHT//2 - 80))
        draw_text(self.screen, f"Final Score: {self.score}", self.med, WHITE, (WIDTH//2, HEIGHT//2 - 16))
        draw_text(self.screen, "Press R or SPACE to Restart", self.med, GREEN, (WIDTH//2, HEIGHT//2 + 48))
        draw_text(self.screen, "ESC to Quit", self.small, GRAY, (WIDTH//2, HEIGHT//2 + 86))

def draw_heart(surface, center, size, color):
    cx, cy = center
    pts = []
    for t in [i * (math.pi/16) for i in range(33)]:
        x = size * 16 * math.sin(t) ** 3
        y = -size * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x/16, cy + y/16))
    pygame.draw.polygon(surface, color, pts)

# ---------- Entry ----------
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # ensure pygame quits cleanly on unexpected errors
        try:
            pygame.quit()
        finally:
            raise
