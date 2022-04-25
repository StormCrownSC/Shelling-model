import time, gui
from numpy import random


class Shelling_calculating:
    def __init__(self, data, window):
        self.data = data
        self.window = window

    @staticmethod
    def another_agent(number):
        if number == 0:
            return 2
        if number == 2:
            return 0
        return 1

    @staticmethod
    def distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def is_happy(self, x, y, number):
        try:
            temp = 0
            for i in range(0, self.data.size_map, 1):
                if abs(i - y) <= self.data.optimal_distance:
                    for j in range(0, self.data.size_map, 1):
                        if self.distance(x, y, j, i) <= self.data.optimal_distance and self.data.Map[i][
                            j] == number and not (
                                x == j and y == i):
                            temp += 1
                        if self.distance(x, y, j, i) <= self.data.optimal_distance and self.another_agent(
                                self.data.Map[i][j]) == number and not (x == j and y == i):
                            temp -= 13

            if temp < self.data.value_tolerance:
                return False
            else:
                return True
        except:
            gui.show_error("Ошибка при определении счастья")
            return False

    def list_agent_is_happy(self):
        try:
            array = []
            for i in range(0, self.data.size_map, 1):
                array_temp = []
                for j in range(0, self.data.size_map, 1):
                    if self.data.Map[i][j] != 1 and self.is_happy(j, i, self.data.Map[i][j]):
                        array_temp.append(True)
                    else:
                        array_temp.append(False)

                array.append(array_temp)

            return array
        except:
            gui.show_error("Ошибка при определении 'счастья' у агентов")

    def counting_happy_agent(self):
        try:
            array = self.list_agent_is_happy()
            count = 0
            for i in range(0, self.data.size_map, 1):
                for j in range(0, self.data.size_map, 1):
                    if array[i][j]:
                        count += 1
            return count
        except:
            gui.show_error("Ошибка при вычислении количества 'счастливых' агентов")
            return 0

    def list_happy_position(self, type):
        try:
            array = []
            for i in range(0, self.data.size_map, 1):
                for j in range(0, self.data.size_map, 1):
                    if self.data.Map[i][j] == 1 and self.is_happy(j, i, type):
                        array.append([j, i])

            return array
        except Exception as exc:
            gui.show_error("Ошибка при вычислении свободных 'счастливых' позиций", exc)
            return []

    def list_free_position(self):
        try:
            array = []
            for i in range(0, self.data.size_map, 1):
                for j in range(0, self.data.size_map, 1):
                    if self.data.Map[i][j] == 1:
                        array.append([j, i])

            return array
        except Exception as exc:
            gui.show_error("Ошибка при поиске свободных позиций", exc)
            return []

    def end_modeling(self):
        try:
            for i in range(len(self.data.graph_list) - 1, self.data.steps + 1, 1):
                self.data.graph_x.append(i + 1)
                self.data.graph_list.append(100)
        except:
            gui.show_error("Ошибка при досрочном завершении моделирования")

    def modeling(self, num):
        try:
            array = self.list_agent_is_happy()
            for i in range(0, self.data.size_map, 1):
                for j in range(0, self.data.size_map, 1):
                    if self.data.Map[i][j] != 1 and array[i][j] is False:
                        good_position = self.list_happy_position(self.data.Map[i][j])
                        if len(good_position) > 0:
                            random_int = int(random.uniform(0, len(good_position) - 1))
                            self.data.Map[good_position[random_int][1]][good_position[random_int][0]] = \
                            self.data.Map[i][j]
                            self.data.Map[i][j] = 1
                        else:
                            free = self.list_free_position()
                            if len(free) > 0:
                                random_int = int(random.uniform(0, len(free) - 1))
                                self.data.Map[free[random_int][1]][free[random_int][0]] = self.data.Map[i][j]
                                self.data.Map[i][j] = 1

                        if self.data.extra_counting.get() is True:
                            array = self.data.list_agent_is_happy()

            self.data.graph_x.append(num + 1)
            self.data.count_happy = self.counting_happy_agent()
            self.data.graph_list.append(100 * self.data.count_happy / self.data.size_population)
            self.data.History.append(self.data.Map)

            if self.data.count_happy / self.data.size_population == 1:
                self.end_modeling()
                self.window.shelling_model.print_graph()
                return True

            self.window.shelling_model.print_graph()
            return False
        except Exception as exc:
            gui.show_error("Ошибка при моделировании переселения", exc)

    def start_calc(self):
        if self.data.work_modeling is True:
            self.data.History.append(self.data.Map)
            self.data.graph_x.append(0)
            self.data.count_happy = self.counting_happy_agent()
            self.data.graph_list.append(100 * self.data.count_happy / self.data.size_population)

            for i in range(0, self.data.steps, 1):
                if self.modeling(i):
                    break
            self.data.work_modeling = False

        time.sleep(1)
        self.start_calc()
