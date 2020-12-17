import numpy as np


class Space:
    def __init__(self, screen=(500, 500), unit=250):
        self.screen = screen
        self.unit = unit

        self.objects = []
        self.cameras = []
        self.lights = []

    def add_camera(self, camera, location=(0, 0, 0), orient=(0, 0, 1)):
        camera.place(self, location, orient)
        self.cameras.append(camera)

    def add_object(self, object, location=(0, 0, 0)):
        object.place(self, location)
        self.objects.append(object)

    def add_light(self, light, location=(0, 0, 0), orient=(0, 0, 0)):
        light.place(location, orient)
        self.lights.append(light)


class Camera:
    def __init__(self, fov=(103, 77), z_far=100, z_near=1, shutter=1, clarity=2):
        self.fov = fov
        self.fov_cos = np.cos(np.radians(max(self.fov)) / 2)
        self.fov_tan = np.tan(np.radians(self.fov) / 4)
        self.z_far = z_far
        self.z_near = z_near
        self.shutter = shutter
        self.clarity = clarity

        self.space = None
        self.location = None

        self.projection_matrix = None
        self.camera_matrix = None

        self.forward = None
        self.up = None
        self.right = None

    def place(self, space, location, orient=(0, 0, 1)):
        self.location = np.array([*location, 1]).reshape((4, 1))
        self.space = space

        # this is the forward direction, the direction the camera will look at initially
        self.forward = np.array([*orient, 0]).reshape((4, 1))
        self.forward = self.forward / np.linalg.norm(self.forward)
        # this is the up direction
        self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[1], [0], [0]], axis=0), 0).reshape((4, 1))
        # if the cross product turned out to be zero, retry with another initialization
        if self.up.all(0): self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[0], [1], [0]], axis=0),
                                               0).reshape((4, 1))
        self.up = self.up / np.linalg.norm(self.up)
        # this is the right direction
        self.right = np.append(np.cross(self.up[:3], self.forward[:3], axis=0), 0).reshape((4, 1))

        a = self.space.screen[1] / self.space.screen[0]  # aspect ratio - screen height / screen width
        z = 1 / (self.z_far - self.z_near)  # pre-calculated value of z factor
        # the projection matrix converts 3d points to 2d point(projected on to the screen)
        # as would be seen from the screen
        self.projection_matrix = np.array([[-2 / self.fov_tan[0] / a, 0, 0, 0],
                                           [0, 2 / self.fov_tan[1], 0, 0],
                                           [0, 0, -(self.z_far + self.z_near) * z, -1],
                                           [0, 0, -2 * z * self.z_far * self.z_near, 0]])
        # the matrix which changes the projection based on the current orientation of the camera
        self.camera_matrix = np.array([[1, 0, 0, 0],
                                       [0, 1, 0, 0],
                                       [0, 0, 1, 0],
                                       [0, 0, 0, 1]])

        # changes the orientation and in turn the camera matrix, given right(x), up(y), forward(z) angles to rotate
        # initially rotated by 0, 0, 0
        self.oriental_rotation(0, 0, 0)

    def capture(self):
        points_cluster = []
        faces_cluster = []
        for obj in self.space.objects:
            faces = []
            point_indexes = []
            p1i, p2i, p3i = obj.vectors[obj.faces.transpose()]
            side1i, side2i = p1i[:, :3] - [p2i[:, :3], p3i[:, :3]]
            normal_i = np.cross(side1i, side2i, axis=1)
            midi = (p1i + p2i + p3i) / 3 + obj.location
            cam_prospect_i = (midi - self.location)[:, :3]
            forward_prospect_i = np.einsum('ij,lik->lk', self.forward[:3], cam_prospect_i)
            doti = np.einsum('lij,lik->lk', normal_i, cam_prospect_i)
            z_buffer_i = np.linalg.norm(cam_prospect_i, axis=1)

            fov_val = z_buffer_i * self.fov_cos
            visible_indices = ((doti > 0) & (forward_prospect_i > fov_val) &
                               (z_buffer_i > self.z_near) & (z_buffer_i < self.z_far)).transpose()[0]
            visible_faces = obj.faces[visible_indices]
            z_buffer_i = z_buffer_i[visible_indices]
            midi = midi[visible_indices]

            light_prospect_i = self.shutter * np.array([self.light_val(light, midi)
                                                        for light in self.space.lights]).sum(axis=0)
            light_prospect_i[light_prospect_i > 1] = 1

            for fi in range(len(visible_faces)):
                face = visible_faces[fi]
                point_indexes.extend([f for f in face if f not in point_indexes])
                faces.append([[point_indexes.index(p) + len(points_cluster) for p in face],
                              light_prospect_i[fi][0], z_buffer_i[fi]])

            points = np.einsum('ij,jk,lkm->lim',
                               self.projection_matrix,
                               self.camera_matrix,
                               obj.vectors[point_indexes] + obj.location - self.location)
            points *= self.space.unit / points[:, 3, np.newaxis]
            points_cluster.extend(points)
            faces_cluster.extend(faces)

        faces_cluster = sorted(faces_cluster, key=lambda x: x[2], reverse=True)

        return points_cluster, faces_cluster

    def light_val(self, light, midi):
        d = ((midi - light.location - self.location / 5) ** (2 * self.clarity)) ** 0.5
        d = light.lum ** 0.5 / d.sum(axis=1)

        return d

    def oriental_rotation(self, r, u, f):
        angles = np.radians([r, u, f])
        c, s = np.cos(angles), np.sin(angles)
        self.forward_rotate(c[2], s[2]), self.right_rotate(c[0], s[0]), self.up_rotate(c[1], s[1])

        rotation_matrix = [self.right.transpose()[0],
                           self.up.transpose()[0],
                           self.forward.transpose()[0],
                           [0, 0, 0, 1]]

        self.camera_matrix = rotation_matrix

    def forward_rotate(self, c, s):
        self.up, self.right = self.up * c + self.right * s, self.right * c - self.up * s

    def right_rotate(self, c, s):
        self.forward, self.up = self.forward * c + self.up * s, self.up * c - self.forward * s

    def up_rotate(self, c, s):
        self.forward, self.right = self.forward * c + self.right * s, self.right * c - self.forward * s

    def oriental_translation(self, r, u, f):
        self.forward_translate(f), self.right_translate(r), self.up_translate(u)

    def forward_translate(self, m):
        self.location += m * self.forward

    def right_translate(self, m):
        self.location += m * self.right

    def up_translate(self, m):
        self.location += m * self.up


