import renderer as rd

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
    def parallelopiped(s, r=(1, 1), z=None, theta=0, rtype='object'):
        if not hasattr(r, '__iter__'): r = (r, r)
        if not hasattr(z, '__iter__'):
            z = (z, 0)
        else:
            z = (*z, 0)
        if z is None:
            z = [1 for _ in r]
        points, faces = [], []
        j_append = 0
        z_append = sum(z)
        for i in range(len(r)):
            if i == 0:
                pointsi, facesi = Spawn.polygon(s, theta, z_append, 'back', '', len(points), r[i])
            elif i == len(r) - 1:
                pointsi, facesi = Spawn.polygon(s, theta, z_append, 'front', '', len(points), r[i])
            else:
                pointsi, facesi = Spawn.polygon(s, theta, z_append, 'none', '', len(points), r[i])
            z_append -= z[i]

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
