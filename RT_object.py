# object class
import RT_utility as rtu
import RT_material as rtm
import math
import numpy as np
import struct

class Object:
    def __init__(self) -> None:
        pass

    def intersect(self, rRay, cInterval):
        pass

class Sphere(Object):
    def __init__(self, vCenter, fRadius, mMat=None) -> None:
        super().__init__()
        self.center = vCenter
        self.radius = fRadius
        self.material = mMat
        # additional parameters for motion blur
        self.moving_center = None       # where to the sphere moves to
        self.is_moving = False          # is it moving ?
        self.moving_dir = None          # moving direction

    def add_material(self, mMat):
        self.material = mMat

    def add_moving(self, vCenter):      # set an ability to move to the sphere
        self.moving_center = vCenter
        self.is_moving = True
        self.moving_dir = self.moving_center - self.center

    def move_sphere(self, fTime):       # move the sphere by time parameter
        return self.center + self.moving_dir*fTime

    def printInfo(self):
        self.center.printout()        
    
    def intersect(self, rRay, cInterval):        

        # check if the sphere is moving then move center of the sphere.
        sphere_center = self.center
        if self.is_moving:
            sphere_center = self.move_sphere(rRay.getTime())

        oc = rRay.getOrigin() - sphere_center
        a = rRay.getDirection().len_squared()
        half_b = rtu.Vec3.dot_product(oc, rRay.getDirection())
        c = oc.len_squared() - self.radius*self.radius
        discriminant = half_b*half_b - a*c 

        if discriminant < 0:
            return None
        sqrt_disc = math.sqrt(discriminant)

        root = (-half_b - sqrt_disc) / a 
        if not cInterval.surrounds(root):
            root = (-half_b + sqrt_disc) / a 
            if not cInterval.surrounds(root):
                return None
            
        hit_t = root
        hit_point = rRay.at(root)
        hit_normal = (hit_point - sphere_center) / self.radius
        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        fuv = self.get_uv(hit_normal)
        hinfo.set_uv(fuv[0], fuv[1])

        return hinfo

    # return uv coordinates of the sphere at the hit point.
    def get_uv(self, vNormal):
        theta = math.acos(-vNormal.y())
        phi = math.atan2(-vNormal.z(), vNormal.x()) + math.pi

        u = phi / (2*math.pi)
        v = theta / math.pi
        return (u,v)

# Ax + By + Cz = D
class Quad(Object):
    def __init__(self, vQ, vU, vV, mMat=None) -> None:
        super().__init__()
        self.Qpoint = vQ
        self.Uvec = vU
        self.Vvec = vV
        self.material = mMat
        self.uxv = rtu.Vec3.cross_product(self.Uvec, self.Vvec)
        self.normal = rtu.Vec3.unit_vector(self.uxv)
        self.D = rtu.Vec3.dot_product(self.normal, self.Qpoint)
        self.Wvec = self.uxv / rtu.Vec3.dot_product(self.uxv, self.uxv)

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        denom = rtu.Vec3.dot_product(self.normal, rRay.getDirection())
        # if parallel
        if rtu.Interval.near_zero(denom):
            return None

        # if it is hit.
        t = (self.D - rtu.Vec3.dot_product(self.normal, rRay.getOrigin())) / denom
        if not cInterval.contains(t):
            return None
        
        hit_t = t
        hit_point = rRay.at(t)
        hit_normal = self.normal

        # determine if the intersection point lies on the quad's plane.
        planar_hit = hit_point - self.Qpoint
        alpha = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(planar_hit, self.Vvec))
        beta = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(self.Uvec, planar_hit))
        if self.is_interior(alpha, beta) is None:
            return None

        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        hinfo.set_uv(alpha, beta)

        return hinfo
    
    def is_interior(self, fa, fb):
        delta = 0   
        if (fa<delta) or (1.0<fa) or (fb<delta) or (1.0<fb):
            return None

        return True


