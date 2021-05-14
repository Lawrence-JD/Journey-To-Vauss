import math
import vector
import pygame


def collides(a, b):
    if not isinstance(a, Shape) or not isinstance(b, Shape):
        raise ValueError("Both objects must be derived from Shape class")

    test_axes = []
    test_origins = []

    a_axes = a.getProjectionAxes(b)
    for ax in a_axes:
        test_axes.append(ax)
        test_origins.append(a.mPos)
    b_axes = b.getProjectionAxes(a)
    for bx in b_axes:
        test_axes.append(bx)
        test_origins.append(b.mPos)

    for i in range(len(test_axes)):
        a_ext = a.getProjectedExtents(a.mPos, test_axes[i])
        b_ext = b.getProjectedExtents(a.mPos, test_axes[i])
        result = a_ext[1] < b_ext[0] or b_ext[1] < a_ext[0]
        if result:
            return False
    return True


class Shape:
    def __init__(self, color, pos):
        if not isinstance(pos, vector.Vector2):
            raise ValueError("Position must be a Vector2")
        self.mColor = color
        self.mPos = pos.copy()
        self.mAngle = 0                 # In radians

    def drawPygame(self, surf, draw_selected, draw_collided):
        return """
        pygame.draw.circle(surf, (255, 255, 255), self.mPos.i, 3)
        xaxis, yaxis = self.getAxes()
        pygame.draw.line(surf, (255, 0, 0), self.mPos, self.mPos + 15 * xaxis, 3)
        pygame.draw.line(surf, (0, 255, 0), self.mPos, self.mPos + 15 * yaxis, 3)"""


    def getAxes(self):
        xaxis = vector.polar_to_vector2(self.mAngle, 1.0)
        yaxis = vector.polar_to_vector2(self.mAngle + math.pi / 2.0, 1.0)
        return (xaxis, yaxis)


    def rotate(self, degree_offset):
        self.mAngle += math.radians(degree_offset)


    def pointInShape(self, p):
        raise NotImplementedError("Sorry -- the derived classes need to define this")


    def getProjectedExtents(self, origin, axis):
        raise NotImplementedError("Sorry -- the derived classes need to define this")


    def getProjectionAxes(self, other):
        raise NotImplementedError("Sorry -- the derived classes need to define this")


class Cuboid(Shape):
    def __init__(self, color, pos, extents):
        if not hasattr(extents, "__len__") or not hasattr(extents, "__getitem__") or len(extents) != 2:
            raise ValueError("extents must be a sequence of 2 values")
        super().__init__(color, pos)
        self.mExtents = []
        for i in range(2):
            self.mExtents.append(float(extents[i]) / 2.0)

    def drawPygame(self, surf, draw_selected=0, draw_collided=0):
        corners = self.getCorners()
        if draw_collided:
            pygame.draw.polygon(surf, (255,0,0), corners)
        else:
            pygame.draw.polygon(surf, self.mColor, corners)
        if draw_selected:
            pygame.draw.polygon(surf, (255, 255, 255), corners, 1)
        super().drawPygame(surf, draw_selected, draw_collided)

    def getCorners(self):
        xaxis, yaxis = self.getAxes()
        a = self.mPos - self.mExtents[0] * xaxis - self.mExtents[1] * yaxis
        b = a + self.mExtents[0] * 2 * xaxis
        c = a + self.mExtents[1] * 2 * yaxis
        d = c + self.mExtents[0] * 2 * xaxis
        return (a, b, d, c)

    def pointInShape(self, p):
        xaxis = vector.polar_to_vector2(self.mAngle, 1.0)
        yaxis = vector.polar_to_vector2(self.mAngle + math.pi / 2.0, 1.0)
        projX = vector.dot(p - self.mPos, xaxis)
        projY = vector.dot(p - self.mPos, yaxis)
        return -self.mExtents[0] <= projX <= self.mExtents[0] and -self.mExtents[1] <= projY <= self.mExtents[1]

    def getProjectedExtents(self, origin, axis):
        corners = self.getCorners()
        ext = [None, None]
        for c in corners:
            p = c - origin
            val = vector.dot(p, axis)
            if ext[0] == None or val < ext[0]:
                ext[0] = val
            if ext[1] == None or val > ext[1]:
                ext[1] = val
        return ext

    def getProjectionAxes(self, other):
        return self.getAxes()


