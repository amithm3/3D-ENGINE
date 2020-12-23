import os
import tkinter as tk


class GUI(tk.Tk):
    def __init__(self, size=(750, 500), title='No Title', **configurations):
        self.configurations = configurations
        tk.Tk.__init__(self, **self.configurations)
        self.resizable(0, 0)
        self.size = size
        self.title(title)
        x, y = (self.winfo_screenwidth() - self.size[0]) // 2, (self.winfo_screenheight() - self.size[1]) // 4
        w, h = self.size[0], self.size[1]
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)

        self._set_input_frame()

        self.bot_frame = tk.Frame(self)
        self.model_button = tk.Button(self.bot_frame, text='Model It')
        self.model_button.grid(row=0, column=0)
        self.save_frame = tk.Frame(self.bot_frame)
        self.save_button = tk.Button(self.save_frame, text='Save It')
        self.save_button.pack(side='left')
        self.save_entry = tk.Entry(self.save_frame)
        self.save_entry.pack(side='right', fill='both', expand=True)
        self.save_frame.grid(row=0, column=1)
        self.load_var = tk.StringVar()
        self.load_var.set('Load')
        parent = os.path.dirname(os.getcwd()) + '/__data__'
        opts = os.listdir(parent)
        items = dict([(opt, os.listdir(parent + '/' + opt)) for opt in opts])
        self.load_button = tk.Menubutton(self.bot_frame, textvariable=self.load_var, indicatoron=True, relief='raised',
                                         borderwidth=2)
        self.topMenu = tk.Menu(self.load_button, tearoff=False)
        self.load_button.configure(menu=self.topMenu)
        for key in sorted(items.keys()):
            menu = tk.Menu(self.topMenu)
            self.topMenu.add_cascade(label=key, menu=menu)
            for value in items[key]:
                menu.add_radiobutton(label=value, variable=self.load_var, value=key+'/'+value)
        self.load_button.grid(row=0, column=2)
        self.bot_frame.pack()

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
        self.look_through_var = tk.IntVar()
        self.look_through_var.set(0)
        self.look_through = tk.Checkbutton(self.left_frame, text='Look Through', variable=self.look_through_var)
        self.look_through.grid(row=3, column=1)
        self.rotate_var = tk.IntVar()
        self.rotate_var.set(0)
        self.rotate_button = tk.Checkbutton(self.left_frame, text='Rotate', variable=self.rotate_var)
        self.rotate_button.grid(row=3, column=0)

        self.right_frame.pack(side='right')
        self.left_frame.pack(side='left')
        self.input_frame.pack()

    def draw_triangles(self, points_cluster, face_cluster, draw_orient=None, color=None):
        if color is None: color = self.winfo_rgb('white'); color = color[0] / 256, color[1] / 256, color[2] / 256
        self.canvas.delete('all')
        for face in face_cluster:
            face, shade = face[0], face[1]
            p1, p2, p3 = points_cluster[face[0]], points_cluster[face[1]], points_cluster[face[2]]
            col = '%02x%02x%02x' % (int(shade * color[0]), int(shade * color[1]), int(shade * color[2]))
            col = '#' + col
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
