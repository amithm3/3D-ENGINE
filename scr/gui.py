import tkinter as tk


class GUI(tk.Tk):
    def __init__(self, size=(250, 250), title='No Title', command=None, **configurations):
        self.configurations = configurations
        self.size = size

        tk.Tk.__init__(self, **configurations)

        self.title(title)
        x, y = (self.winfo_screenwidth() - self.size[0]) // 2, (self.winfo_screenheight() - self.size[1]) // 3
        w, h = self.size[0], self.size[1]
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()
        self.resizable(0, 0)

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)

        self.input_frame = tk.Frame(self)
        self.side = tk.Entry(self.input_frame)
        self.side.grid(row=0, column=1)
        self.side_text = tk.Label(self.input_frame, text='Side:')
        self.side_text.grid(row=0, column=0, sticky='e')
        self.radius = tk.Entry(self.input_frame)
        self.radius.grid(row=1, column=1)
        self.radius_text = tk.Label(self.input_frame, text='Radius:')
        self.radius_text.grid(row=1, column=0, sticky='e')
        self.separation = tk.Entry(self.input_frame)
        self.separation.grid(row=2, column=1)
        self.separation_text = tk.Label(self.input_frame, text='Separation:')
        self.separation_text.grid(row=2, column=0, sticky='e')
        self.input_frame.pack()

        self.model_button = tk.Button(self, text='Model It', command=command)
        self.model_button.pack()

        self.frame = None
        self.hl = ''

        self.canvas.update_idletasks()
        self.add_x, self.add_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

    def draw_triangles(self, points_cluster, face_cluster, draw_orient=None, color=(1, 10, 255)):
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
