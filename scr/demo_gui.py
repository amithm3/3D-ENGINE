import os
import tkinter as tk


class GUI(tk.Tk):
    def __init__(self, size=(750, 600), title='No Title', icon=None, **configurations):
        self.configurations = configurations
        tk.Tk.__init__(self, **self.configurations)
        self.attributes('-alpha', 0.0)
        self.resizable(0, 0)
        self.size = size
        self.title(title)
        if icon is not None:
            self.iconbitmap(os.path.dirname(os.getcwd())+'/'+icon)
        x, y = (self.winfo_screenwidth() - self.size[0]) // 2, (self.winfo_screenheight() - self.size[1]) // 4
        w, h = self.size[0], self.size[1]
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)

        self._set_input_frame()

        self.bot_frame = tk.Frame(self)
        self.model_button = tk.Button(self.bot_frame, text='Model It', bg='gray')
        self.model_button.grid(row=0, column=0, padx=5, pady=5)
        self.save_frame = tk.Frame(self.bot_frame)
        self.save_button = tk.Button(self.save_frame, text='Save It', bg='gray')
        self.save_button.pack(side='left', padx=(5, 0))
        self.save_frame.grid(row=0, column=1, padx=(0, 5))
        self.load_button = tk.Button(self.bot_frame, text='Load', relief='raised', bg='gray')
        self.load_button.grid(row=0, column=2, padx=5)
        self.bot_frame.pack()

        self.hl = ['', 'white']

        self.canvas.update_idletasks()
        self.add_x, self.add_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

        self.after(0, self.attributes, '-alpha', 1.0)

    # args: action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name
    @staticmethod
    def entry_validate(*args, digits=True, alpha=False, special_chars=(',', ' ', '.')):
        def check(char):
            if digits and char.isdigit(): return True
            if alpha and char.isalphs(): return True
            if char not in special_chars:
                return False
            else:
                return True

        if len(args[4]) == 1:
            return check(args[4])
        else:
            for char in args[4]:
                if not check(char): return False
            else:
                return True

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

        vcmd = (self.register(self.entry_validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.side = tk.Entry(self.left_frame, width=36, validatecommand=vcmd, validate='key')
        self.side.grid(row=0, column=1)
        self.side_text = tk.Label(self.left_frame, text='Side:')
        self.side_text.grid(row=0, column=0, sticky='e')
        self.radius = tk.Entry(self.left_frame, width=36, validatecommand=vcmd, validate='key')
        self.radius.grid(row=1, column=1)
        self.radius_text = tk.Label(self.left_frame, text='Radius:')
        self.radius_text.grid(row=1, column=0, sticky='e')
        self.separation = tk.Entry(self.left_frame, width=36, validatecommand=vcmd, validate='key')
        self.separation.grid(row=2, column=1)
        self.separation_text = tk.Label(self.left_frame, text='Separation:')
        self.separation_text.grid(row=2, column=0, sticky='e')

        self.rotate_var = tk.IntVar()
        self.rotate_var.set(0)
        self.rotate_button = tk.Checkbutton(self.left_frame, text='Turbulence', variable=self.rotate_var)
        self.rotate_button.grid(row=3, column=0)
        self.look_through_var = tk.IntVar()
        self.look_through_var.set(0)
        self.look_through = tk.Checkbutton(self.left_frame, text='Look Through', variable=self.look_through_var)
        self.look_through.grid(row=3, column=1)
        self.see_orient_var = tk.IntVar()
        self.see_orient_var.set(0)
        self.see_orient_button = tk.Checkbutton(self.left_frame, text='Show Orient', variable=self.see_orient_var)
        self.see_orient_button.grid(row=3, column=2)

        self.right_frame.pack(side='right')
        self.left_frame.pack(side='left')
        self.input_frame.pack()

    def draw_triangles(self, points_cluster, face_cluster, draw_orient=None, color=None):
        if color is None:
            color = self.winfo_rgb('white')
            color = color[0] / 256, color[1] / 256, color[2] / 256
        self.canvas.delete('all')
        for face in face_cluster:
            face, shade = face[0], face[1]
            p1, p2, p3 = points_cluster[face[0]], points_cluster[face[1]], points_cluster[face[2]]
            col = '%02x%02x%02x' % (int(shade * color[0]), int(shade * color[1]), int(shade * color[2]))
            col = '#' + col
            self.canvas.create_polygon(p1[0][0] + self.add_x, p1[1][0] + self.add_y,
                                       p2[0][0] + self.add_x, p2[1][0] + self.add_y,
                                       p3[0][0] + self.add_x, p3[1][0] + self.add_y,
                                       outline=self.hl[0], fill=col)

        if draw_orient:
            self.draw_orient(draw_orient)

        self.canvas.update()

    def draw_orient(self, orient_cluster):
        for orient in orient_cluster:
            f, u, r, o = orient

            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y,
                                    f[0][0] + self.add_x, f[1][0] + self.add_y, fill='white', width=2)
            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y,
                                    u[0][0] + self.add_x, u[1][0] + self.add_y, fill='red', width=2)
            self.canvas.create_line(o[0][0] + self.add_x, o[1][0] + self.add_y,
                                    r[0][0] + self.add_x, r[1][0] + self.add_y, fill='green', width=2)