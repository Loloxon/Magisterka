class DroneInterface:
    def __init__(self, starting_position, color="black", name="unknown", params_id=-1, id=-1):
        self.doing_moves = None
        self.continuous_thread = None
        self.rectangle_id = None
        self.canvas = None
        self.map = None
        self.GUI = None
        self.x = starting_position[0]
        self.y = starting_position[1]
        self.drone_size = None
        self.color = color
        self.name = name
        self.params_id = params_id
        self.id = id
        self.max_signal = 0
        self.curr_signal = None

    def set_values(self, canvas, map, GUI, master):
        self.canvas = canvas
        self.map = map
        self.GUI = GUI
        self.drone_size = min(map.square_size * 0.8, 8)

        master.bind("<KeyPress>", self.on_key_press)

    def pause_moves(self):
        self.doing_moves = False

    def resume_moves(self):
        self.doing_moves = True

    def on_key_press(self, event):
        key = event.keysym
        if key == "Up":
            self.move(0, -2)
        if key == "Down":
            self.move(0, 2)
        if key == "Left":
            self.move(-2, 0)
        if key == "Right":
            self.move(2, 0)
        self.draw()
        self.print_value()

    def draw(self):
        if not self.GUI.simulation_hidden:
            x0 = self.x - self.drone_size // 2
            y0 = self.y - self.drone_size // 2
            x1 = self.x + self.drone_size // 2
            y1 = self.y + self.drone_size // 2

            if self.rectangle_id is None:
                self.rectangle_id = self.canvas.create_oval(x0, y0, x1, y1, fill="white", outline=self.color, width=3)

            self.canvas.coords(self.rectangle_id, x0, y0, x1, y1)

    def get_position(self):
        return self.x, self.y

    def move(self, d_x, d_y):
        self.x += d_x
        self.y += d_y
        return self.map.is_in_map(self)

    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def print_value(self):
        print(self.map.get_value_on((self.x, self.y), self.drone_size))

    def signal_received(self):
        return self.map.get_value_on((self.x, self.y), self.drone_size)
