import tkinter as tk


class GUI(tk.Tk):
    def __init__(self, size=(250, 250), title='No Title', model_it_command=None, **configurations):
        self.configurations = configurations

        tk.Tk.__init__(self, **configurations)
        self.resizable(0, 0)
        if size is None:
            size = self.maxsize()

        self.size = size[0] - 100, size[1] - 100

        self.title(title)
        x, y = (self.winfo_screenwidth() - self.size[0]) // 2, (self.winfo_screenheight() - self.size[1]) // 4
        w, h = self.size[0], self.size[1]
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)

        self._set_input_frame()

        self.model_button = tk.Button(self, text='Model It', command=model_it_command)
        self.model_button.pack()

        self.frame = None
        self.hl = ''

        self.canvas.update_idletasks()
        self.add_x, self.add_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

    def _set_input_frame(self):
        self.input_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self.input_frame)
        self.left_frame = tk.Frame(self.input_frame)

        self.fov_bar_x = tk.Scale(self.right_frame, from_=0, to=360, length=180, orient='horizontal')
        self.fov_bar_x.grid(row=0, column=1)
        self.fov_bar_x_text = tk.Label(self.right_frame, text='Fov X:')
        self.fov_bar_x_text.grid(row=0, column=0, sticky='n')
        self.fov_bar_y = tk.Scale(self.right_frame, from_=0, to=360, length=180, orient='horizontal')
        self.fov_bar_y.grid(row=1, column=1)
        self.fov_bar_y_text = tk.Label(self.right_frame, text='Fov Y:')
        self.fov_bar_y_text.grid(row=1, column=0, sticky='n')

        self.side = tk.Entry(self.left_frame)
        self.side.grid(row=0, column=1)
        self.side_text = tk.Label(self.left_frame, text='Side:')
        self.side_text.grid(row=0, column=0, sticky='e')
        self.radius = tk.Entry(self.left_frame)
        self.radius.grid(row=1, column=1)
        self.radius_text = tk.Label(self.left_frame, text='Radius:')
        self.radius_text.grid(row=1, column=0, sticky='e')
        self.separation = tk.Entry(self.left_frame)
        self.separation.grid(row=2, column=1)
        self.separation_text = tk.Label(self.left_frame, text='Separation:')
        self.separation_text.grid(row=2, column=0, sticky='e')

        self.right_frame.pack(side='right')
        self.left_frame.pack(side='left')
        self.input_frame.pack()

    def draw_triangles(self, points_cluster, face_cluster, draw_orient=None, color=None):
        if color is None: color = self.winfo_rgb('peachpuff'); color = color[0] / 256, color[1] / 256, color[2] / 256
        self.canvas.delete('all')
        for face in face_cluster:
            face, shade = face[0], face[1]
            p1, p2, p3 = points_cluster[face[0]], points_cluster[face[1]], points_cluster[face[2]]
            col = '%02x%02x%02x' % (int(shade * color[0]), int(shade * color[1]), int(shade * color[2]))
            col = '#' + str(col)
            self.canvas.create_polygon(p1[0][0] + self.add_x, p1[1][0] + self.add_y,
                                       p2[0][0] + self.add_x, p2[1][0] + self.add_y,
                                       p3[0][0] + self.add_x, p3[1][0] + self.add_y,
                                       outline=self.hl, fill=col)

        if draw_orient:
            self.draw_orient(draw_orient)

        self.canvas.update()

    def draw_orient(self, orient_cluster):
        for orient in orient_cluster:
            f, u, r, o = orient

            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y, o[0][0] + f[0][0] + self.add_x,
                                    o[1][0] + f[1][0] + self.add_y, fill='white')
            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y, o[0][0] + u[0][0] + self.add_x,
                                    o[1][0] + u[1][0] + self.add_y, fill='red')
            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y, o[0][0] + r[0][0] + self.add_x,
                                    o[1][0] + r[1][0] + self.add_y, fill='green')
