from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty, BooleanProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ListProperty, OptionProperty
from kivy.event import EventDispatcher

import random

colors = {'default_background': (0, 0, 0, 0),# Black
          'move': (1, 0, 0, 1),# Redish
          'units_turn': (0, 0, 66, 1),# Blue?
          'attack': (0, 33, 66, 1)}

max_number_of_steps = 2

class Unit(Widget):
    health = NumericProperty(100)

    short_names = {'Empty': '',
                   'Stone': 'S',
                   'Archer': 'A',
                   'Wizard': 'W',
                   'Knight': 'K'}

    def __init__(self, type_of_unit="Empty", **kwargs):
        super(Unit, self).__init__(**kwargs)
        self.type_of_unit = type_of_unit
        self.short_name = self.short_names[type_of_unit]
        self.health = 0
        self.initial_health = 0
        self.damage = 0
        self.attack_range = 0
        self.player = 0

    def attack(self, damage):
        self.health = self.health - damage

    def dead(self):
        if self.health <= 0:
            return True


class Stone(Unit):
    def __init__(self, **kwargs):
        Unit.__init__(self, "Stone", **kwargs)


class Archer(Unit):
    def __init__(self, player, **kwargs):
        Unit.__init__(self, "Archer", **kwargs)
        self.health = 100
        self.initial_health = 100
        self.damage = 10
        self.attack_range = 6
        self.player = player


class Knight(Unit):
    def __init__(self, player, **kwargs):
        Unit.__init__(self, "Knight", **kwargs)
        self.health = 150
        self.initial_health = 150
        self.damage = 50
        self.attack_range = 1
        self.player = player


class Wizard(Unit):
    def __init__(self, player, **kwargs):
        Unit.__init__(self, "Wizard", **kwargs)
        self.health = 100
        self.initial_health = 100
        self.damage = 20
        self.attack_range = 4
        self.player = player


class StartScreen(Screen):
    def on_enter(*args):
        print("ENTER StartScreen")


class GridEntry(Button):
    coords = ListProperty([0, 0])
    possible_to_attack_this_grid = False
    possible_to_move_to_this_grid = False
    unit = Unit()


class GameScreen(Screen):
    pass


class ArcherGameBoard(BoxLayout):
    pass


class KnightGameBoard(BoxLayout):
    pass


class WizardGameBoard(BoxLayout):
    pass


