"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os.path
import random
import threading

import remi.gui as gui
from remi import start, App


class Cell(gui.Widget):
    """
    Represent a cell in the minefield map
    """

    def __init__(self, width, height, x, y, game):
        super(Cell, self).__init__(width, height)
        self.x = x
        self.y = y
        self.has_mine = False
        self.state = 0  # unknown - doubt - flag
        self.opened = False
        self.nearest_mine = 0  # number of mines adjacent with this cell
        self.game = game

        self.style['font-weight'] = 'bold'
        self.style['text-align'] = 'center'
        self.style['background-size'] = 'contain'
        self.set_on_contextmenu_listener(self, 'on_right_click')
        self.set_on_click_listener(self, "check_mine")

    def on_right_click(self):
        """ Here with right click the change of cell is changed """
        if self.opened:
            return
        self.state = (self.state + 1) % 3
        self.set_icon()
        self.game.check_if_win()

    def check_mine(self, notify_game=True):
        if self.state == 1:
            return
        if self.opened:
            return
        self.opened = True
        if self.has_mine and notify_game:
            self.game.explosion(self)
            self.set_icon()
            return
        if notify_game:
            self.game.no_mine(self)
        self.set_icon()

    def set_icon(self):
        self.style['background-image'] = "''"
        if self.opened:
            if self.has_mine:
                self.style['background-image'] = "url('/res/mine.png')"
            else:
                if self.nearest_mine > 0:
                    self.append('nearestbomb', "%s" % self.nearest_mine)
                else:
                    self.style['background-color'] = 'rgb(200,255,100)'
            return
        if self.state == 2:
            self.style['background-image'] = "url('/res/doubt.png')"
        if self.state == 1:
            self.style['background-image'] = "url('/res/flag.png')"

    def add_nearest_mine(self):
        self.nearest_mine += 1


class MyApp(App):
    def __init__(self, *args):
        res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
        super(MyApp, self).__init__(*args, static_paths=(res_path,))

    def display_time(self):
        self.lblTime.set_text('Play time: ' + str(self.time_count))
        self.time_count += 1
        threading.Timer(1, self.display_time).start()

    def main(self):
        # the arguments are	width - height - layoutOrientationOrizontal
        self.main_container = gui.Widget(1020, 600, False, 10)

        self.title = gui.Label(1000, 30, 'Mine Field GAME')
        self.title.style['font-size'] = '25px'
        self.title.style['font-weight'] = 'bold'

        self.info = gui.Label(400, 30, 'Collaborative minefiled game. Enjoy.')
        self.info.style['font-size'] = '20px'

        self.lblMineCount = gui.Label(100, 30, 'Mines')
        self.lblFlagCount = gui.Label(100, 30, 'Flags')

        self.time_count = 0
        self.lblTime = gui.Label(100, 30, 'Time')

        self.btReset = gui.Button(100, 30, 'Restart')
        self.btReset.set_on_click_listener(self, "new_game")

        self.horizontal_container = gui.Widget(1000, 30, True, 0)
        self.horizontal_container.append('info', self.info)
        self.horizontal_container.append('icon_mine', gui.Image(30, 30, '/res/mine.png'))
        self.horizontal_container.append('info_mine', self.lblMineCount)
        self.horizontal_container.append('icon_flag', gui.Image(30, 30, '/res/flag.png'))
        self.horizontal_container.append('info_flag', self.lblFlagCount)
        self.horizontal_container.append('info_time', self.lblTime)
        self.horizontal_container.append('reset', self.btReset)

        self.minecount = 0  # mine number in the map
        self.flagcount = 0  # flag placed by the players

        self.link = gui.Link(1000, 20, "https://github.com/dddomodossola/remi",
                             "This is an example of REMI gui library.")

        self.main_container.append('title', self.title)
        self.main_container.append('horizontal_container', self.horizontal_container)
        self.main_container.append('link', self.link)

        self.new_game()

        self.display_time()
        # returning the root widget
        return self.main_container

    def coord_in_map(self, x, y, w=None, h=None):
        w = len(self.mine_matrix[0]) if w is None else w
        h = len(self.mine_matrix) if h is None else h
        return not (x > w - 1 or y > h - 1 or x < 0 or y < 0)

    def new_game(self):
        self.time_count = 0
        self.mine_table = gui.Table(900, 450)
        self.mine_matrix = self.build_mine_matrix(30, 15, 60)
        self.mine_table.from_2d_matrix(self.mine_matrix, False)
        self.main_container.append("mine_table", self.mine_table)
        self.check_if_win()

    def build_mine_matrix(self, w, h, minenum):
        """random fill cells with mines and increments nearest mines num in adiacent cells"""
        self.minecount = 0
        matrix = [[Cell(30, 30, x, y, self) for x in range(w)] for y in range(h)]
        for i in range(0, minenum):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            if matrix[y][x].has_mine:
                continue

            self.minecount += 1
            matrix[y][x].has_mine = True
            for coord in [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]:
                _x, _y = coord
                if not self.coord_in_map(x + _x, y + _y, w, h):
                    continue
                matrix[y + _y][x + _x].add_nearest_mine()
        return matrix

    def no_mine(self, cell):
        """opens nearest cells that are not near a mine"""
        if cell.nearest_mine > 0:
            return
        self.fill_void_cells(cell)

    def check_if_win(self):
        """Here are counted the flags. Is checked if the user win."""
        self.flagcount = 0
        win = True
        for x in range(0, len(self.mine_matrix[0])):
            for y in range(0, len(self.mine_matrix)):
                if self.mine_matrix[y][x].state == 1:
                    self.flagcount += 1
                    if not self.mine_matrix[y][x].has_mine:
                        win = False
                elif self.mine_matrix[y][x].has_mine:
                    win = False
        self.lblMineCount.set_text("%s" % self.minecount)
        self.lblFlagCount.set_text("%s" % self.flagcount)
        if win:
            self.dialog = gui.GenericDialog(title='You Win!', message='Game done in %s seconds' % self.time_count)
            self.dialog.set_on_confirm_dialog_listener(self, 'new_game')
            self.dialog.set_on_cancel_dialog_listener(self, 'new_game')
            self.dialog.show(self)

    def fill_void_cells(self, cell):
        checked_cells = [cell, ]
        while len(checked_cells) > 0:
            for cell in checked_cells[:]:
                checked_cells.remove(cell)
                if (not self.mine_matrix[cell.y][cell.x].has_mine) and \
                        (self.mine_matrix[cell.y][cell.x].nearest_mine == 0):
                    for coord in [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]:
                        _x, _y = coord
                        if not self.coord_in_map(cell.x + _x, cell.y + _y):
                            continue

                        if not self.mine_matrix[cell.y + _y][cell.x + _x].opened:
                            self.mine_matrix[cell.y + _y][cell.x + _x].check_mine(False)
                            checked_cells.append(self.mine_matrix[cell.y + _y][cell.x + _x])

    def explosion(self, cell):
        print("explosion")
        self.mine_table = gui.Table(900, 450)
        self.main_container.append("mine_table", self.mine_table)
        for x in range(0, len(self.mine_matrix[0])):
            for y in range(0, len(self.mine_matrix)):
                self.mine_matrix[y][x].style['background-color'] = 'red'
                self.mine_matrix[y][x].check_mine(False)
        self.mine_table.from_2d_matrix(self.mine_matrix, False)


if __name__ == "__main__":
    start(MyApp, multiple_instance=False, address='0.0.0.0', port=8081, debug=False)
