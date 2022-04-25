class Application:
    def __init__(self):
        self.work_modeling = False
        self.History = []
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
        self.extra_counting = None
