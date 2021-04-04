import numpy as np


class Space:
    def __init__(self, screen, unit=250):
        self.screen = screen  # screen width, height
        self.unit = unit

        self.objects = []
        self.cameras = []
        self.lights = []

    def add_camera(self, camera, location=(0, 0, 0), orient=(0, 0, 1)):
        camera.place(self, location, orient)
        self.cameras.append(camera)

    def add_object(self, Object, location=(0, 0, 0)):
        Object.place(self, location)
        self.objects.append(Object)

    def add_light(self, light, location=(0, 0, 0), orient=(0, 0, 0)):
        light.place(location, orient)
        self.lights.append(light)


class Camera:
    def __init__(self, fov=None, z_far=1000, z_near=1, shutter=1, clarity=1):
        self.fov = fov
        self.fov_cos = None
        self.fov_tan = None
        self.z_far = z_far
        self.z_near = z_near
        self.shutter = shutter
        self.clarity = clarity
        self.thresh = 'doti > 0'  # will be evaluated(eval) for see through or normal view effect

        # class variables initialization
        self.space = None
        self.location = None
        self.cost = 0

        self.projection_matrix = None
        self.camera_matrix = None

        self.forward = None
        self.up = None
        self.right = None

    # will be evaluated(eval) for see through or normal view effect
    def thresh_set(self, val):
        if val == 0:
            self.thresh = 'doti > 0'
        else:
            self.thresh = 'doti <= 0'

    def fov_config(self, new_fov=None):
        if new_fov is None:
            self.fov = np.degrees(2 * np.arctan(np.array(self.space.screen) / 2 / self.z_near / self.space.unit))
        else:
            self.fov = np.array(new_fov)
        self.fov_cos = np.cos(np.radians(self.fov + 25) / 4)
        self.fov_tan = np.tan(np.radians(self.fov) / 4)

        a = self.space.screen[1] / self.space.screen[0]  # aspect ratio - screen height / screen width
        z = 1 / (self.z_far - self.z_near)  # pre-calculated value of z factor
        # the projection matrix converts 3d points to 2d point(projected on to the screen)
        # as would be seen from the screen
        self.projection_matrix = np.array([[-2 / self.fov_tan[0] / a, 0, 0, 0],
                                           [0, 2 / self.fov_tan[1], 0, 0],
                                           [0, 0, -(self.z_far + self.z_near) * z, -1],
                                           [0, 0, -2 * z * self.z_far * self.z_near, 0]])
        # the matrix which changes the projection based on the current orientation of the camera
        self.camera_matrix = [[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]]

        # changes the orientation and in turn the camera matrix, given right(x), up(y), forward(z) angles to rotate
        # initially rotated by 0, 0, 0
        self.oriental_rotation(0, 0, 0)

    def place(self, space, location, orient=(0, 0, 1)):
        self.location = np.array([*location, 1]).reshape((4, 1))
        self.space = space

        # this is the forward direction, the direction the camera will look at initially
        self.forward = np.array([*orient, 0]).reshape((4, 1))
        self.forward = self.forward / np.linalg.norm(self.forward)
        # this is the up direction
        self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[1], [0], [0]], axis=0), 0).reshape((4, 1))
        # if the cross product turned out to be zero, retry with another initialization
        if self.up.all(0):
            self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[0], [1], [0]], axis=0),
                                0).reshape((4, 1))
        self.up = self.up / np.linalg.norm(self.up)
        # this is the right direction
        self.right = np.append(np.cross(self.up[:3], self.forward[:3], axis=0), 0).reshape((4, 1))

        self.fov_config(self.fov)

    def capture(self, capture_orient=False):
        points_cluster = []
        faces_cluster = []
        orient_cluster = []
        for obj in self.space.objects:
            faces = []
            point_indexes = []
            p1i, p2i, p3i = obj.vectors[obj.faces.transpose()]
            side1i, side2i = p1i[:, :3] - [p2i[:, :3], p3i[:, :3]]
            normal_i = np.cross(side1i, side2i, axis=1)  # normal of triangular side
            midi = (p1i + p2i + p3i) / 3 + obj.location  # mid-point of triangular side

            # calculates orientation of object if asked
            if capture_orient:
                orient = np.einsum('ij,jk,lkm->lim',
                                   self.projection_matrix,
                                   self.camera_matrix,
                                   np.array([*(obj.rotation_matrix @ obj.initial_orient), obj.vectors.mean(axis=0)]) +
                                   obj.location - self.location)
                orient *= self.space.unit / orient[:, 3, np.newaxis]
                orient_cluster.append(orient)

            #  required calculation to determine the visibility of faces for drawing
            cam_prospect_i = (midi - self.location)[:, :3]  # object-cam vector
            forward_prospect_i = np.einsum('ij,lik->lk', self.forward[:3], cam_prospect_i)  # object-cam projection
            doti = np.einsum('lij,lik->lk', normal_i, cam_prospect_i)  # object-normal projection onto object-cam vector
            z_buffer_i = np.linalg.norm(cam_prospect_i, axis=1)  # z distance of object wrt camera orientation
            fov_val = z_buffer_i * self.fov_cos
            #  check various conditions for visibility and extract required faces for further calculation
            visible_indices = ((eval(self.thresh, {'doti': doti})) & ((forward_prospect_i > fov_val[:, [0]]) |
                                                                      (forward_prospect_i > fov_val[:, [1]])) &
                               (z_buffer_i > self.z_near) & (z_buffer_i < self.z_far)).transpose()[0]
            visible_faces = obj.faces[visible_indices]
            self.cost = visible_faces.shape[0]
            z_buffer_i = z_buffer_i[visible_indices]
            midi = midi[visible_indices]

            light_prospect_i = self.shutter * np.array([light.luminate(midi)
                                                        for light in self.space.lights]).sum(axis=0)
            light_prospect_i = light_prospect_i ** self.clarity / self.clarity
            light_prospect_i[light_prospect_i > 1] = 1
            light_prospect_i[light_prospect_i < 0] = 0

            #  extract faces to be drawn and provide lighting info with z_buffer
            for fi in range(len(visible_faces)):
                face = visible_faces[fi]
                point_indexes.extend([f for f in face if f not in point_indexes])
                faces.append([[point_indexes.index(p) + len(points_cluster) for p in face],
                              light_prospect_i[fi][0], z_buffer_i[fi]])

            #  final calculation for 2d projection onto screen
            points = np.einsum('ij,jk,lkm->lim',
                               self.projection_matrix,
                               self.camera_matrix,
                               obj.vectors[point_indexes] + obj.location - self.location)
            points *= self.space.unit / points[:, 3, np.newaxis]

            points_cluster.extend(points)
            faces_cluster.extend(faces)

        faces_cluster = sorted(faces_cluster, key=lambda x: x[2], reverse=True)

        return points_cluster, faces_cluster, orient_cluster

    def oriental_rotation(self, r, u, f):
        angles = np.radians([r, u, f])
        c, s = np.cos(angles), np.sin(angles)
        self.forward_rotate(c[2], s[2]), self.right_rotate(c[0], s[0]), self.up_rotate(c[1], s[1])

        self.camera_matrix = [self.right.transpose()[0],
                              self.up.transpose()[0],
                              self.forward.transpose()[0],
                              [0, 0, 0, 1]]

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
        self.initial_orient = None
        self.rotation_matrix = None

    def place(self, space, location, orient=(0, 0, 1)):
        self.location = np.array(list(location) + [0], dtype=np.float64).reshape((4, 1))
        self.space = space

        # this is the forward direction, the direction the camera will look at initially
        self.forward = np.array([*orient, 0]).reshape((4, 1))
        self.forward = self.forward / np.linalg.norm(self.forward)
        # this is the up direction
        self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[1], [0], [0]], axis=0), 0).reshape((4, 1))
        # if the cross product turned out to be zero, retry with another initialization
        if self.up.all(0):
            self.up = np.append(np.cross(self.forward[:3], self.forward[:3] + [[0], [1], [0]], axis=0),
                                0).reshape((4, 1))
        self.up = self.up / np.linalg.norm(self.up)
        # this is the right direction
        self.right = np.append(np.cross(self.up[:3], self.forward[:3], axis=0), 0).reshape((4, 1))
        self.initial_orient = np.array([self.forward, self.up, self.right]) + [[0], [0], [0], [1]]
        self.rotation_matrix = [[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]]

    def oriental_rotation(self, r, u, f):
        angles = np.radians([r, u, f])
        c, s = np.cos(angles), np.sin(angles)
        self.forward_rotate(c[2], s[2]), self.right_rotate(c[0], s[0]), self.up_rotate(c[1], s[1])

        self.rotation_matrix = [self.right.transpose()[0],
                                self.up.transpose()[0],
                                self.forward.transpose()[0],
                                [0, 0, 0, 1]]

        self.vectors = np.einsum('ij,ljk->lik', self.rotation_matrix, self.initial_vectors)

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

    def luminate(self, midi):
        d = (midi - self.location) ** 2
        d = 1 - d.sum(axis=1) ** 0.5 / self.lum * self.alpha

        return d