class GameBoardGrid(GridLayout):
    player1_archer = Archer(1)
    player1_knight = Knight(1)
    player1_wizard = Wizard(1)
    player2_archer = Archer(2)
    player2_knight = Knight(2)
    player2_wizard = Wizard(2)
    number_of_cols = 9
    number_of_rows = 9
    active_coords = ListProperty([-1, -1])
    active_unit = Unit()
    player_turn = random.randint(1, 2)
    action_property = OptionProperty('none', options=('none', 'move', 'attack'))

    def __init__(self, **kwargs):
        super(GameBoardGrid, self).__init__(**kwargs)
        print("Enter _INIT_ GameBoardGrid")
        for row in range(self.number_of_rows):
            for column in range(self.number_of_cols):
                grid_entry = GridEntry(
                    coords=(row, column))
                grid_entry.bind(on_release=self.button_pressed)
                self.add_widget(grid_entry)
        self.clear_board()

        for child in self.children:
            if child.coords == [0, 2]:
                child.unit = self.player1_archer
            if child.coords == [0, 4]:
                child.unit = self.player1_knight
            if child.coords == [0, 6]:
                child.unit = self.player1_wizard
            if child.coords == [8, 2]:
                child.unit = self.player2_wizard
            if child.coords == [8, 4]:
                child.unit = self.player2_knight
            if child.coords == [8, 6]:
                child.unit = self.player2_archer
            if child.coords == [2, 3]:
                child.unit = Stone()
            if child.coords == [2, 5]:
                child.unit = Stone()
            if child.coords == [6, 3]:
                child.unit = Stone()
            if child.coords == [6, 5]:
                child.unit = Stone()

        self.draw_board()

    def clear_board(self):
        for child in self.children:
            child.background_color = colors['default_background']
            child.possible_to_move_to_this_grid = False
            child.possible_to_attack_this_grid = False
        self.draw_board()

    def draw_board(self):
        for child in self.children:
            child.text = child.unit.short_name
            if child.possible_to_attack_this_grid:
                child.background_color = colors['attack']
            elif child.possible_to_move_to_this_grid:
                child.background_color = colors['move']
            elif child.unit.short_name != '' and child.unit.player == self.player_turn:
                child.background_color = colors['units_turn']
            else:
                child.background_color = colors['default_background']

    def button_pressed(self, button):
        # Print output just to see what's going on
        print ('{} button clicked!'.format(button.coords))
        row, col = button.coords

        if button.coords == self.active_coords:
            self.active_coords = [-1, -1]
            self.clear_board()
        elif self.action_property == 'attack' and button.possible_to_attack_this_grid:
            button.unit.attack(self.active_unit.damage)
            if button.unit.dead():
                button.unit = Unit()
                self.active_coords = [-1, -1]
                self.player_turn = 1 if (self.player_turn == 2) else 2
                self.clear_board()
            print("ATTACKED : " + str(button.unit.health))
        elif self.action_property == 'move' and (isinstance(button.unit, Archer) or
                                                 isinstance(button.unit, Knight) or
                                                 isinstance(button.unit, Wizard)):
            if button.unit.player == self.player_turn:
                self.active_coords = button.coords
                self.active_unit = button.unit
                self.show_possible_moves(row, col)
        elif self.action_property == 'attack' and (isinstance(button.unit, Archer) or
                                                   isinstance(button.unit, Knight) or
                                                   isinstance(button.unit, Wizard)):
            if button.unit.player == self.player_turn:
                self.active_coords = button.coords
                self.active_unit = button.unit
                self.show_possible_targets(row, col, button.unit)
        elif self.action_property == 'move' and button.possible_to_move_to_this_grid:
            active_unit = ''
            for child in self.children:
                if child.coords == self.active_coords:
                    active_unit = child.unit
                    child.unit = Unit()
            button.unit = active_unit
            self.active_coords = [-1, -1]
            self.player_turn = 1 if (self.player_turn == 2) else 2
            self.clear_board()

    def show_possible_moves(self, row, col):
        move_table = [[0 for i in range(self.number_of_cols)] for j in range(self.number_of_rows)]
        self.clear_board()

        # Init move table
        for child in self.children:
            c_row, c_col = child.coords
            if child.unit.short_name != '':
                move_table[c_row][c_col] = -1
            else:
                move_table[c_row][c_col] = 99

        # Function to count moves over the full board
        def set_possible_moves(m_row, m_col, current):
            move_table[m_row][m_col] = current
            if current > max_number_of_steps:
                return
            try:
                if m_col == 0:
                    pass
                elif move_table[m_row][m_col - 1] > current + 1:
                    set_possible_moves(m_row, m_col - 1, current + 1)
            except IndexError:
                pass

            try:
                if move_table[m_row][m_col + 1] > current + 1:
                    set_possible_moves(m_row, m_col + 1, current + 1)
            except IndexError:
                pass

            try:
                if m_row == 0:
                    pass
                elif move_table[m_row - 1][m_col] > current + 1:
                    set_possible_moves(m_row - 1, m_col, current + 1)
            except IndexError:
                pass

            try:
                if move_table[m_row + 1][m_col] > current + 1:
                    set_possible_moves(m_row + 1, m_col, current + 1)
            except IndexError:
                pass

        set_possible_moves(row, col, 0)

        for child in self.children:
            test_row, test_col = child.coords
            if 0 < move_table[test_row][test_col] <= max_number_of_steps:
                child.possible_to_move_to_this_grid = True

        self.draw_board()

    def show_possible_targets(self, row, col, attack_unit):
        target_table = [[0 for i in range(self.number_of_cols)] for j in range(self.number_of_rows)]
        self.clear_board()

        # Init move table
        for child in self.children:
            c_row, c_col = child.coords

            if child.unit.type_of_unit == "Stone":
                target_table[c_row][c_col] = -1
            else:
                target_table[c_row][c_col] = 99

        # Function to count moves over the full board
        def set_possible_targets(m_row, m_col, current, dir_row, dir_col):
            target_table[m_row][m_col] = current

            if current > 6:
                return
            try:
                if self.number_of_rows < m_row + dir_row or \
                        m_row + dir_row < 0 or \
                        self.number_of_cols < (m_col + dir_col) or \
                        m_col + dir_col < 0:
                    pass
                elif target_table[m_row + dir_row][m_col + dir_col] > current + 1:
                    set_possible_targets(m_row + dir_row, m_col + dir_col, current + 1, dir_row, dir_col)
            except IndexError:
                pass

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dir_row, dir_col in directions:
            set_possible_targets(row, col, 0, dir_row, dir_col)

        for child in self.children:
            test_row, test_col = child.coords
            if 0 < target_table[test_row][test_col] <= attack_unit.attack_range:
                if child.unit.player != self.player_turn and child.unit.short_name != '':
                    child.possible_to_attack_this_grid = True

        self.draw_board()


class StrategyApp(App):

    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartScreen(name='start_screen'))
        sm.add_widget(GameScreen(name='game_screen'))
        return sm


if __name__ == '__main__':
    StrategyApp().run()
