import math
import re
from shapely import geometry as geo
from functools import cmp_to_key


def orientation(p1, p2, p3):
    val = (float(p2[1] - p1[1]) * (p3[0] - p2[0])) - \
        (float(p2[0] - p1[0]) * (p3[1] - p2[1]))

    if val > 0:
        # Clockwise orientation
        # print("orientation: Clockwise")
        return 1

    elif val < 0:
        # Counterclockwise orientation
        # print("orientation: Counterclockwise")
        return -1

    elif val == 0:
        # Collinear orientation
        # print("orientation: Collinear orientation")
        return 0


class ConvexHull:
    def __init__(self, point_list):
        self.point_list = point_list
        self.upper_tan = list()
        self.lower_tan = list()
        self.cvhull = list()
        self.mid_point = [0] * 2

        for point in point_list:
            self.mid_point[0] += point[0]
            self.mid_point[1] += point[1]
        self.mid_point[0] /= len(point_list)
        self.mid_point[1] /= len(point_list)

        self.brute_cvhull()

    def __clockwise_compare(self, point1, point2):
        vec_p = [point1[0] - self.mid_point[0], point1[1] - self.mid_point[1]]
        vec_q = [point2[0] - self.mid_point[0], point2[1] - self.mid_point[1]]
        val = vec_p[1] * vec_q[0] - vec_q[1] * vec_p[0]

        if val > 0:
            return 1
        elif val == 0:
            return 0
        elif val < 0:
            return -1

    # Convex Hull Brute Force
    def brute_cvhull(self):
        if len(self.point_list) == 1:
            self.cvhull.append(self.point_list[0])

        elif len(self.point_list) >= 2:
            print("convex hull >= 2 point")
            self.cvhull += self.point_list
            self.cvhull.sort(key=cmp_to_key(self.__clockwise_compare))


def convex_hull_merge(hull_a: ConvexHull, hull_b: ConvexHull) -> ConvexHull:
    print(f"Start to merge the Convex Hull: {hull_a.cvhull} {hull_b.cvhull}")
    size_a = len(hull_a.cvhull)
    size_b = len(hull_b.cvhull)
    upper_done = False
    lower_done = False
    ret_hull = list()
    ind_a = hull_a.cvhull.index(max(hull_a.cvhull, key=lambda x: x[0]))
    ind_b = hull_b.cvhull.index(min(hull_b.cvhull, key=lambda x: x[0]))

    # upper tangent
    upper_a = ind_a
    upper_b = ind_b
    while not upper_done:
        upper_done = True
        while orientation(hull_b.cvhull[upper_b],
                          hull_a.cvhull[upper_a], hull_a.cvhull[(upper_a + 1) % size_a]) >= 0:
            upper_a = (upper_a + 1) % size_a

        while orientation(hull_a.cvhull[upper_a],
                          hull_b.cvhull[upper_b], hull_b.cvhull[(upper_b - 1) % size_b]) <= 0:
            upper_b = (upper_b - 1) % size_b
            upper_done = False

    hull_a.upper_tan = [hull_b.cvhull[upper_b], hull_a.cvhull[upper_a]]
    print("hull a upper tangent: ", hull_a.upper_tan)

    # lower tangent
    lower_a = ind_a
    lower_b = ind_b
    while not lower_done:
        lower_done = True
        while orientation(hull_a.cvhull[lower_a],
                          hull_b.cvhull[lower_b], hull_b.cvhull[(lower_b + 1) % size_b]) >= 0:
            lower_b = (lower_b + 1) % size_b

        while orientation(hull_b.cvhull[lower_b],
                          hull_a.cvhull[lower_a], hull_a.cvhull[(lower_a - 1) % size_a]) <= 0:
            lower_a = (lower_a - 1) % size_a
            lower_done = False

    hull_a.lower_tan = [hull_a.cvhull[lower_a], hull_b.cvhull[lower_b]]
    print("hull lower tangent: ", hull_a.lower_tan)

    ind = upper_a
    ret_hull.append(hull_a.cvhull[ind])
    while ind != lower_a:
        ind = (ind + 1) % size_a
        ret_hull.append(hull_a.cvhull[ind])

    ind = lower_b
    ret_hull.append(hull_b.cvhull[ind])
    while(ind != upper_b):
        ind = (ind + 1) % size_b
        ret_hull.append(hull_b.cvhull[ind])
    ret_hull.append(ret_hull[0])

    hull_a.cvhull = ret_hull.copy()
    return hull_a