class Triangle(Object):
    def __init__(self, vA, vB, vC, mMat=None) -> None:
        """
        Initialize triangle with three vertices and optional material
        vA, vB, vC: Vec3 vertices of the triangle
        mMat: material of the triangle
        """
        super().__init__()
        self.vertA = vA
        self.vertB = vB
        self.vertC = vC
        self.material = mMat
        
        self.edge1 = self.vertB - self.vertA
        self.edge2 = self.vertC - self.vertA
        self.normal = rtu.Vec3.unit_vector(rtu.Vec3.cross_product(self.edge1, self.edge2))

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        """
        Implement Möller-Trumbore algorithm for ray-triangle intersection
        Returns Hitinfo object if intersection occurs, None otherwise
        """
        # Begin Möller-Trumbore algorithm
        h = rtu.Vec3.cross_product(rRay.getDirection(), self.edge2)
        a = rtu.Vec3.dot_product(self.edge1, h)

        # If ray is parallel to triangle
        if rtu.Interval.near_zero(a):
            return None

        f = 1.0 / a
        s = rRay.getOrigin() - self.vertA
        u = f * rtu.Vec3.dot_product(s, h)

        # Test if intersection is outside first edge
        if u < 0.0 or u > 1.0:
            return None

        q = rtu.Vec3.cross_product(s, self.edge1)
        v = f * rtu.Vec3.dot_product(rRay.getDirection(), q)

        # Test if intersection is outside second edge
        if v < 0.0 or u + v > 1.0:
            return None

        # Compute t to find point of intersection
        t = f * rtu.Vec3.dot_product(self.edge2, q)

        # Check if intersection is within the interval
        if not cInterval.surrounds(t):
            return None

        # Compute intersection point and create hit info
        hit_point = rRay.at(t)
        hit_normal = self.normal
        hinfo = rtu.Hitinfo(hit_point, hit_normal, t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # Set UV coordinates for texture mapping
        # UV coordinates are barycentric coordinates (u,v)
        hinfo.set_uv(u, v)

        return hinfo

    def get_normal(self):
        return self.normal

class Box(Object):
    def __init__(self, vMin, vMax, mMat=None) -> None:
        """
        Initialize box with minimum and maximum points
        vMin: Vec3 minimum point (smallest x,y,z coordinates)
        vMax: Vec3 maximum point (largest x,y,z coordinates)
        mMat: material of the box
        """
        super().__init__()
        self.min_point = vMin
        self.max_point = vMax
        self.material = mMat
        
        # Create the six faces of the box using quads
        self.sides = []
        
        # Front and back
        self.sides.append(Quad(
            vMin,
            rtu.Vec3(self.max_point.x() - self.min_point.x(), 0, 0),
            rtu.Vec3(0, self.max_point.y() - self.min_point.y(), 0),
            mMat
        ))
        self.sides.append(Quad(
            rtu.Vec3(self.min_point.x(), self.min_point.y(), self.max_point.z()),
            rtu.Vec3(self.max_point.x() - self.min_point.x(), 0, 0),
            rtu.Vec3(0, self.max_point.y() - self.min_point.y(), 0),
            mMat
        ))
        
        # Left and right
        self.sides.append(Quad(
            vMin,
            rtu.Vec3(0, 0, self.max_point.z() - self.min_point.z()),
            rtu.Vec3(0, self.max_point.y() - self.min_point.y(), 0),
            mMat
        ))
        self.sides.append(Quad(
            rtu.Vec3(self.max_point.x(), self.min_point.y(), self.min_point.z()),
            rtu.Vec3(0, 0, self.max_point.z() - self.min_point.z()),
            rtu.Vec3(0, self.max_point.y() - self.min_point.y(), 0),
            mMat
        ))
        
        # Top and bottom
        self.sides.append(Quad(
            vMin,
            rtu.Vec3(self.max_point.x() - self.min_point.x(), 0, 0),
            rtu.Vec3(0, 0, self.max_point.z() - self.min_point.z()),
            mMat
        ))
        self.sides.append(Quad(
            rtu.Vec3(self.min_point.x(), self.max_point.y(), self.min_point.z()),
            rtu.Vec3(self.max_point.x() - self.min_point.x(), 0, 0),
            rtu.Vec3(0, 0, self.max_point.z() - self.min_point.z()),
            mMat
        ))

    def add_material(self, mMat):
        self.material = mMat
        for side in self.sides:
            side.add_material(mMat)

    def intersect(self, rRay, cInterval):
        """
        Test intersection with all six faces of the box
        Returns closest hit point
        """
        current_interval = rtu.Interval(cInterval.min_val, cInterval.max_val)
        closest_hit = None
        
        for side in self.sides:
            hit_info = side.intersect(rRay, current_interval)
            if hit_info is not None:
                current_interval.max_val = hit_info.getT()
                closest_hit = hit_info
        
        return closest_hit

class ConstantMedium(Object):
    def __init__(self, boundary, fDensity, cAlbedo) -> None:
        """
        Initialize constant medium within a boundary shape
        boundary: Any object class that defines the volume boundary
        fDensity: Density of the medium
        cAlbedo: Color of the medium
        """
        super().__init__()
        self.boundary = boundary
        self.neg_inv_density = -1.0 / fDensity
        # Create IsotropicVolume material
        self.material = rtm.IsotropicVolume(cAlbedo, fDensity)

    def add_material(self, mMat):
        # Override to prevent changing the isotropic material
        pass

    def intersect(self, rRay, cInterval):
        """
        Test if ray intersects the volume and handle scattering
        """
        # First hit point
        hit1 = self.boundary.intersect(rRay, rtu.Interval(cInterval.min_val, rtu.infinity_number))
        if hit1 is None:
            return None

        # Second hit point
        hit2 = self.boundary.intersect(rRay, rtu.Interval(hit1.getT() + 0.0001, rtu.infinity_number))
        if hit2 is None:
            return None

        # Clamp ray distances to valid interval
        t1 = max(hit1.getT(), cInterval.min_val)
        t2 = min(hit2.getT(), cInterval.max_val)

        if t1 >= t2:
            return None

        # Ensure t1 is not behind the ray
        t1 = max(t1, 0)

        # Calculate distance through volume
        ray_length = rRay.getDirection().len()
        distance_inside_boundary = (t2 - t1) * ray_length

        # Sample random scattering distance
        hit_distance = self.material.sample_distance()

        # Check if scattering occurs within the volume
        if hit_distance > distance_inside_boundary:
            return None

        # Calculate hit point and create hit info
        hit_t = t1 + hit_distance / ray_length
        hit_p = rRay.at(hit_t)
        
        # For volumes, normal direction doesn't matter
        # We set it to an arbitrary direction since it's not used in scattering
        hit_normal = rtu.Vec3(1, 0, 0)

        return rtu.Hitinfo(hit_p, hit_normal, hit_t, self.material)

class TiltedBox(Object):
    def __init__(self, center, x_dir, y_dir, z_dir, x_length, y_length, z_length, mMat=None) -> None:
        super().__init__()
        self.center = center
        self.x_dir = rtu.Vec3.unit_vector(x_dir) * x_length
        self.y_dir = rtu.Vec3.unit_vector(y_dir) * y_length
        self.z_dir = rtu.Vec3.unit_vector(z_dir) * z_length
        self.material = mMat
        
        # Calculate the corners of the tilted box
        self.vertices = [
            self.center + (self.x_dir * sign_x) + (self.y_dir * sign_y) + (self.z_dir * sign_z)
            for sign_x in (-1, 1) for sign_y in (-1, 1) for sign_z in (-1, 1)
        ]

        # Define each face of the box as a quad
        self.sides = [
            Quad(self.vertices[0], self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[0], mMat),
            Quad(self.vertices[4], self.vertices[5] - self.vertices[4], self.vertices[6] - self.vertices[4], mMat),
            Quad(self.vertices[0], self.vertices[4] - self.vertices[0], self.vertices[2] - self.vertices[0], mMat),
            Quad(self.vertices[1], self.vertices[5] - self.vertices[1], self.vertices[3] - self.vertices[1], mMat),
            Quad(self.vertices[0], self.vertices[1] - self.vertices[0], self.vertices[4] - self.vertices[0], mMat),
            Quad(self.vertices[2], self.vertices[3] - self.vertices[2], self.vertices[6] - self.vertices[2], mMat)
        ]

    def add_material(self, mMat):
        self.material = mMat
        for side in self.sides:
            side.add_material(mMat)

    def intersect(self, rRay, cInterval):
        current_interval = rtu.Interval(cInterval.min_val, cInterval.max_val)
        closest_hit = None

        for side in self.sides:
            hit_info = side.intersect(rRay, current_interval)
            if hit_info is not None:
                current_interval.max_val = hit_info.getT()
                closest_hit = hit_info

        return closest_hit