class mCuboid(Shape):
    def __init__(self, color, pos, extents):
        super().__init__(color, pos)
        self.mExtents = []
        for i in range(2):
            self.mExtents.append(float(extents[i]) / 2.0)

    def drawPygame(self, surf, draw_selected=0, draw_collided=0):
        corners = self.getCorners()
        if draw_collided:
            pygame.draw.polygon(surf, (255,0,0), corners)
        else:
            pygame.draw.polygon(surf, self.mColor, corners)
        if draw_selected:
            pygame.draw.polygon(surf, (255, 255, 255), corners, 1)
        super().drawPygame(surf, draw_selected, draw_collided)

    def getCorners(self):
        xaxis, yaxis = self.getAxes()
        a = self.mPos - self.mExtents[1] * yaxis
        b = a + self.mExtents[0] * 2 * xaxis
        c = a + self.mExtents[1] * 2 * yaxis
        d = c + self.mExtents[0] * 2 * xaxis
        return (a, b, d, c)

    def pointInShape(self, p):
        xaxis = vector.polar_to_vector2(self.mAngle, 1.0)
        yaxis = vector.polar_to_vector2(self.mAngle + math.pi / 2.0, 1.0)
        projX = vector.dot(p - self.mPos, xaxis)
        projY = vector.dot(p - self.mPos, yaxis)
        return -self.mExtents[0] <= projX <= self.mExtents[0] and -self.mExtents[1] <= projY <= self.mExtents[1]

    def getProjectedExtents(self, origin, axis):
        corners = self.getCorners()
        ext = [None, None]
        for c in corners:
            p = c - origin
            val = vector.dot(p, axis)
            if ext[0] == None or val < ext[0]:
                ext[0] = val
            if ext[1] == None or val > ext[1]:
                ext[1] = val
        return ext

    def getProjectionAxes(self, other):
        return self.getAxes()


class Triangle(Shape):
    def __init__(self, color, pos, points):
        super().__init__(color, pos)
        self.mPoints = []
        self.mPoints3d = []
        for p in points:
            v = p - self.mPos
            self.mPoints.append(v)
            self.mPoints3d.append(vector.Vector3(v.x, v.y, 0))
        self.mArea = vector.cross(self.mPoints3d[1] - self.mPoints3d[0], self.mPoints3d[2] - self.mPoints3d[0]).magnitude / 2.0

    def drawPygame(self, surf, draw_selected, draw_collided):
        xaxis, yaxis = self.getAxes()
        draw_pts = []
        for p in self.mPoints:
            draw_pts.append(self.mPos + p[0] * xaxis + p[1] * yaxis)
        if draw_collided:
            pygame.draw.polygon(surf, (255, 0, 0), draw_pts)
        else:
            pygame.draw.polygon(surf, self.mColor, draw_pts)
        if draw_selected:
            pygame.draw.polygon(surf, (255, 255, 255), draw_pts, 1)
        super().drawPygame(surf, draw_selected, draw_collided)

    def barycentric(self, P):
        xaxis, yaxis = self.getAxes()
        pts3d = []
        for p in self.mPoints:
            v = self.mPos + p[0] * xaxis + p[1] * yaxis
            pts3d.append(vector.Vector3(v.x, v.y, 0))

        bcoord = []
        den = self.mArea * 2.0
        p3d = vector.Vector3(P.x, P.y, 0)
        bcoord.append(vector.cross(pts3d[1] - p3d, pts3d[2] - p3d).magnitude / den)
        bcoord.append(vector.cross(pts3d[0] - p3d, pts3d[2] - p3d).magnitude / den)
        bcoord.append(vector.cross(pts3d[0] - p3d, pts3d[1] - p3d).magnitude / den)
        return bcoord


    def pointInShape(self, p):
        bary = self.barycentric(p)
        return 0.9999 <= bary[0] + bary[1] + bary[2] <= 1.0001



    def getProjectedExtents(self, origin, axis):
        xaxis, yaxis = self.getAxes()
        pts = []
        for p in self.mPoints:
            v = self.mPos + p[0] * xaxis + p[1] * yaxis
            pts.append(v)
        ext = [None, None]
        for c in pts:
            p = c - origin
            val = vector.dot(p, axis)
            if ext[0] == None or val < ext[0]:
                ext[0] = val
            if ext[1] == None or val > ext[1]:
                ext[1] = val
        return ext


    def getProjectionAxes(self, other):
        xaxis, yaxis = self.getAxes()
        pts = []
        for p in self.mPoints:
            v = self.mPos + p[0] * xaxis + p[1] * yaxis
            pts.append(v)

        axes = []
        for i in range(3):
            j = (i + 1) % 3
            w = (pts[j] - pts[i]).normalized
            axes.append(w.perpendicular)
        return axes


class Sphere(Shape):
    def __init__(self, color, pos, radius):
        super().__init__(color, pos)
        self.mRadius = radius
        self.mRadiusSq = self.mRadius ** 2     # An optimization

    def drawPygame(self, surf, draw_selected, draw_collided):
        if draw_collided:
            pygame.draw.circle(surf, (255, 0, 0), self.mPos.i, self.mRadius)
        else:
            pygame.draw.circle(surf, self.mColor, self.mPos.i, self.mRadius)
        if draw_selected:
            pygame.draw.circle(surf, (255, 255, 255), self.mPos.i, self.mRadius, 1)
        super().drawPygame(surf, draw_selected, draw_collided)

    def pointInShape(self, p):
        return (p - self.mPos).magnitudeSquared <= self.mRadiusSq



    def getProjectedExtents(self, origin, axis):
        offset = self.mPos - origin
        val = vector.dot(offset, axis)
        return [val - self.mRadius, val + self.mRadius]


    def getProjectionAxes(self, other):
        return [(other.mPos - self.mPos).normalized]


