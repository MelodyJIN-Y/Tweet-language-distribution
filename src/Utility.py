import json
import numpy as np
import os
import sys
sys.path.append("shapely")
from collections import defaultdict
from shapely.geometry import *
from shapely.geometry import Polygon


# convert abbreviations to full language name
CONVERTOR = {"en":"English","ar":"Arabic","bn":"Bengalid","cs":"Czech","da":"Danish","de":"German","el":"Greek",
             "es":"Spanish","fa":"Persian","fi":"Finnish","fil":"Filipino","fr":"French","he":"Hebrew","hi":"Hindi",
             "hu":"Hungarian","id":"Indonesian", "in":"Indonesian","it":"Italian","ja":"Japanese","ko":"Korean",
             "msa":"Malay","nl":"Dutch","no":"Norwegian","pl":"Polish","pt":"Portuguese","ro":"Romanian","ru":"Russian",
             "sv":"Swedish","th":"Thai","tr":"Turkish","uk":"Ukrainian","ur":"Urdu","vi":"Vietnamese",
             "zh-cn":"Chinese","zh-tw":"Chinese","tl":"Tagalog"}
# define the index of allowed vertex coordinates for each cell.
ALLOED_COORDS = {'A1':[0,1], 'A2':[1], 'A3':[1], 'A4':[1],
                 'B1':[0,1], 'B2':[1], 'B3':[1], 'B4':[1],
                 'C1':[0,1], 'C2':[1], 'C3':[1], 'C4':[1],
                 'D1':[0,1,2,3], 'D2':[1,2], 'D3':[1,2], 'D4':[1,2]}
# define cells whose left border should be counted
LEFT_BORDER_CELLS = ["A1","B1","C1","D1"]
# define cells  whose bottom border should be counted
BOTTOM_BORDER_CELLS = ["D1","D2","D3","D4"]

grid ={}
class Cell():
    def __init__(self, poly, name):

        self.name = name
        # a polygon object
        self.polygon = Polygon([list(i) for i in poly])

        # raw coordiates
        self.coords  = np.array([list(i) for i in poly])

        # a list of ordered coordinates, left_top, right_top, right_bottom, left_bottom
        self.ordered_coords = self.get_ordered_points()
        # a list of not-allowed vertex coordinates
        self.exc_coords = [self.ordered_coords[pt] for pt in (set(list(range(4))) - set(ALLOED_COORDS[self.name]))]
        #print(self.exc_coords)
        # raw coordiates
        # self.ordered_pts = Polygon([Point(i) for i in self.ordered_coords])

        # get four borders as LineString object
        self.left, self.top, self.right, self.bottom = self.get_borders()
        # a border dictionary
        self.borders = {"left":self.left, "top": self.top,
                        "right":self.right, "bottom": self.bottom}

        # count dictionary, keys are the languages abbreviation, values are the counts in a cell
        self.count_dict = defaultdict(int)

        # non-zero language count pairs, full name converted
        self.final_result = {}

        # a summary for a cell
        self.summary = {}

    # get an ordered set of coordinates
    def get_ordered_points(self):
        x_coords = [pt[0] for pt in self.coords]
        y_coords = [pt[1] for pt in self.coords]
        x = np.min(x_coords)
        y = np.max(y_coords)
        width = np.max(x_coords) - np.min(x_coords)
        height = np.max(y_coords) - np.min(y_coords)
        left_top = [x, y]
        right_top = [x + width, y]
        right_bottom = [x + width, y - height]
        left_bottom = [x, y - height]

        return [left_top, right_top, right_bottom, left_bottom]

    # get four LineString define the border of a cell
    def get_borders(self):
        left = LineString([Point(self.ordered_coords[0]),Point(self.ordered_coords[3])])
        top = LineString([Point(self.ordered_coords[0]), Point(self.ordered_coords[1])])
        right = LineString([Point(self.ordered_coords[1]), Point(self.ordered_coords[2])])
        bottom = LineString([Point(self.ordered_coords[2]), Point(self.ordered_coords[3])])
        return left, top, right, bottom

    # check if a given point(pt) is on any valid border of a cell
    # Increase language count number if True
    def is_on_border(self, pt, lang):
        on_board=""
        for name, border in self.borders.items():
            # if the pt intersects with the LineString
            if border.intersects(pt):
                # if the intersection is not at any not-allowed vertex coordiantes of cell
                if not ([pt.x, pt.y] in (self.exc_coords)):
                    on_board = name
                    break
        # check valid border
        if on_board == "right":
            self.count_dict[lang] +=1
            return True
        if on_board == "top":
            self.count_dict[lang] +=1
            return True

        if (on_board == "left") and (self.name in LEFT_BORDER_CELLS):
            self.count_dict[lang] += 1
            return True

        if (on_board == "bottom") and (self.name in BOTTOM_BORDER_CELLS):
            self.count_dict[lang] += 1
            return True

        return False

    # check valid corner point
    def is_corner(self, pt, lang):

        if pt.x == self.ordered_coords[1][0] and pt.y == self.ordered_coords[1][1]:
            self.count_dict[lang] += 1
            return True
        return False

    # check valid within-cell point
    def is_within(self, pt, lang):
        if self.polygon.contains(pt):
            self.count_dict[lang] += 1
            return True
        return False

    # update cell's count dictionary
    def update_count(self, pt, lang):
        # point on left_top corner
        check = self.is_corner(pt, lang)
        if check:
            return True

        # point within cell region
        check = self.is_within(pt, lang)
        if check:
            return True

        # point on cell border
        check = self.is_on_border(pt, lang)
        if check:
            return True

        # point not in the cell
        else:
            return False

    # get summary of the cell
    def get_summary(self):

        self.summary["cell"] = self.name
        # total tweets
        self.summary["total_tweets"] = sum(self.count_dict.values())
        # number of languages used
        self.summary["num_langs"] = len([ke for ke in list(self.count_dict.keys())])

        # merge two Chinese language versions
        self.count_dict["zh-cn"] += self.count_dict["zh-tw"]
        del self.count_dict["zh-tw"]

        # convert abbreviation to full language name if abbreviation is known
        for abbr in list(self.count_dict.keys()):
            if self.count_dict[abbr] != 0:
                full = abbr
                if abbr in list(CONVERTOR.keys()):
                    full = CONVERTOR[abbr]
                self.final_result[full] = self.count_dict[abbr]

        if len(self.final_result) == 0:
            self.summary["top_10"] = " "
        else:
            # print(self.final_result)
            idx = min(10, len(self.final_result))
            # Top 10 Languages & #Tweets
            tp10= [str(ke) + "-" + str(self.final_result[ke]) for ke in sorted(self.final_result,key=self.final_result.get,reverse=True)[:idx]]
            self.summary["top_10"] = '(' + ', '.join([ele for ele in tp10]) + ')'
