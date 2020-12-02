import numpy as np



class Space:
    def __init__(self, screen=(500, 500), unit=250):
        self.screen = screen
        self.unit = unit



class Camera:
    def __init__(self, fov=(103, 77), z_far=100, z_near=1, shutter=1, clarity=2):
        self.fov = fov
        self.fov_cos = np.cos(np.radians(max(self.fov) / 2))
        self.z_far = z_far
        self.z_near = z_near
        self.shutter = shutter
        self.clarity = clarity



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



class Light:
    def __init__(self, location, orient, alpha, lum):
        self.location = np.array([*location, 0]).reshape((4, 1))
        self.orient = np.array([*orient, 0]).reshape((4, 1))
        self.alpha = alpha
        self.lum = lum