class Object:
    def __init__(self, vectors, faces):
        vectors = [[*v, 1] for v in vectors]
        self.vectors = np.array(vectors, dtype=np.float64).reshape((len(vectors), 4, 1))
        self.initial_vectors = np.array(self.vectors)

        center = np.mean(self.vectors, axis=0)
        center[3][0] = 0

        self.vectors = self.vectors - center
        self.initial_vectors = self.initial_vectors - center
        self.faces = np.array(faces)

        self.space = None
        self.location = None

        self.forward = None
        self.up = None
        self.right = None

    def place(self, space, location, orient=(0, 0, 1)):
        self.location = np.array(list(location) + [0]).reshape((4, 1))
        self.space = space

        # this is the forward direction, the direction the camera will look at initially
        self.forward = np.array([*orient, 0]).reshape((4, 1))
        self.forward = self.forward / np.linalg.norm(self.forward)
        # this is the up direction
        self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[1], [0], [0]], axis=0), 0).reshape((4, 1))
        # if the cross product turned out to be zero, retry with another initialization
        if self.up.all(0): self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[0], [1], [0]], axis=0),
                                               0).reshape((4, 1))
        self.up = self.up / np.linalg.norm(self.up)
        # this is the right direction
        self.right = np.append(np.cross(self.up[:3], self.forward[:3], axis=0), 0).reshape((4, 1))

    def oriental_rotation(self, r, u, f):
        angles = np.radians([r, u, f])
        c, s = np.cos(angles), np.sin(angles)
        self.forward_rotate(c[2], s[2]), self.right_rotate(c[0], s[0]), self.up_rotate(c[1], s[1])

        rotation_matrix = [self.right.transpose()[0],
                           self.up.transpose()[0],
                           self.forward.transpose()[0],
                           [0, 0, 0, 1]]

        self.vectors = np.einsum('ij,ljk->lik', rotation_matrix, self.initial_vectors)

    def forward_rotate(self, c, s):
        self.up, self.right = self.up * c + self.right * s, self.right * c - self.up * s

    def right_rotate(self, c, s):
        self.forward, self.up = self.forward * c + self.up * s, self.up * c - self.forward * s

    def up_rotate(self, c, s):
        self.forward, self.right = self.forward * c + self.right * s, self.right * c - self.forward * s

    def oriental_translation(self, r, u, f):
        self.forward_translate(f), self.right_translate(r), self.up_translate(u)

    def forward_translate(self, m):
        self.location += m * self.forward

    def right_translate(self, m):
        self.location += m * self.right

    def up_translate(self, m):
        self.location += m * self.up


class Light:
    def __init__(self, alpha, lum):
        self.alpha = alpha
        self.lum = lum

        self.location = None
        self.orient = None

    def place(self, location, orient):
        self.location = np.array([*location, 0]).reshape((4, 1))
        self.orient = np.array([*orient, 0]).reshape((4, 1))
