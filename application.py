import random, time, os
from threading import Thread

import tkinter as tk
from tkinter import *
from tkinter import Scale
import tkinter.messagebox as message

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Модель сегрегации Шеллинга")
        self.minsize(width=1200, height=800)
        self.attributes('-zoomed', True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()

    def create_widgets(self):
        main_frame = MainFrame(self)
        model = Shelling_model(self)

    def on_closing(self):
        if message.askokcancel("Закрыть", "Вы уверены, что хотите выйти"):
            self.destroy()
            os._exit(0)


class MainFrame(tk.Frame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.create_widgets()

    def create_widgets(self):
        self.start_btn = self.button("Запуск")
        self.start_btn.place(relheight=0.1, relwidth=0.1, relx=0.7, rely=0.1)

        self.label_size_population = self.label("Размер популяции: ")
        self.label_size_population.place(relheight=0.05, relwidth=0.1, relx=0.03, rely=0.04)
        self.size_population_elem = Entry(self.window, width=40)
        self.size_population_elem.place(relheight=0.05, relwidth=0.08, relx=0.15, rely=0.04)
        self.size_population_elem.insert(0, "300")

        self.label_size_map = self.label("Размер карты: ")
        self.label_size_map.place(relheight=0.05, relwidth=0.1, relx=0.03, rely=0.17)
        self.size_map_elem = Entry(self.window, width=40)
        self.size_map_elem.place(relheight=0.055, relwidth=0.08, relx=0.15, rely=0.17)
        self.size_map_elem.insert(0, "20")

        self.optimal_distance_elem = Scale(self.window, from_=1, to=10, orient=HORIZONTAL, bg="grey", label="Дистанция")
        self.optimal_distance_elem.place(relheight=0.1, relwidth=0.1, relx=0.3, rely=0.01)
        self.optimal_distance_elem.set(2)

        self.percentage_ratio_elem = Scale(self.window, from_=1, to=99, orient=HORIZONTAL, bg="grey",
                                           label="% соотношение")
        self.percentage_ratio_elem.place(relheight=0.1, relwidth=0.1, relx=0.3, rely=0.15)
        self.percentage_ratio_elem.set(30)

        self.value_tolerance_elem = Scale(self.window, from_=0, to=10, orient=HORIZONTAL, bg="grey",
                                          label="Толерантность")
        self.value_tolerance_elem.place(relheight=0.1, relwidth=0.1, relx=0.45, rely=0.01)
        self.value_tolerance_elem.set(2)

        self.steps_elem = Scale(self.window, from_=0, to=100, orient=HORIZONTAL, bg="grey", label="Шагов")
        self.steps_elem.place(relheight=0.1, relwidth=0.1, relx=0.45, rely=0.15)
        self.steps_elem.set(10)

        self.extra_counting = BooleanVar()
        self.extra_counting_elem = Checkbutton(self.window, text='Дополнительные вычисления',
                                               variable=self.extra_counting, onvalue=True, offvalue=False,
                                               selectcolor='black')
        self.extra_counting_elem.place(relheight=0.03, relwidth=0.2, relx=0.01, rely=0.25)

        self.visual_model = 0
        self.visual_graph = 0

    def button(self, text):
        return Button(self.window, text=text,
                      bg="Light gray",
                      fg="Black",
                      # font = ("Times New Roman"),
                      bd=2,
                      justify=CENTER,
                      heigh=2,
                      width=15
                      )

    def label(self, text):
        return Label(self.window, text=text,
                     # bg="Light gray",
                     fg="White",
                     font=("Times new Roman", 10, "bold"),
                     bd=10,
                     justify=CENTER,
                     heigh=2,
                     width=15)

    def show_error(self, text):
        message.showerror("Ошибка", text)


class Shelling_model(MainFrame):
    def __init__(self, window):
        super().__init__(window)
        self.start_btn.bind('<Button-1>', self.start_modeling)
        self.stop_thread = True

        self.Map = []
        self.size_population = 300
        self.size_map = 20
        self.optimal_distance = 2
        self.percentage_ratio = 30
        self.value_tolerance = 2
        self.steps = 10
        self.size_population_first = self.size_population * (self.percentage_ratio / 100)
        self.size_population_second = self.size_population - self.size_population_first
        self.count_happy = 0
        self.graph_list = []
        self.graph_x = []

        self.fill()

    def fill(self):
        try:
            self.Map = []
            self.graph_list = []
            self.graph_x = []
            self.graph_x.append(0)
            temp_population_first = temp_population_second = 0
            rand_arr = []
            for i in range(0, self.size_map * self.size_map, 1):
                if temp_population_first < self.size_population_first:
                    rand_arr.append(0)
                    temp_population_first += 1
                elif temp_population_second < self.size_population_second:
                    rand_arr.append(2)
                    temp_population_second += 1
                else:
                    rand_arr.append(1)

            random.shuffle(rand_arr)
            for i in range(0, self.size_map, 1):
                temp_arr = []
                for j in range(0, self.size_map, 1):
                    temp_arr.append(rand_arr[i * self.size_map + j])
                self.Map.append(temp_arr)

            self.count_happy = self.counting_happy_agent()
            self.graph_list.append(100 * self.count_happy / self.size_population)
            self.print_graph()

        except:
            self.show_error("Ошибка при генерации мира")

    def another_agent(self, type):
        if type == 0:
            return 2
        if type == 2:
            return 0
        return 1

    def distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def is_happy(self, x, y, type):
        try:
            temp = 0
            for i in range(0, self.size_map, 1):
                if abs(i - y) <= self.optimal_distance:  # I don't now
                    for j in range(0, self.size_map, 1):
                        if self.distance(x, y, j, i) <= self.optimal_distance and self.Map[i][j] == type and not (
                                x == j and y == i):
                            temp += 1
                        if self.distance(x, y, j, i) <= self.optimal_distance and self.another_agent(
                                self.Map[i][j]) == type and not (x == j and y == i):
                            temp -= 13

            if temp < self.value_tolerance:
                return False
            else:
                return True
        except:
            self.show_error("Ошибка при определении счастья")
            return False

    def list_happy_position(self, type):
        try:
            array = []
            for i in range(0, self.size_map, 1):
                for j in range(0, self.size_map, 1):
                    if self.Map[i][j] == 1 and self.is_happy(j, i, type):
                        array.append([j, i])

            return array
        except:
            self.show_error("Ошибка при вычислении свободных 'счастливых' позиций")
            return []

    def list_agent_is_happy(self):
        try:
            array = []
            for i in range(0, self.size_map, 1):
                array_temp = []
                for j in range(0, self.size_map, 1):
                    if self.Map[i][j] != 1 and self.is_happy(j, i, self.Map[i][j]):
                        array_temp.append(True)
                    else:
                        array_temp.append(False)

                array.append(array_temp)

            return array
        except:
            self.show_error("Ошибка при определении 'счастья' у агентов")

    def list_free_position(self):
        try:
            array = []
            for i in range(0, self.size_map, 1):
                for j in range(0, self.size_map, 1):
                    if self.Map[i][j] == 1:
                        array.append([j, i])

            return array
        except:
            self.show_error("Ошибка при поиске свободных позиций")
            return []

    def counting_happy_agent(self):
        try:
            array = self.list_agent_is_happy()
            count = 0
            for i in range(0, self.size_map, 1):
                for j in range(0, self.size_map, 1):
                    if array[i][j] == True:
                        count += 1
            return count
        except:
            self.show_error("Ошибка при вычислении количества 'счастливых' агентов")
            return 0

    def check_data(self):
        try:
            if self.size_population > 0 and self.size_map > 0 and self.size_population <= pow(self.size_map, 2):
                return True
            elif self.size_population <= 0:
                self.show_error("Численность популяции - число большее 0")
            elif self.size_map <= 0:
                self.show_error("Размер карты - число большее 0")
            elif self.size_population > pow(self.size_map, 2):
                self.show_error("Численность популяции не может превосходить размер карты")
            return False
        except:
            self.show_error("Ошибка при вводе данных! Введите число!")
            return False

    def read_data(self):
        try:
            self.size_population = int(self.size_population_elem.get())
            self.size_map = int(self.size_map_elem.get())
            self.optimal_distance = int(self.optimal_distance_elem.get())
            self.percentage_ratio = int(self.percentage_ratio_elem.get())
            self.value_tolerance = int(self.value_tolerance_elem.get())
            self.steps = int(self.steps_elem.get())
            self.size_population_first = int(self.size_population * (self.percentage_ratio / 100))
            if self.size_population_first == 0:
                self.size_population_first = 1
            self.size_population_second = self.size_population - self.size_population_first
            if self.check_data():
                return True
            return False
        except:
            self.show_error("Ошибка при вводе данных! Введите число!")
            return False

    def end_modeling(self):
        try:
            for i in range(len(self.graph_list) - 1, self.steps + 1, 1):
                self.graph_x.append(i + 1)
                self.graph_list.append(100)
        except:
            self.show_error("Ошибка при досрочном завершении моделирования")

    def modeling(self, num):
        try:
            array = self.list_agent_is_happy()
            for i in range(0, self.size_map, 1):
                for j in range(0, self.size_map, 1):
                    if self.Map[i][j] != 1 and array[i][j] is False:
                        good_position = self.list_happy_position(self.Map[i][j])
                        if len(good_position) > 0:
                            random_int = int(random.uniform(0, len(good_position) - 1))
                            self.Map[good_position[random_int][1]][good_position[random_int][0]] = self.Map[i][j]
                            self.Map[i][j] = 1
                        else:
                            free = self.list_free_position()
                            if len(free) > 0:
                                random_int = int(random.uniform(0, len(free) - 1))
                                self.Map[free[random_int][1]][free[random_int][0]] = self.Map[i][j]
                                self.Map[i][j] = 1

                        if self.extra_counting.get() is True:
                            array = self.list_agent_is_happy()

            self.graph_x.append(num + 1)
            self.count_happy = self.counting_happy_agent()
            self.graph_list.append(100 * self.count_happy / self.size_population)

            if self.count_happy / self.size_population == 1:
                self.stop_thread = True
                self.end_modeling()
            self.print_graph()

        except:
            self.show_error("Ошибка при моделировании переселения")

    def start_modeling(self, event):
        try:
            if self.check_data() and self.stop_thread is True:
                if self.read_data():
                    self.fill()
                    self.stop_thread = False
                    modelize = Thread(target=self.work_modeling, daemon=True)
                    modelize.start()
        except:
            self.show_error("Ошибка при запуске потока")

    def work_modeling(self):
        try:
            for i in range(0, self.steps, 1):
                if self.stop_thread is False:
                    tic = time.perf_counter()
                    self.modeling(i)
                    toc = time.perf_counter()
                    result_timer = 2 - (toc - tic)
                    if result_timer < 0:
                        result_timer = 0
                    time.sleep(result_timer)
                else:
                    break
            self.stop_thread = True
        except:
            self.show_error("Ошибка внутри потока")

    def print_graph(self):
        fig = plt.figure(1)
        plt.clf()
        colours = (["brown", "grey", "blue"])
        cmap = ListedColormap(colours)
        labels = ['Первая\nгруппа', 'Свободное\nполе', 'Вторая\nгруппа']
        ticks = [0.3, 1, 1.7]
        graph_1 = plt.pcolormesh(self.Map, cmap=cmap, edgecolors="k", shading='flat')
        cb = plt.colorbar(graph_1, cmap=cmap, ticks=ticks)
        cb.set_ticklabels(labels)
        plt.axis("off")
        fig.subplots_adjust(top=1, bottom=0, left=0, right=1)
        self.visual_model = FigureCanvasTkAgg(fig, master=self.window)
        plot_widget = self.visual_model.get_tk_widget()
        plot_widget.place(relheight=0.63, relwidth=0.63, relx=0.35, rely=0.3)

        graph_elem = plt.figure(2)
        graph_elem.clf()
        plt.title('Процент счастливых')
        plt.plot(self.graph_x, self.graph_list)
        plt.xlim([0, self.steps])
        plt.ylim([0, 101])
        self.visual_graph = FigureCanvasTkAgg(graph_elem, master=self.window)
        plot_widget_1 = self.visual_graph.get_tk_widget()
        plot_widget_1.place(relheight=0.63, relwidth=0.3, relx=0.01, rely=0.3)
