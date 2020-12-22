import scr.gui as gui
import scr.renderer as rd
import scr.generator as gn


def main():
    def key_bind():
        app.bind("<Up>", lambda event: cam.oriental_translation(0, 0.1, 0))
        app.bind("<Down>", lambda event: cam.oriental_translation(0, -0.1, 0))
        app.bind("<Right>", lambda event: cam.oriental_translation(0.1, 0, 0))
        app.bind("<Left>", lambda event: cam.oriental_translation(-0.1, 0, 0))
        app.bind("<space>", lambda event: cam.oriental_translation(0, 0, 0.1))
        app.bind("<BackSpace>", lambda event: cam.oriental_translation(0, 0, -0.1))
        app.bind('w', lambda event: cam.oriental_rotation(1, 0, 0))
        app.bind('s', lambda event: cam.oriental_rotation(-1, 0, 0))
        app.bind('d', lambda event: cam.oriental_rotation(0, 1, 0))
        app.bind('a', lambda event: cam.oriental_rotation(0, -1, 0))
        app.bind('z', lambda event: cam.oriental_rotation(0, 0, 1))
        app.bind('<Shift-Z>', lambda event: cam.oriental_rotation(0, 0, -1))

        app.bind("l", lambda event: [exec("light.lum += 1") for light in space.lights])
        app.bind("<Shift-L>", lambda event: [exec("light.lum -= 1") for light in space.lights])
        app.bind("c", lambda event: exec("cam.clarity += 0.1"))
        app.bind("<Shift-C>", lambda event: exec("cam.clarity -= 0.1"))
        app.bind("t", lambda event: exec("cam.shutter += 0.1"))
        app.bind("<Shift-T>", lambda event: exec("cam.shutter -= 0.1"))

    def init():
        global space, obj, cam, light

        s = eval(app.side.get())
        r = eval(app.radius.get())
        z = eval(app.separation.get())

        space = rd.Space((app.canvas.winfo_reqwidth(), app.canvas.winfo_height()))
        obj = gn.Spawn.parallelopiped(s=s, r=r, z=z)
        fov = app.canvas.winfo_width(), app.canvas.winfo_height()
        fov = 120 * fov[0] / sum(fov), 180 * fov[1] / sum(fov)
        cam = rd.Camera(fov=fov, shutter=1, clarity=1)
        light = rd.Light(360, 33)
        space.add_object(obj, location=(0, 0, 10.))
        space.add_camera(cam, location=(0, 0, 0.), orient=(0, 0, 1.))
        space.add_light(light)

        app.fov_bar_x.set(cam.fov[0])
        app.fov_bar_y.set(cam.fov[1])
        app.fov_bar_x.configure(command=lambda event: cam.change_fov(app.fov_bar_x.get(), app.fov_bar_y.get()))
        app.fov_bar_y.configure(command=lambda event: cam.change_fov(app.fov_bar_x.get(), app.fov_bar_y.get()))

        key_bind()
        app.focus_set()

        app.draw_triangles(*cam.capture())

        while 1:
            # obj.oriental_rotation(0.1, 0.2, 0.5)
            app.draw_triangles(*cam.capture())

    app = gui.GUI((750, 700), model_it_command=lambda: init())

    return app


if __name__ == '__main__':
    main().mainloop()
