import os
import pickle
import sys
from tkinter import filedialog

import demo_gui as gui
import generator as gn

rd = gn.rd


class Main(gui.GUI):
    def __init__(self):
        gui.GUI.__init__(self, title="ENGINE", icon=r'__data__\assets\icon.ico')

        self.files = [('3D-OBJECT File', '*.3dobj')]

        self.model_button.configure(command=lambda: self.model_it())
        self.save_button.configure(command=lambda: (self.save_model(
            filedialog.asksaveasfilename(filetypes=self.files, defaultextension=self.files,
                                         initialfile='new_3d_object_file')),
                                                    self.canvas.focus_set()))
        self.load_button.configure(command=lambda: (self.load_model(
            filedialog.askopenfilename(filetypes=self.files, defaultextension=self.files,
                                       initialdir=os.getcwd() + '/__data__/Examples')),
                                                    self.canvas.focus_set()))
        self.rotate_var.trace('w', lambda *_: self.after(0, self.loop) if not self.turb_var.get() else None)
        self.turb_var.trace('w', lambda *_: self.after(0, self.loop) if not self.rotate_var.get() else None)
        self.look_through_var.trace('w', lambda *_: (self.camera.thresh_set(self.look_through_var.get()),
                                                     self.smart_loop()))
        self.see_orient_var.trace('w', lambda *_: self.smart_loop())

        self.canvas.bind('<Button-1>', lambda event: self.canvas.focus_force())

        self.space = None
        self.object = None
        self.camera = None
        self.light = None

        self.loaded = False
        self.srz_info = None

        if associate_file:
            self.load_model(associate_file)

    def save_model(self, fpath):
        if fpath:
            with open(fpath, 'wb') as save_file:
                pickle.dump(self.srz_info, save_file)
            self.load_button.configure(text=os.path.basename(fpath))
            self.load_model(fpath)

    def load_model(self, fpath):
        if fpath:
            global associate_file
            if not associate_file:
                with open(fpath, 'rb') as save_file:
                    data = list(pickle.load(save_file))
            else:
                with open(fpath, 'rb') as save_file:
                    data = list(pickle.load(save_file))
                associate_file = ''

            self.side.delete(0, 'end'), self.radius.delete(0, 'end'), self.separation.delete(0, 'end')
            self.side.insert(0, data[0])
            data[1], data[2] = str(data[1]).replace('(', '').replace(')', ''), str(data[2]).replace('(', '').replace(
                ')',
                '')
            self.radius.insert(0, data[1])
            self.separation.insert(0, data[2])
            self.load_button.configure(text=os.path.basename(fpath))

            self.loaded = True
            self.model_it()

    def exec(self, expr, node=None):
        if node is None:
            node = {}
        local = {'self': self}
        local.update(node)
        exec(expr, local)
        self.smart_loop()

    def translate(self, *args):
        self.camera.oriental_translation(*args)
        self.smart_loop()

    def rotate(self, *args):
        self.camera.oriental_rotation(*args)
        self.smart_loop()

    def key_bind(self):
        self.canvas.bind("<Up>", lambda event: self.translate(0, 0.2, 0))
        self.canvas.bind("<Down>", lambda event: self.translate(0, -0.2, 0))
        self.canvas.bind("<Right>", lambda event: self.translate(0.2, 0, 0))
        self.canvas.bind("<Left>", lambda event: self.translate(-0.2, 0, 0))
        self.canvas.bind("<space>", lambda event: self.translate(0, 0, 0.2))
        self.canvas.bind("<BackSpace>", lambda event: self.translate(0, 0, -0.2))

        self.canvas.bind('w', lambda event: self.rotate(1, 0, 0))
        self.canvas.bind('s', lambda event: self.rotate(-1, 0, 0))
        self.canvas.bind('d', lambda event: self.rotate(0, 1, 0))
        self.canvas.bind('a', lambda event: self.rotate(0, -1, 0))
        self.canvas.bind('z', lambda event: self.rotate(0, 0, 1))
        self.canvas.bind('<Shift-Z>', lambda event: self.rotate(0, 0, -1))

        self.canvas.bind("l", lambda event: [self.exec("light.lum += 1", {'light': light})
                                             for light in self.space.lights])
        self.canvas.bind("<Shift-L>", lambda event: [self.exec("light.lum -= 1", {'light': light})
                                                     for light in self.space.lights])
        self.canvas.bind("c", lambda event: self.exec("self.camera.clarity += 0.01"))
        self.canvas.bind("<Shift-C>", lambda event: self.exec("self.camera.clarity -= 0.01"))
        self.canvas.bind("t", lambda event: self.exec("self.camera.shutter += 0.01"))
        self.canvas.bind("<Shift-T>", lambda event: self.exec("self.camera.shutter -= 0.01"))

        self.canvas.bind("h", lambda event: self.exec("self.hl.reverse()"))

    def model_it(self):
        self._set_offset()
        self.space = rd.Space((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.srz_info = eval(self.side.get()), eval(self.radius.get()), eval(self.separation.get())
        if not self.loaded:
            self.load_button.configure(text='Load')
        else:
            self.loaded = False
        self.object = gn.Spawn.parallelopiped(*self.srz_info)
        self.camera = rd.Camera(shutter=2, clarity=4)
        obj_center = self.object.vectors.mean(axis=0)
        self.space.add_object(self.object, location=(0, 0, 0))
        cam_d = rd.np.max(rd.np.sum(rd.np.square(self.object.vectors), axis=1)) ** 0.5
        location = (obj_center[:3]).transpose()[0] + [0, -4 * cam_d, 0]
        self.light = rd.Light(1, 2 * rd.np.linalg.norm(location))
        self.space.add_camera(self.camera, location=location, orient=(0, 1, 0.))
        self.space.add_light(self.light, location=location)

        self.fov_bar_x.set(self.camera.fov[0])
        self.fov_bar_y.set(self.camera.fov[1])
        self.fov_bar_x.configure(command=lambda event: (self.camera.fov_config((self.fov_bar_x.get(),
                                                                                self.fov_bar_y.get())),
                                                        self.smart_loop()))
        self.fov_bar_y.configure(command=lambda event: (self.camera.fov_config((self.fov_bar_x.get(),
                                                                                self.fov_bar_y.get())),
                                                        self.smart_loop()))
        self.bind("<Configure>", lambda *_: self.after(0, self.resize_bind)
        if self.space.screen != (self.canvas.winfo_width(), self.canvas.winfo_height())
        else None)
        self.key_bind()
        self.canvas.focus_set()

        self.smart_loop()

    def resize_bind(self):
        self.rotate_var.set(0)
        self.turb_var.set(0)
        self.space.screen = (self.canvas.winfo_width(), self.canvas.winfo_height())
        self._set_offset(), self.camera.fov_config()
        self.fov_bar_x.set(self.camera.fov[0])
        self.fov_bar_y.set(self.camera.fov[1])

    def smart_loop(self):
        if not self.rotate_var.get() and not self.turb_var.get():
            self.after(0, self.loop())

    def loop(self):
        if self.space is not None:
            self.draw_triangles(*self.camera.capture(self.see_orient_var.get()))
            if self.rotate_var.get() or self.turb_var.get():
                if self.turb_var.get():
                    self.object.oriental_rotation(*(rd.np.random.uniform(-1, 1, 3)))
                    self.object.oriental_translation(*(rd.np.random.uniform(-.1, .1, 3)))
                if self.rotate_var.get():
                    self.object.oriental_rotation(*(rd.np.random.uniform(0, 1, 3)))
                self.after(0, self.loop)


if __name__ == '__main__':
    global associate_file
    cmd_handle = sys.argv
    if len(cmd_handle) > 1:
        associate_file = cmd_handle[1]
        os.chdir(os.path.dirname(cmd_handle[0]))
    else:
        associate_file = ''
    os.chdir(os.path.dirname(os.getcwd()))
    Main().mainloop()
