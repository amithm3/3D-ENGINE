import pickle

import generator as gn
import demo_gui as gui
import threading as td

rd = gn.rd


class Main(gui.GUI):
    def __init__(self):
        gui.GUI.__init__(self, title="ENGINE", icon='__data__\icon.ico')

        self.model_button.configure(command=lambda: self.model_it())
        self.load_var_handler = lambda *_: self.load_model(self.load_var.get())
        self.load_var_trace_id = self.load_var.trace('wua', self.load_var_handler)
        self.save_button.configure(command=lambda: self.save_model(self.save_entry.get()) or self.canvas.focus_set())

        self.canvas.bind('<Button-1>', lambda event: self.canvas.focus_force())

        self.space = None
        self.object = None
        self.camera = None
        self.light = None

        self.loaded = False
        self.srz_info = None

    def save_model(self, fname):
        if fname == '':
            return
        with open(f'{gui.os.getcwd()}/__data__/Saves/{fname}.obj', 'wb') as save_file:
            pickle.dump(self.srz_info, save_file)
        self._file_handle()
        self.load_var.set(f'Saves/{fname}.obj')
        self.save_entry.delete(0, 'end')

    def load_model(self, fname):
        with open(f'{gui.os.getcwd()}/__data__/{fname}', 'rb') as save_file:
            data = list(pickle.load(save_file))

        self.side.delete(0, 'end'), self.radius.delete(0, 'end'), self.separation.delete(0, 'end')
        self.side.insert(0, data[0])
        data[1], data[2] = str(data[1]).replace('(', '').replace(')', ''), str(data[2]).replace('(', '').replace(')',
                                                                                                                 '')
        self.radius.insert(0, data[1])
        self.separation.insert(0, data[2])

        self.loaded = True
        self.model_it()

    def exec(self, expr):
        exec(expr, {'self': self})

    def key_bind(self):
        self.canvas.bind("<Up>", lambda event: self.camera.oriental_translation(0, 0.2, 0))
        self.canvas.bind("<Down>", lambda event: self.camera.oriental_translation(0, -0.2, 0))
        self.canvas.bind("<Right>", lambda event: self.camera.oriental_translation(0.2, 0, 0))
        self.canvas.bind("<Left>", lambda event: self.camera.oriental_translation(-0.2, 0, 0))
        self.canvas.bind("<space>", lambda event: self.camera.oriental_translation(0, 0, 0.2))
        self.canvas.bind("<BackSpace>", lambda event: self.camera.oriental_translation(0, 0, -0.2))
        self.canvas.bind('w', lambda event: self.camera.oriental_rotation(1, 0, 0))
        self.canvas.bind('s', lambda event: self.camera.oriental_rotation(-1, 0, 0))
        self.canvas.bind('d', lambda event: self.camera.oriental_rotation(0, 1, 0))
        self.canvas.bind('a', lambda event: self.camera.oriental_rotation(0, -1, 0))
        self.canvas.bind('z', lambda event: self.camera.oriental_rotation(0, 0, 1))
        self.canvas.bind('<Shift-Z>', lambda event: self.camera.oriental_rotation(0, 0, -1))

        self.canvas.bind("l", lambda event: [exec("light.lum += 1", {'light': light}) for light in self.space.lights])
        self.canvas.bind("<Shift-L>", lambda event: [exec("light.lum -= 1", {'light': light})
                                                     for light in self.space.lights])
        self.canvas.bind("c", lambda event: self.exec("self.camera.clarity += 0.1"))
        self.canvas.bind("<Shift-C>", lambda event: self.exec("self.camera.clarity -= 0.1"))
        self.canvas.bind("t", lambda event: self.exec("self.camera.shutter += 0.1"))
        self.canvas.bind("<Shift-T>", lambda event: self.exec("self.camera.shutter -= 0.1"))

        self.canvas.bind("h", lambda event: self.hl.reverse())

    def model_it(self):
        self.space = rd.Space((self.canvas.winfo_reqwidth(), self.canvas.winfo_height()))
        self.srz_info = eval(self.side.get()), eval(self.radius.get()), eval(self.separation.get())
        if not self.loaded:
            self.load_var.trace_vdelete('wua', self.load_var_trace_id)
            self.load_var.set('Load')
            self.load_var.trace('wua', self.load_var_handler)
        else:
            self.loaded = False
        self.object = gn.Spawn.parallelopiped(*self.srz_info)
        fov = self.canvas.winfo_width(), self.canvas.winfo_height()
        fov = 120 * fov[0] / sum(fov), 180 * fov[1] / sum(fov)
        self.camera = rd.Camera(fov=fov, shutter=3, clarity=1)
        self.light = rd.Light(360, 25)
        obj_center = self.object.vectors.mean(axis=0)
        self.space.add_object(self.object, location=(0, 0, 0))
        cam_d = rd.np.max(rd.np.sum(rd.np.square(self.object.vectors), axis=1)) ** 0.5
        self.space.add_camera(self.camera,
                              location=(obj_center[:3]).transpose()[0] + [0, -4 * cam_d, 0], orient=(0, 1, 0.))
        self.space.add_light(self.light, location=(obj_center[:3]).transpose()[0])

        self.fov_bar_x.set(self.camera.fov[0])
        self.fov_bar_y.set(self.camera.fov[1])
        self.fov_bar_x.configure(command=lambda event: self.camera.change_fov(self.fov_bar_x.get(),
                                                                              self.fov_bar_y.get()))
        self.fov_bar_y.configure(command=lambda event: self.camera.change_fov(self.fov_bar_x.get(),
                                                                              self.fov_bar_y.get()))
        self.look_through.configure(command=lambda: self.camera.change_thresh(self.look_through_var.get()))

        self.key_bind()
        self.canvas.focus_set()

        self.draw_triangles(*self.camera.capture())

        def loop():
            try:
                self.object.oriental_rotation(*(rd.np.random.random(3) * self.rotate_var.get()))
                self.draw_triangles(*self.camera.capture(self.see_orient_var.get()))
                self.after(0, loop)
            except gui.tk.TclError:
                pass

        td.Thread(target=loop, daemon=True).start()


if __name__ == '__main__':
    Main().mainloop()
