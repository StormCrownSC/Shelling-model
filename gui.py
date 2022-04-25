import random, os, tkinter as tk, tkinter.messagebox as message
from tkinter import *
from tkinter import Scale
from tkinter.ttk import Notebook

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap


def show_error(text):
    message.showerror("Ошибка", text)


class Window(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.title("Модель сегрегации Шеллинга")
        self.minsize(width=1200, height=800)
        self.attributes('-zoomed', True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tab_control = Notebook(self)

        self.input_frame = InputFrame(self.tab_control, data)
        self.model_frame = ModelFrame(self.tab_control, data)
        self.stat_frame = StatFrame(self.tab_control, data)
        self.tab_control.add(self.input_frame, text="Панель ввода")
        self.tab_control.add(self.model_frame, text="Модель Шеллинга")
        self.tab_control.add(self.stat_frame, text="Статистика по модели")
        self.tab_control.pack(expand=True, fill=BOTH)

        self.shelling_model = Shelling_model(data, self.input_frame, self.model_frame, self.stat_frame)

    def on_closing(self):
        if message.askokcancel("Закрыть", "Вы уверены, что хотите выйти"):
            self.destroy()
            os._exit(0)


class InputFrame(tk.Frame):
    def __init__(self, window, data):
        super().__init__(window)
        self.window = window
        self.data = data
        self.visual_model = 0
        self.visual_graph = 0
        data.extra_counting = BooleanVar()

        self.generate_btn = self.button("Генерировать")
        self.generate_btn.place(relheight=0.1, relwidth=0.1, relx=0.6, rely=0.1)

        self.start_btn = self.button("Запуск")
        self.start_btn.place(relheight=0.1, relwidth=0.1, relx=0.8, rely=0.1)

        self.label_size_population = self.label("Размер популяции: ")
        self.label_size_population.place(relheight=0.05, relwidth=0.1, relx=0.03, rely=0.04)
        self.size_population_elem = Entry(self, width=40)
        self.size_population_elem.place(relheight=0.05, relwidth=0.08, relx=0.15, rely=0.04)
        self.size_population_elem.insert(0, data.size_population)

        self.label_size_map = self.label("Размер карты: ")
        self.label_size_map.place(relheight=0.05, relwidth=0.1, relx=0.03, rely=0.17)
        self.size_map_elem = Entry(self, width=40)
        self.size_map_elem.place(relheight=0.055, relwidth=0.08, relx=0.15, rely=0.17)
        self.size_map_elem.insert(0, data.size_map)

        self.optimal_distance_elem = Scale(self, from_=1, to=10, orient=HORIZONTAL, bg="grey", label="Дистанция")
        self.optimal_distance_elem.place(relheight=0.1, relwidth=0.1, relx=0.3, rely=0.01)
        self.optimal_distance_elem.set(data.optimal_distance)

        self.percentage_ratio_elem = Scale(self, from_=1, to=99, orient=HORIZONTAL, bg="grey",
                                           label="% соотношение")
        self.percentage_ratio_elem.place(relheight=0.1, relwidth=0.1, relx=0.3, rely=0.15)
        self.percentage_ratio_elem.set(data.percentage_ratio)

        self.value_tolerance_elem = Scale(self, from_=0, to=10, orient=HORIZONTAL, bg="grey",
                                          label="Толерантность")
        self.value_tolerance_elem.place(relheight=0.1, relwidth=0.1, relx=0.45, rely=0.01)
        self.value_tolerance_elem.set(data.value_tolerance)

        self.steps_elem = Scale(self, from_=0, to=100, orient=HORIZONTAL, bg="grey", label="Шагов")
        self.steps_elem.place(relheight=0.1, relwidth=0.1, relx=0.45, rely=0.15)
        self.steps_elem.set(data.steps)

        self.extra_counting_elem = Checkbutton(self, text='Дополнительные вычисления',
                                               variable=data.extra_counting, onvalue=True, offvalue=False,
                                               selectcolor='black')
        self.extra_counting_elem.place(relheight=0.03, relwidth=0.2, relx=0.01, rely=0.25)

    def button(self, text):
        return Button(self, text=text,
                      bg="Light gray",
                      fg="Black",
                      # font = ("Times New Roman"),
                      bd=2,
                      justify=CENTER,
                      width=15
                      )

    def label(self, text):
        return Label(self, text=text,
                     # bg="Light gray",
                     fg="White",
                     font=("Times new Roman", 10, "bold"),
                     bd=10,
                     justify=CENTER,
                     width=15)


class ModelFrame(tk.Frame):
    def __init__(self, window, data):
        super().__init__(window)
        self.window = window
        self.data = data


class StatFrame(tk.Frame):
    def __init__(self, window, data):
        super().__init__(window)
        self.window = window
        self.data = data


class Shelling_model:
    def __init__(self, data, input_frame, model_frame, stat_frame):
        self.data = data
        self.input_frame = input_frame
        self.model_frame = model_frame
        self.stat_frame = stat_frame
        input_frame.generate_btn.bind('<Button-1>', self.enter_data)
        input_frame.start_btn.bind('<Button-1>', self.start_modeling)
        self.visual_model = None
        self.visual_graph = None
        self.fill()

    def fill(self):
        try:
            self.data.Map = []
            self.data.graph_list = []
            self.data.graph_x = []
            temp_population_first = temp_population_second = 0
            rand_arr = []
            for i in range(0, self.data.size_map * self.data.size_map, 1):
                if temp_population_first < self.data.size_population_first:
                    rand_arr.append(0)
                    temp_population_first += 1
                elif temp_population_second < self.data.size_population_second:
                    rand_arr.append(2)
                    temp_population_second += 1
                else:
                    rand_arr.append(1)

            random.shuffle(rand_arr)
            for i in range(0, self.data.size_map, 1):
                temp_arr = []
                for j in range(0, self.data.size_map, 1):
                    temp_arr.append(rand_arr[i * self.data.size_map + j])
                self.data.Map.append(temp_arr)

            self.print_graph()
        except:
            show_error("Ошибка при генерации мира")

    def check_data(self):
        try:
            if 0 < self.data.size_population <= pow(self.data.size_map, 2) and self.data.size_map > 0:
                return True
            elif self.data.size_population <= 0:
                show_error("Численность популяции - число большее 0")
            elif self.data.size_map <= 0:
                show_error('Размер карты - число большее 0')
            elif self.data.size_population > pow(self.data.size_map, 2):
                show_error("Численность популяции не может превосходить размер карты")
            return False
        except:
            show_error("Ошибка при вводе данных! Введите число!")
            return False

    def read_data(self):
        try:
            self.data.size_population = int(self.input_frame.size_population_elem.get())
            self.data.size_map = int(self.input_frame.size_map_elem.get())
            self.data.optimal_distance = int(self.input_frame.optimal_distance_elem.get())
            self.data.percentage_ratio = int(self.input_frame.percentage_ratio_elem.get())
            self.data.value_tolerance = int(self.input_frame.value_tolerance_elem.get())
            self.data.steps = int(self.input_frame.steps_elem.get())
            self.data.size_population_first = int(self.data.size_population * (self.data.percentage_ratio / 100))
            if self.data.size_population_first == 0:
                self.data.size_population_first = 1
            self.data.size_population_second = self.data.size_population - self.data.size_population_first
            if self.check_data():
                return True
            return False
        except:
            show_error("Ошибка при вводе данных! Введите число!")
            return False

    def enter_data(self, event):
        if self.read_data():
            self.fill()
        else:
            show_error("Ошибка при вводе данных! Введите число!")

    def start_modeling(self, event):
        self.data.work_modeling = True

    def print_graph(self):
        fig = plt.figure(1)
        plt.clf()
        colours = (["brown", "grey", "blue"])
        cmap = ListedColormap(colours)
        labels = ['Первая\nгруппа', 'Свободное\nполе', 'Вторая\nгруппа']
        ticks = [0.3, 1, 1.7]
        graph_1 = plt.pcolormesh(self.data.Map, cmap=cmap, edgecolors="k", shading='flat')
        cb = plt.colorbar(graph_1, cmap=cmap, ticks=ticks)
        cb.set_ticklabels(labels)
        plt.axis("off")
        fig.subplots_adjust(top=1, bottom=0, left=0, right=1)
        self.visual_model = FigureCanvasTkAgg(fig, master=self.input_frame)
        plot_widget = self.visual_model.get_tk_widget()
        plot_widget.place(relheight=0.63, relwidth=0.63, relx=0.35, rely=0.3)

        graph_elem = plt.figure(2)
        graph_elem.clf()
        plt.title('Процент счастливых')
        plt.plot(self.data.graph_x, self.data.graph_list)
        plt.xlim([0, self.data.steps])
        plt.ylim([0, 101])
        self.visual_graph = FigureCanvasTkAgg(graph_elem, master=self.input_frame)
        plot_widget_1 = self.visual_graph.get_tk_widget()
        plot_widget_1.place(relheight=0.63, relwidth=0.3, relx=0.01, rely=0.3)
