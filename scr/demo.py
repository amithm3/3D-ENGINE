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
                                         initialdir=os.getcwd() + '/__data__/Saves',
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

        self.keys = {'Up': 0,
                     'Down': 0,
                     'Right': 0,
                     'Left': 0,
                     'b': 0,
                     'space': 0,
                     'w': 0,
                     's': 0,
                     'd': 0,
                     'a': 0,
                     'z': 0,
                     'x': 0}

        self.bind_key = {'Up': rd.np.array([0, 0.25, 0]),
                         'Down': rd.np.array([0, -0.25, 0]),
                         'Right': rd.np.array([0.25, 0, 0]),
                         'Left': rd.np.array([-0.25, 0, 0]),
                         'b': rd.np.array([0, 0, 0.25]),
                         'space': rd.np.array([0, 0, -0.25]),

                         'w': rd.np.array([0.5, 0, 0]),
                         's': rd.np.array([-0.5, 0, 0]),
                         'd': rd.np.array([0, 0.5, 0]),
                         'a': rd.np.array([0, -0.5, 0]),
                         'z': rd.np.array([0, 0, 0.5]),
                         'x': rd.np.array([0, 0, -0.5])}

        self.event_started = False

        self.space = None
        self.object = None
        self.camera = None
        self.light = None

        self.loaded = False
        self.srzc_info = None

        if associate_file:
            self.load_model(associate_file)

    def save_model(self, fpath):
        if fpath:
            with open(fpath, 'wb') as save_file:
                pickle.dump(self.srzc_info, save_file)
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

            self.side.delete(0, 'end'), self.radius.delete(0, 'end'), \
            self.separation.delete(0, 'end'), self.color.delete(0, 'end')
            self.side.insert(0, data[0])
            data[1], data[2] = str(data[1]).replace('(', '').replace(')', ''), \
                               str(data[2]).replace('(', '').replace(')', '')
            self.radius.insert(0, data[1])
            self.separation.insert(0, data[2])
            self.color.insert(0, data[3])
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

    def translate(self, args):
        if self.fps > 60:
            self.after(int(self.fps / 60))
        self.camera.oriental_translation(*args)

    def rotate(self, args):
        self.camera.oriental_rotation(*args)

    def event(self):
        if 1 in self.keys.values():
            self.event_started = True
            if self.keys['Up'] == 1 or self.keys['Down'] == 1 or self.keys['Left'] == 1 or self.keys['Right'] == 1 \
                    or self.keys['b'] == 1 or self.keys['space'] == 1:
                self.translate(self.keys['Up'] * self.bind_key['Up'] + self.keys['Down'] * self.bind_key['Down'] +
                               self.keys['Left'] * self.bind_key['Left'] + self.keys['Right'] * self.bind_key['Right'] +
                               self.keys['b'] * self.bind_key['b'] + self.keys['space'] * self.bind_key['space'])
            if self.keys['w'] == 1 or self.keys['s'] == 1 or self.keys['a'] == 1 or self.keys['d'] == 1 \
                    or self.keys['z'] == 1 or self.keys['x'] == 1:
                self.rotate(self.keys['w'] * self.bind_key['w'] + self.keys['s'] * self.bind_key['s'] +
                            self.keys['d'] * self.bind_key['d'] + self.keys['a'] * self.bind_key['a'] +
                            self.keys['z'] * self.bind_key['z'] + self.keys['x'] * self.bind_key['x'])
            self.smart_loop()
            self.after(self.rotate_var.get() + self.turb_var.get(), self.event)
        else:
            self.event_started = False

    def key_pressed(self, event):
        if event.keysym in self.keys.keys() and not self.keys[event.keysym]:
            self.keys[event.keysym] = 1
        if not self.event_started:
            self.after(0, self.event)

    def key_released(self, event):
        if event.keysym in self.keys.keys() and self.keys[event.keysym]:
            self.keys[event.keysym] = 0

    def key_bind(self):
        self.canvas.bind("l", lambda event: [self.exec("light.lum += 1", {'light': light})
                                             for light in self.space.lights])
        self.canvas.bind("<Shift-L>", lambda event: [self.exec("light.lum -= 1", {'light': light})
                                                     for light in self.space.lights])
        self.canvas.bind("c", lambda event: self.exec("self.camera.clarity += 0.1"))
        self.canvas.bind("<Shift-C>", lambda event: self.exec("self.camera.clarity -= 0.1"))
        self.canvas.bind("t", lambda event: self.exec("self.camera.shutter += 0.1"))
        self.canvas.bind("<Shift-T>", lambda event: self.exec("self.camera.shutter -= 0.1"))

        self.canvas.bind("h", lambda event: self.exec("self.hl.reverse()"))

    def model_it(self):
        self._set_offset()
        self.space = rd.Space((self.canvas.winfo_width(), self.canvas.winfo_height()))
        if int(self.side.get()) > 36:
            self.side.delete(0, 'end')
            self.side.insert(0, '36')
        self.srzc_info = eval(self.side.get()), eval(self.radius.get()), \
                         eval(self.separation.get()), self.color.get()
        if not self.loaded:
            self.load_button.configure(text='Load')
        else:
            self.loaded = False
        self.object = gn.Spawn.parallelopiped(*self.srzc_info[:3])
        self.camera = rd.Camera(shutter=2, clarity=6)
        obj_center = self.object.vectors.mean(axis=0).transpose()[0][:3]
        self.space.add_object(self.object, location=(0, 0, 0))
        cam_d = rd.np.max(rd.np.sum(rd.np.square(self.object.vectors), axis=1)) ** 0.5
        location = obj_center + [0, -4 * cam_d, -5 / 2 * cam_d]
        self.light = rd.Light(1, 2.5 * rd.np.linalg.norm(location))
        self.space.add_camera(self.camera, location=location, orient=-location / rd.np.linalg.norm(location))
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
        self.canvas.bind("<KeyPress>", lambda event: self.key_pressed(event))
        self.canvas.bind("<KeyRelease>", lambda event: self.key_released(event))
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
