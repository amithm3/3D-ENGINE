import scr.gui as gui
import scr.renderer as rd

np = rd.np


class Spawn:
    @staticmethod
    def polygon(s, theta=0, z=0, face='both', rtype='object', append_i=0, r=1):
        points = [(0, 0, z),
                  *[(r * np.cos(np.radians(i * 360 / s + theta)), r * np.sin(np.radians(i * 360 / s + theta)), z) for i
                    in range(s + 1)]]
        if face == 'both':
            faces = [(append_i, i, i + 1) for i in range(1 + append_i, len(points) - 1 + append_i)] + \
                    [(i, i + 1, append_i) for i in range(1 + append_i, len(points) - 1 + append_i)]
        elif face == 'front':
            faces = [(append_i, i, i + 1) for i in range(1 + append_i, len(points) - 1 + append_i)]
        elif face == 'back':
            faces = [(i + 1, i, append_i) for i in range(1 + append_i, len(points) - 1 + append_i)]
        elif face == 'none':
            faces = []
        else:
            raise Exception('invalid face value')

        if rtype == 'object':
            return rd.Object(points, faces)
        else:
            return points, faces

    @staticmethod
    def parallelopiped(s, r=(1, 1), theta=0, z=None, rtype='object'):
        if z is None: z = [1 for i in r]
        points, faces = [], []
        j_append = 0
        z_append = sum(z)
        for i in range(len(r)):
            z_append -= z[i]
            if i == 0:
                pointsi, facesi = Spawn.polygon(s, theta, z_append + z[i], 'back', '', len(points), r[i])
            elif i == len(r) - 1:
                pointsi, facesi = Spawn.polygon(s, theta, z_append + z[i], 'front', '', len(points), r[i])
            else:
                pointsi, facesi = Spawn.polygon(s, theta, z_append + z[i], 'none', '', len(points), r[i])

            if i == 0:
                pass
            else:
                facesj = [(len(points) + j, j + j_append, len(points) + j + 1) for j in range(1, len(pointsi) - 1)] + \
                         [(j + j_append, j + j_append + 1, len(points) + j + 1) for j in range(1, len(pointsi) - 1)]
                faces.extend(facesj)
            j_append = len(points)
            points.extend(pointsi), faces.extend(facesi)

        if rtype == 'object':
            return rd.Object(points, faces)
        else:
            return points, faces


def main():
    def move_cam(x, y, z):
        camera.oriental_translation(x, y, z)
        app.draw_triangles(*camera.capture())

    def rotate_cam(x, y, z):
        camera.oriental_rotation(x, y, z)
        app.draw_triangles(*camera.capture())

    def key_bind():
        app.bind("<Up>", lambda event: move_cam(0, 0.1, 0))
        app.bind("<Down>", lambda event: move_cam(0, -0.1, 0))
        app.bind("<Right>", lambda event: move_cam(0.1, 0, 0))
        app.bind("<Left>", lambda event: move_cam(-0.1, 0, 0))
        app.bind("<space>", lambda event: move_cam(0, 0, 0.1))
        app.bind("<BackSpace>", lambda event: move_cam(0, 0, -0.1))
        app.bind('w', lambda event: rotate_cam(1, 0, 0))
        app.bind('s', lambda event: rotate_cam(-1, 0, 0))
        app.bind('d', lambda event: rotate_cam(0, 1, 0))
        app.bind('a', lambda event: rotate_cam(0, -1, 0))
        app.bind('z', lambda event: rotate_cam(0, 0, 1))
        app.bind('<Shift-Z>', lambda event: rotate_cam(0, 0, -1))

        app.bind("l", lambda event: [exec("light.lum += 1") for light in space.lights] and app.draw_triangles(
            *camera.capture()))
        app.bind("<Shift-L>", lambda event: [exec("light.lum -= 1") for light in space.lights] and app.draw_triangles(
            *camera.capture()))

    def init():
        s = eval(app.side.get())
        r = eval(app.radius.get())
        z = eval(app.separation.get())

        global space, object, camera, light
        space = rd.Space((app.canvas.winfo_reqwidth(), app.canvas.winfo_height()))
        object = Spawn.parallelopiped(s=s, r=r, z=z)
        fov = app.canvas.winfo_reqwidth(), app.canvas.winfo_reqheight()
        fov = 180 * fov[0] / sum(fov), 180 * fov[1] / sum(fov)
        fov = 90, 90
        camera = rd.Camera(fov=fov, shutter=5, clarity=2)
        light = rd.Light(360, 100)
        space.add_object(object, location=(0, 0, 10.))
        space.add_camera(camera, location=(0, 0, 0.), orient=(0, 0, 1.))
        space.add_light(light)

        key_bind()
        app.focus_set()

        app.draw_triangles(*camera.capture())

        # while 1:
        #     object.oriental_rotation(0.1, 0.2, 0.5)
        #     app.draw_triangles(*camera.capture())

    app = gui.GUI((750, 700), command=lambda: init())

    return app


if __name__ == '__main__':
    main().mainloop()
