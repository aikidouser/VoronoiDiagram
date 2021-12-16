import math
import re
from shapely import geometry as geo
from functools import cmp_to_key


def orientation(p1, p2, p3):
    val = (float(p2[1] - p1[1]) * (p3[0] - p2[0])) - \
        (float(p2[0] - p1[0]) * (p3[1] - p2[1]))

    if (val > 0):
        # Clockwise orientation
        print("orientation: Clockwise")
        return 1

    elif (val < 0):
        # Counterclockwise orientation
        print("orientation: Counterclockwise")
        return 2

    else:
        # Collinear orientation
        print("orientation: Collinear orientation")
        return 0


class VoronoiDiagram:
    def __init__(self, point_list):
        self.point_list = sorted(point_list)
        self.record = list()
        self.polyedge_list = list()     # for final result
        self.polypoints_list = list()   # for final result

        self.run()

    def run(self, type=0):
        print("Start:", self.point_list)
        self.__garbage(self.point_list)

    def __garbage(self, point_list):
        print("Divided:", point_list)
        split = int(len(point_list)/2)
        l_pointlist = point_list[0: split]
        r_pointlist = point_list[split:]
        hyperplane_list = list()

        if len(point_list) <= 3:
            self.__brute_vd(point_list)
            return

        self.__garbage(l_pointlist)
        print("finish left:", l_pointlist)
        self.__garbage(r_pointlist)
        print("finish right:", r_pointlist)

        # Merge
        print("Merge: l: {l_pointlist}, r: {r_pointlist}")

    def __brute_vd(self, point_list):
        s_index = 0
        dis_list = list()

        # TODO: check if need to merge
        if len(point_list) == 1:
            self.__writeback_record('n', False, point_list, None)
            return

        elif len(point_list) == 2:
            p_bisector = self.__p_bisector(*self.point_list)
            self.polyedge_list.append(p_bisector)
            self.polypoints_list.append(point_list)
            self.__writeback_record('n', False, point_list, p_bisector)
            return

        for i in range(len(point_list)):
            dis_list.append(math.dist(point_list[i], point_list[(i+1) % 3]))

        s_index = (dis_list.index(max(dis_list)) + 1) % 3
        point_list += point_list[:s_index]
        del point_list[0:s_index]

        # point_list = anti_clockwise(point_list)
        if orientation(*point_list) == 1:  # if it is clockwise
            point_list.reverse()
        l_p_bisector = self.__p_bisector(point_list[0], point_list[1])
        r_p_bisector = self.__p_bisector(point_list[1], point_list[2])
        circumcenter = self.__line_intersection(l_p_bisector, r_p_bisector)

        def write_back():
            self.polyedge_list.append(l_p_bisector)
            self.polypoints_list.append([point_list[0], point_list[1]])
            self.polyedge_list.append(r_p_bisector)
            self.polypoints_list.append([point_list[1], point_list[2]])

        if circumcenter:
            m_p_bisector = self.__p_bisector(point_list[2], point_list[0])

            l_p_bisector[0] = circumcenter
            r_p_bisector[0] = circumcenter
            m_p_bisector[0] = circumcenter
            write_back()
            self.polyedge_list.append(m_p_bisector)
            self.polypoints_list.append([point_list[2], point_list[0]])
            self.__writeback_record(
                'n', False, point_list, l_p_bisector, r_p_bisector, m_p_bisector)

        else:
            write_back()
            self.__writeback_record(
                'n', False, point_list, l_p_bisector, r_p_bisector)

    def __p_bisector(self, a, b):
        p_bisector = list()
        midpoint = [(a[0] + b[0])/2, (a[1] + b[1])/2]
        # vector = [a[0] - b[0], a[1] - b[1]]
        normal_vector = [b[1] - a[1], - (b[0] - a[0])]
        vector_extend = [i * 600 for i in normal_vector]

        start_p = [midpoint[0] - vector_extend[0],
                   midpoint[1] - vector_extend[1]]
        end_p = [midpoint[0] + vector_extend[0],
                 midpoint[1] + vector_extend[1]]
        p_bisector = [start_p, end_p]

        print(f"bisector: {a}, {b} --> {p_bisector}")
        return p_bisector

    def __line_intersection(self, line_a, line_b):
        geo_line1 = geo.LineString(line_a)
        geo_line2 = geo.LineString(line_b)
        print("intersection: ", geo_line1, geo_line2, end="")

        if geo_line1.intersects(geo_line2):
            intersection = geo_line1.intersection(geo_line2)
            if(0 <= intersection.x <= 600 and 0 <= intersection.y <= 600):
                print([intersection.x, intersection.y])
                return [intersection.x, intersection.y]
        print("None")
        return None

    # TODO:
    def __writeback_record(self, type, clean, points, *lines):
        temp_dict = dict()
        temp_dict['type'] = type
        temp_dict['clean'] = clean
        temp_dict['points'] = points
        temp_dict['edges'] = lines
        self.record.append(temp_dict)


class ConvexHull:
    def __init__(self, point_list):
        self.upper_tanget = list()
        self.lower_tanget = list()
        self.convex_hull = list()
        self.mid_point = [0] * 2

        for point in point_list:
            self.mid_point[0] += point[0]
            self.mid_point[1] += point[1]
        self.mid_point[0] /= len(point_list)
        self.mid_point[1] /= len(point_list)

        self.point_list = sorted(
            point_list, key=cmp_to_key(self.__clockwise_compare))

    def __clockwise_compare(self, point1, point2):
        vec_p = [point1[0] - self.mid_point[0], point1[1] - self.mid_point[1]]
        vec_q = [point2[0] - self.mid_point[0], point2[1] - self.mid_point[1]]
        val = vec_p[1] * vec_q[0] - vec_q[1] * vec_p[0]

        if val > 0:
            return 1
        elif val == 0:
            return 0
        else:
            return -1


if __name__ == '__main__':
    point_list = [[100, 20], [20, 40], [30, 50]]
    # vd = VoronoiDiagram(point_list)
    # print(vd.point_list)

    ch = ConvexHull(point_list)
    print(ch.point_list)
    orientation(*ch.point_list)
