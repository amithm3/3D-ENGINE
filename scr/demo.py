import pickle

import scr.generator as gn
import scr.gui as gui
import scr.renderer as rd


class Main(gui.GUI):
    def __init__(self):
        gui.GUI.__init__(self, title="3D-ENGINE-Demo")
        self.model_button.configure(command=lambda: self.model_it())
        self.load_var.trace('wua', lambda *_: self.load_model(self.load_var.get()))
        self.rotate = self.rotate_var.get()
        self.rotate_var.trace('wua', lambda *_: exec("self.rotate=self.rotate_var.get()", {'self': self}))

        self.space = None
        self.object = None
        self.camera = None
        self.light = None

        self.loaded = False
        self.srz_info = None

    def save_model(self, fname):
        with open(f'{gui.os.path.dirname(gui.os.getcwd())}/__data__/Saves/{fname}', 'wb') as save_file:
            pickle.dump(self.srz_info, save_file)

    def load_model(self, fname):
        with open(f'{gui.os.path.dirname(gui.os.getcwd())}/__data__/{fname}', 'rb') as save_file:
            data = pickle.load(save_file)

        self.side.delete(0, 'end'), self.radius.delete(0, 'end'), self.separation.delete(0, 'end')
        self.side.insert(0, data[0])
        self.radius.insert(0, str(data[1])[1:-1])
        self.separation.insert(0, str(data[2])[1:-1])

        self.loaded = True
        self.model_it()

    def exec(self, expr):
        exec(expr, {'self': self})

    def key_bind(self):
        self.canvas.bind("<Up>", lambda event: self.camera.oriental_translation(0, 0.1, 0))
        self.canvas.bind("<Down>", lambda event: self.camera.oriental_translation(0, -0.1, 0))
        self.canvas.bind("<Right>", lambda event: self.camera.oriental_translation(0.1, 0, 0))
        self.canvas.bind("<Left>", lambda event: self.camera.oriental_translation(-0.1, 0, 0))
        self.canvas.bind("<space>", lambda event: self.camera.oriental_translation(0, 0, 0.1))
        self.canvas.bind("<BackSpace>", lambda event: self.camera.oriental_translation(0, 0, -0.1))
        self.canvas.bind('w', lambda event: self.camera.oriental_rotation(1, 0, 0))
        self.canvas.bind('s', lambda event: self.camera.oriental_rotation(-1, 0, 0))
        self.canvas.bind('d', lambda event: self.camera.oriental_rotation(0, 1, 0))
        self.canvas.bind('a', lambda event: self.camera.oriental_rotation(0, -1, 0))
        self.canvas.bind('z', lambda event: self.camera.oriental_rotation(0, 0, 1))
        self.canvas.bind('<Shift-Z>', lambda event: self.camera.oriental_rotation(0, 0, -1))

        self.canvas.bind("l", lambda event: [exec("light.lum += 1") for light in self.space.lights])
        self.canvas.bind("<Shift-L>", lambda event: [exec("light.lum -= 1") for light in self.space.lights])
        self.canvas.bind("c", lambda event: self.exec("self.camera.clarity += 0.1"))
        self.canvas.bind("<Shift-C>", lambda event: self.exec("self.camera.clarity -= 0.1"))
        self.canvas.bind("t", lambda event: self.exec("self.camera.shutter += 0.1"))
        self.canvas.bind("<Shift-T>", lambda event: self.exec("self.camera.shutter -= 0.1"))

        self.canvas.bind("h", lambda event: self.exec("self.hl='white'"))
        self.canvas.bind("<Shift-H>", lambda event: self.exec("self.hl=''"))

    def model_it(self):
        self.space = rd.Space((self.canvas.winfo_reqwidth(), self.canvas.winfo_height()))
        self.srz_info = eval(self.side.get()), eval(self.radius.get()), eval(self.separation.get())
        if not self.loaded:
            self.load_button.configure(text='Load')
        else:
            self.loaded = False
        self.object = gn.Spawn.parallelopiped(*self.srz_info)
        fov = self.canvas.winfo_width(), self.canvas.winfo_height()
        fov = 120 * fov[0] / sum(fov), 180 * fov[1] / sum(fov)
        self.camera = rd.Camera(fov=fov, shutter=1, clarity=1)
        self.light = rd.Light(360, 33)
        self.space.add_object(self.object, location=(0, 0, 10.))
        self.space.add_camera(self.camera, location=(0, 0, 0.), orient=(0, 0, 1.))
        self.space.add_light(self.light)

        self.fov_bar_x.set(self.camera.fov[0])
        self.fov_bar_y.set(self.camera.fov[1])
        self.fov_bar_x.configure(command=lambda event: self.camera.change_fov(self.fov_bar_x.get(),
                                                                              self.fov_bar_y.get()))
        self.fov_bar_y.configure(command=lambda event: self.camera.change_fov(self.fov_bar_x.get(),
                                                                              self.fov_bar_y.get()))
        self.look_through.configure(command=lambda: self.camera.change_thresh(self.look_through_var.get()))
        self.save_button.configure(command=lambda: self.save_model(self.save_entry.get()) or self.canvas.focus_set())

        self.key_bind()
        self.canvas.focus_set()

        self.draw_triangles(*self.camera.capture())

        while 1:
            if self.rotate:
                self.object.oriental_rotation(0.1, 0.2, 0.5)
            self.draw_triangles(*self.camera.capture())


if __name__ == '__main__':
    Main().mainloop()
