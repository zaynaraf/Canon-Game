import json

from kivy.config import Config
from kivy.core.audio import SoundLoader

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '700')

import random
from math import cos, sin, radians

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.label import Label
from kivy.uix.widget import Widget

game_over = False
score = 0
level = 1


class CanonGame(Widget):
    x = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.help_label = Label(text="", pos=(Window.width / 2 - 50, Window.height / 2), size_hint=(None, None),
                                color=[0, 0, 0, 1])
        self.add_widget(self.help_label)

        self.help_clicked = False
        help_button = Button(text='Help', pos=(0, Window.height / 2))
        help_button.bind(on_release=self.show_help)
        self.add_widget(help_button)

        restart_button = Button(text='Restart', pos=(Window.width - 100, Window.height / 2))
        restart_button.bind(on_release=self.reset_game)
        self.add_widget(restart_button)

        save_button = Button(text='Save', pos=(0, Window.height / 2 - 100))
        save_button.bind(on_release=self.save_game)
        self.add_widget(save_button)

        load_button = Button(text='Load', pos=(Window.width - 100, Window.height / 2 - 100))
        load_button.bind(on_release=self.load_game)
        self.add_widget(load_button)

        with self.canvas:
            Color(0, 0, 1, 1)  # Blue color for cannon
            self.cannon = Rectangle(pos=(Window.width / 2 + self.x, 40), size=(40, 40))

            Color(1, 0, 0, 1)  # Red color for bullet
            self.bullet = Rectangle(pos=(self.cannon.pos[0] + 15, 60), size=(10, 30))

            Color(0, 1, 0, 1)  # Green color for missile
            self.missile = Ellipse(pos=(self.cannon.pos[0] + 15, 60), size=(10, 40))

        global score
        self.bullet_state = 'ready'
        self.bullet_speed = 40
        self.bullet_heading = 90
        self.gravity = 1
        self.bullet_dx = self.bullet_speed * cos(radians(self.bullet_heading))
        self.bullet_dy = self.bullet_speed * sin(radians(self.bullet_heading))
        self.missile_number = 3
        self.missile_state = 'not ready'
        self.missile_speed = 30
        self.missile_heading = 90
        self.missile_dx = self.missile_speed * cos(radians(self.missile_heading))
        self.missile_dy = self.missile_speed * sin(radians(self.missile_heading))

        self.scores = Label(text="Score: 0", pos=(0, Window.height - 60), font_size=24, color=[0, 0, 0, 1])
        self.add_widget(self.scores)

        self.level_text = Label(text="\nLevel: 1", pos=(0, Window.height - 105), font_size=24, color=[0, 0, 0, 1])
        self.add_widget(self.level_text)
        self.missile_numbers = Label(text='Missiles: ' + str(self.missile_number), pos=(12, Window.height - 90),
                                     font_size=24, color=[0, 0, 0, 1])
        self.add_widget(self.missile_numbers)

        self.game_over = Label(text='GAME OVER \n Score:' + str(score),
                               pos=(Window.width / 2 - 70, Window.height - 300),
                               font_size=24, color=[0, 0, 0, 1])

        self.Balls_list = []
        self.Blocks_list = []

        self.bullet_sound = SoundLoader.load('bullet.wav')
        self.missile_sound = SoundLoader.load('missile.wav')
        self.pop_sound = SoundLoader.load('pop.wav')
        self.game_over_sound = SoundLoader.load('gameOver.wav')

        with self.canvas.after:
            self.trajectory_line = Line(points=[], width=2, color=[1, 0, 0, 1])

        Clock.schedule_interval(self.update, 1 / 60)

    def save_game(self, instance):
        global score, level
        save_data = {'score': score, 'level': level, 'Missiles':self.missile_number}
        with open('save_game.json', 'w') as f:
            json.dump(save_data, f)

    def load_game(self, instance):
        global score, level
        try:
            with open('save_game.json', 'r') as f:
                save_data = json.load(f)
                score = save_data['score']
                level = save_data['level']
                self.missile_number = save_data['Missiles']

                self.scores.pos = (0, Window.height - 46)
                self.scores.text = f"\nScore: {score}"

                self.level_text.pos = (1, Window.height - 118)
                self.level_text.text = f'  Level : {level}'

                self.missile_numbers.pos = (18, Window.height - 90)
                self.missile_numbers.text = f'Missiles: {self.missile_number}'

                for enemy in self.Balls_list:
                    self.canvas.remove(enemy)
                self.Balls_list.clear()
                for Block in self.Blocks_list:
                    self.canvas.remove(Block)
                self.Blocks_list.clear()
        except FileNotFoundError:
            print("Save file not found")

    def show_help(self, instance):
        if self.help_clicked:
            self.help_label.text = ""
            self.help_clicked = False
        else:
            self.help_label.text = """
                Game mechanism:
                Shoot the balls with bullets while avoiding the red bricks 
                as they reflect back the bullets. After every 5 balls popped,
                1 missile can be obtained, which can be used to break red brick
                as well as to pop the balls. The number of balls falling and the
                speed of the balls falling increases as you reach higher level.
                Control: Press space button to shoot
                         right and left arrow to aim
                         a and d key to move the canon left and right
                         C button to switch between bullets and missiles

                         GOODLUCK! HAPPY SHOOTING!"""

            self.help_clicked = True

    def move_right(self):
        self.x += 10
        self.cannon.pos = (Window.width / 2 + self.x, 40)
        self.bullet.pos = (self.cannon.pos[0] + 15, 60)
        self.missile.pos = (self.cannon.pos[0] + 15, 60)

    def move_left(self):
        self.x -= 10
        self.cannon.pos = (Window.width / 2 + self.x, 40)
        self.bullet.pos = (self.cannon.pos[0] + 15, 60)
        self.missile.pos = (self.cannon.pos[0] + 15, 60)

    def update_trajectory_line(self):
        global game_over
        if game_over:
            self.trajectory_line.points = (0, 0, 0, 0)
        elif self.bullet_state == 'ready':
            start_x = self.bullet.pos[0] + self.bullet.size[0] / 2
            start_y = self.bullet.pos[1] + self.bullet.size[1]
            end_x = start_x + 100 * cos(radians(self.bullet_heading))
            end_y = start_y + 100 * sin(radians(self.bullet_heading))
            self.trajectory_line.points = (start_x, start_y, end_x, end_y)
        elif self.missile_state == 'ready':
            start_x = self.missile.pos[0] + self.missile.size[0] / 2
            start_y = self.missile.pos[1] + self.missile.size[1]
            end_x = start_x + 100 * cos(radians(self.missile_heading))
            end_y = start_y + 100 * sin(radians(self.missile_heading))
            self.trajectory_line.points = (start_x, start_y, end_x, end_y)

    def aim_left(self):
        if self.bullet_state == 'ready':
            self.bullet_heading += 10
            self.update_bullet_velocity()
            self.update_trajectory_line()
        elif self.missile_state == 'ready':
            self.missile_heading += 10
            self.update_missile_velocity()
            self.update_trajectory_line()

    def aim_right(self):
        if self.bullet_state == 'ready':
            self.bullet_heading -= 10
            self.update_bullet_velocity()
            self.update_trajectory_line()
        elif self.missile_state == 'ready':
            self.missile_heading -= 10
            self.update_missile_velocity()
            self.update_trajectory_line()

    def switch_bullet_missile(self):
        if self.bullet_state == 'ready':
            self.bullet_state = 'not ready'
            self.missile_state = 'ready'
        elif self.missile_state == 'ready':
            self.bullet_state = 'ready'
            self.missile_state = 'not ready'

    def update_bullet_velocity(self):
        self.bullet_dx = self.bullet_speed * cos(radians(self.bullet_heading))
        self.bullet_dy = self.bullet_speed * sin(radians(self.bullet_heading))

    def update_missile_velocity(self):
        self.missile_dx = self.missile_speed * cos(radians(self.missile_heading))
        self.missile_dy = self.missile_speed * sin(radians(self.missile_heading))


    def shoot(self):

        if self.bullet_state == 'ready':
            if True:
                self.bullet_sound.play()
            self.bullet_state = 'fire'
        elif self.missile_state == 'ready' and self.missile_number > 0:
                    self.missile_sound.play()
                    self.missile_state = 'fire'
                    self.missile_number -= 1
                    self.missile_numbers.pos = (18, Window.height - 90)
                    self.missile_numbers.text = f'Missiles: {self.missile_number}'

    def check_collision(self, projectile, target):
        bx, by = projectile.pos
        ex, ey = target.pos
        return (bx < ex + target.size[0] and bx + projectile.size[0] > ex and
                by < ey + target.size[1] and by + projectile.size[1] > ey)

    def update_missile_number(self):
        global score
        if score % 5 == 0:
            self.missile_number += 1
            self.missile_numbers.text = f'Missiles: {self.missile_number}'

    def update_level(self):
        global level, score
        if score % 10 == 0:
            level += 1
            self.level_text.pos = (1, Window.height - 118)
            self.level_text.text = f'  Level : {level}'

    def reset_bullet(self):
        self.bullet.pos = (self.cannon.pos[0] + 15, 60)
        self.bullet_state = 'ready'
        self.update_bullet_velocity()
        self.trajectory_line.points = []

    def reset_missile(self):
        self.missile.pos = (self.cannon.pos[0] + 15, 60)
        self.missile_state = 'ready'
        self.update_missile_velocity()
        self.trajectory_line.points = []

    def end_game(self):
        global game_over, score
        game_over = True

        self.canvas.clear()

        self.game_over.text = f'''
        GAME OVER
        Score:''' + str(score) + f'\n        Level:' + str(level)
        self.add_widget(self.game_over)


    def reset_game(self, instance):
        global score, level
        score = 0
        level = 1
        self.missile_number = 3
        self.missile_numbers.text = f'Missiles: {self.missile_number}'
        self.scores.pos = (1, Window.height - 60)
        self.scores.text = f"Score: {score}"
        self.level_text.pos = (1, Window.height - 118)
        self.level_text.text = f"Level: {level}"

        for enemy in self.Balls_list:
            self.canvas.remove(enemy)
        self.Balls_list.clear()
        for Block in self.Blocks_list:
            self.canvas.remove(Block)
        self.Blocks_list.clear()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'd':
            self.move_right()
        elif keycode[1] == 'a':
            self.move_left()
        elif keycode[1] == 'left':
            self.aim_left()
        elif keycode[1] == 'right':
            self.aim_right()
        elif keycode[1] == 'spacebar':
            self.shoot()
        elif keycode[1] == 'c':
            self.switch_bullet_missile()

    def update(self, dt):
        global game_over, score, level
        self.update_trajectory_line()

        if not game_over:
            if self.bullet_state == 'fire':
                self.bullet.pos = (self.bullet.pos[0] + self.bullet_dx, self.bullet.pos[1] + self.bullet_dy)
                self.bullet_dy -= self.gravity

                if (self.bullet.pos[1] < 0 or self.bullet.pos[0] > Window.width or
                        self.bullet.pos[0] < 0 or self.bullet.pos[1] > Window.height):
                    self.reset_bullet()

            if self.missile_state == 'fire':
                self.missile.pos = (self.missile.pos[0] + self.missile_dx, self.missile.pos[1] + self.missile_dy)
                self.missile_dy -= 0.1

                if self.missile.pos[1] < 0:
                    self.reset_missile()
                if self.missile.pos[0] > Window.width:
                    self.missile_dx = -self.missile_dx

                if self.missile.pos[0] < 0:
                    self.missile_dx = -self.missile_dx
                if self.missile.pos[1] > Window.height:
                    self.missile_dy = -self.missile_dy

            if len(self.Balls_list) < 10 + level and random.random() < 0.05:
                Ball = Ellipse(pos=(random.randint(150, Window.width - 150), Window.height), size=(50, 50))
                self.canvas.add(Color(random.random(), random.random(), random.random(), 1))
                self.canvas.add(Ball)
                self.Balls_list.append(Ball)
            if len(self.Blocks_list) < 3 + 0.25 * level and random.random() < 0.05:
                Block = Rectangle(pos=(random.randint(150, Window.width - 150), Window.height), size=(50, 10))
                self.canvas.add(Color(1, 0, 0, 1))
                self.canvas.add(Block)
                self.Blocks_list.append(Block)

            for Ball in self.Balls_list:
                Ball.pos = (Ball.pos[0], Ball.pos[1] - (0.3 + 0.01 * level))
                if Ball.pos[1] < -Ball.size[1] * 2:
                    self.game_over_sound.play()
                    self.end_game()
                elif self.check_collision(self.bullet, Ball):
                    self.canvas.remove(Ball)
                    self.Balls_list.remove(Ball)
                    self.reset_bullet()
                    sound3 = SoundLoader.load('pop.wav')
                    if True:
                        sound3.play()
                    score += 1
                    self.scores.pos = (0, Window.height - 46)
                    self.scores.text = f"\nScore: {score}"
                    self.update_missile_number()
                    self.update_level()
                elif self.check_collision(self.missile, Ball):
                    self.canvas.remove(Ball)
                    self.Balls_list.remove(Ball)
                    sound3= SoundLoader.load('pop.wav')
                    if True:
                        sound3.play()
                    score += 1
                    self.scores.pos = (0, Window.height - 46)
                    self.scores.text = f"\nScore: {score}"
                    self.update_missile_number()
                    self.update_level()

            for Block in self.Blocks_list:
                Block.pos = (Block.pos[0], Block.pos[1] - 0.5)
                if Block.pos[1] < Block.size[1]:
                    self.canvas.remove(Block)
                    self.Blocks_list.remove(Block)
                elif self.check_collision(self.bullet, Block):
                    self.bullet_dx = self.bullet_dx
                    self.bullet_dy = -self.bullet_dy
                elif self.check_collision(self.missile, Block):
                    self.canvas.remove(Block)
                    self.Blocks_list.remove(Block)

class CanonApp(App):
    def build(self):
        return CanonGame()


if __name__ == '__main__':
    CanonApp().run()