class VoronoiDiagram:
    def __init__(self, point_list):
        self.point_list = sorted(point_list)
        self.record = list()
        self.polyedge_list = list()     # for final result
        self.polypoints_list = list()   # for final result
        self.convex_hull_list = list()
        self.hyperplane_list = list()

        self.run()

    def run(self, type=0):
        print("Start:", self.point_list)
        self.__garbage(self.point_list)

    def __garbage(self, point_list):
        print("Divided:", point_list)
        split = int(len(point_list)/2)
        l_pointlist = point_list[0: split]
        r_pointlist = point_list[split:]

        # Brute Fore
        if len(point_list) <= 3:
            self.__brute_vd(point_list)
            ret_cvhull = ConvexHull(point_list)
            self.convex_hull_list = (
                ret_cvhull.cvhull + ret_cvhull.cvhull[0]).copy()
            # ret_cvhull.brute_cvhull()

            return ret_cvhull

        # Get the ret_cvhull from conquer
        l_cvhull = self.__garbage(l_pointlist)
        print("finish left:", l_pointlist)
        r_cvhull = self.__garbage(r_pointlist)
        print("finish right:", r_pointlist)

        # Merge
        print(f"Merge: l: {l_pointlist}, r: {r_pointlist}")
        ret_cvhull = convex_hull_merge(l_cvhull, r_cvhull)
        self.convex_hull_list = ret_cvhull.cvhull.copy()

        # Hyperplane
        self.__hyperplane(ret_cvhull)

    # TODO: Set the return
    def __brute_vd(self, point_list):
        s_index = 0
        dis_list = list()

        # 1 point case
        if len(point_list) == 1:
            self.__writeback_record('n', False, point_list, None)
            return

        # 2 points case
        elif len(point_list) == 2:
            p_bisector = self.__p_bisector(*point_list)
            self.polyedge_list.append(p_bisector)
            self.polypoints_list.append(point_list)
            self.__writeback_record('n', False, point_list, p_bisector)
            return

        # 3 points case
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

        return

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
        if line_a == line_b:
            return None
        geo_line1 = geo.LineString(line_a)
        geo_line2 = geo.LineString(line_b)
        print("intersection: ", geo_line1, geo_line2, end=" - ")

        if geo_line1.intersects(geo_line2):
            intersection = geo_line1.intersection(geo_line2)
            if(0 <= intersection.x <= 600 and 0 <= intersection.y <= 600):
                print([intersection.x, intersection.y])
                return [intersection.x, intersection.y]
        print("None")
        return None

    def __hyperplane(self, cvhull: ConvexHull):
        l_cur_point = list()
        r_cur_point = list()
        hyperplane = self.__p_bisector(*cvhull.upper_tan)
        # Sort by y, make sure the hyperplane can go down
        hyperplane.sort(reverse=True, key=lambda x: x[1])
        r_cur_point = cvhull.upper_tan[0].copy()
        l_cur_point = cvhull.upper_tan[1].copy()
        l_next_point = list()
        r_next_point = list()

        # self.polyedge_list.append(hyperplane)
        # self.polypoints_list.append([cvhull.upper_tan[0], cvhull.upper_tan[1]])

        while l_cur_point != cvhull.lower_tan[0] or r_cur_point != cvhull.lower_tan[1]:
            l_highest_inters = [0, -1]
            r_highest_inters = [0, -1]
            l_line_ind = 0
            r_line_ind = 0
            l_line_set = list()
            r_line_set = list()

            for points in self.polypoints_list:
                if l_cur_point in points:
                    l_line_set.append(self.polypoints_list.index(points))

                if r_cur_point in points:
                    r_line_set.append(self.polypoints_list.index(points))

            # Find the highest intersection between the hyperplane and the lines beside the point
            # TODO: Get the next point
            for ind in l_line_set:
                check_line = self.polyedge_list[ind]
                hyper_inters = self.__line_intersection(
                    hyperplane[-2:], check_line)
                if hyper_inters:
                    if hyper_inters[1] > l_highest_inters[1]:
                        l_highest_inters = hyper_inters.copy()
                        l_next_point = self.polypoints_list[ind][0].copy() \
                            if self.polypoints_list[ind][0] != l_cur_point else self.polypoints_list[ind][1].copy()
                        l_line_ind = ind

            for ind in r_line_set:
                check_line = self.polyedge_list[ind]
                hyper_inters = self.__line_intersection(
                    hyperplane[-2:], check_line)
                if hyper_inters:
                    if hyper_inters[1] > r_highest_inters[1]:
                        r_highest_inters = hyper_inters.copy()
                        r_next_point = self.polypoints_list[ind][0].copy() \
                            if self.polypoints_list[ind][0] != r_cur_point else self.polypoints_list[ind][1]
                        r_line_ind = ind

            if len(hyperplane) == 2:
                hyperplane.pop()

            # TODO: Judge the relation between the hyperplane and the lines
            if l_highest_inters == r_highest_inters:
                # left part: change the point with higher x
                if self.polyedge_list[l_line_ind][0][0] < self.polyedge_list[l_line_ind][1][0]:
                    self.polyedge_list[l_line_ind][1] = l_highest_inters.copy()
                else:
                    self.polyedge_list[l_line_ind][0] = l_highest_inters.copy()

                # right part: change the point with lower x
                if self.polyedge_list[r_line_ind][0][0] < self.polyedge_list[r_line_ind][1][0]:
                    self.polyedge_list[r_line_ind][0] = r_highest_inters.copy()
                else:
                    self.polyedge_list[r_line_ind][1] = r_highest_inters.copy()

                l_cur_point = l_next_point.copy()
                r_cur_point = r_next_point.copy()
                hyperplane.append(l_highest_inters)

            elif l_highest_inters[1] > r_highest_inters[1]:
                if self.polyedge_list[l_line_ind][0][0] < self.polyedge_list[l_line_ind][1][0]:
                    self.polyedge_list[l_line_ind][1] = l_highest_inters.copy()
                else:
                    self.polyedge_list[l_line_ind][0] = l_highest_inters.copy()

                l_cur_point = l_next_point.copy()
                hyperplane.append(l_highest_inters)

            elif l_highest_inters[1] < r_highest_inters[1]:
                if self.polyedge_list[r_line_ind][0][0] < self.polyedge_list[r_line_ind][1][0]:
                    self.polyedge_list[r_line_ind][0] = r_highest_inters.copy()
                else:
                    self.polyedge_list[r_line_ind][1] = r_highest_inters.copy()

                r_cur_point = r_next_point.copy()
                hyperplane.append(r_highest_inters)

            temp_hyper = self.__p_bisector(l_cur_point, r_cur_point)
            temp_hyper.sort(reverse=True, key=lambda x: x[1])
            hyperplane.append(temp_hyper[1])

        print(f"hyperplane: {hyperplane}")
        self.hyperplane_list = hyperplane.copy()

    # TODO: Save all the line on the graph
    def __writeback_record(self, type, clean, points, *lines):
        temp_dict = dict()
        temp_dict['type'] = type
        temp_dict['clean'] = clean
        temp_dict['points'] = points
        temp_dict['edges'] = lines
        self.record.append(temp_dict)


if __name__ == '__main__':
    point_list_a = [[5, 3], [4, 8], [7, 6]]
    point_list_b = [[9, 8], [10, 2], [12, 6]]

    vd = VoronoiDiagram(point_list_a)
    print("main: ", vd.polyedge_list)

    # ch = ConvexHull(point_list_a)
    # print(ch.point_list)
    # print(max(point_list_a, key=lambda x: x[0]))
    # orientation(*ch.point_list)

    # hull_a = ConvexHull(point_list_a)
    # print(hull_a.cvhull)
    # hull_b = ConvexHull(point_list_b)
    # print(hull_b.cvhull)
    # out_hull = convex_hull_merge(hull_a, hull_b)

    # print(out_hull.cvhull)
