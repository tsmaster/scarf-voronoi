#
# Voronoi Scarf Generator
# By Dave LeCompte tsmaster@gmail.com
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# See also "Fast Poisson Disk Sampling in Arbitrary Dimensions" by Robert Bridson

from PIL import Image
import random
import math

X = 100
Y = 1200

CELL_EDGE_WIDTH = 4

BORDER_WIDTH = 4

DIST_BETWEEN_POINTS = 25

POPULATION_RETRIES = 30

EDGE_COLOR = (50, 50, 50)
BASE_COLOR = (255, 255, 255)

GRID_SIZE = int(DIST_BETWEEN_POINTS / math.sqrt(2.0))

points = []

vorScarfImg = Image.new("RGB", (X, Y))

indexCache = {}

grid = None

def findClosestPointIndexOld(x, y):
    key = (x,y)
    if key in indexCache:
        return indexCache[key]

    bestDist = (X + Y) * (X + Y)
    bestIndex = -1

    for i, (px, py) in enumerate(points):
        dx = px - x
        dy = py - y
        dSqr = dx * dx + dy * dy
        if dSqr < bestDist:
            bestDist = dSqr
            bestIndex = i
    indexCache[key] = bestIndex
    return bestIndex

def findClosestPointIndex(x, y):
    key = (x,y)
    if key in indexCache:
        return indexCache[key]

    neighborIndices = []
    r = DIST_BETWEEN_POINTS
    while len(neighborIndices) == 0:
        r = r * 2
        neighborIndices = list(findNeighborIndicesInGrid(x, y, r))

    bestRadiusSqr = 1e30
    bestIndex = -1
    for ni in neighborIndices:
        nx, ny = points[ni]
        dx = nx - x
        dy = ny - y
        dSqr = dx * dx + dy * dy
        if dSqr < bestRadiusSqr:
            bestRadiusSqr = dSqr
            bestIndex = ni
    indexCache[key] = bestIndex
    return bestIndex

def isOnBorder(x, y):
    return (x < BORDER_WIDTH or x + BORDER_WIDTH >= X or
            y < BORDER_WIDTH or y + BORDER_WIDTH >= Y)

def isOnEdge(x, y):
    ci = findClosestPointIndex(x, y)

    EWSQR = CELL_EDGE_WIDTH * CELL_EDGE_WIDTH

    for tx in range(x - CELL_EDGE_WIDTH, x + CELL_EDGE_WIDTH + 1):
        for ty in range(y - CELL_EDGE_WIDTH, y + CELL_EDGE_WIDTH + 1):
            dx = tx - x
            dy = ty - y
            if dx * dx + dy * dy > EWSQR:
                continue
            if tx < 0 or tx >= X or ty < 0 or ty >= Y:
                continue
            ti = findClosestPointIndex(tx, ty)
            if ti != ci:
                return True
    return False


def makeGrid():
    global grid

    GX = int(math.ceil(X * 1.0 / GRID_SIZE))
    GY = int(math.ceil(Y * 1.0 / GRID_SIZE))

    grid = [[-1 for gy in range(GY)] for gx in range(GX)]

def findPointInGrid(x, y):
    sx = int (x * 1.0 / GRID_SIZE)
    sy = int (y * 1.0 / GRID_SIZE)
    return grid[sx][sy]

def findNeighborIndicesInGrid(x, y, r):
    ax = int((x - r) * 1.0 / GRID_SIZE)
    bx = int((x + r) * 1.0 / GRID_SIZE) + 1
    ay = int((y - r) * 1.0 / GRID_SIZE)
    by = int((y + r) * 1.0 / GRID_SIZE) + 1

    ax = max(0, ax)
    bx = min(bx, len(grid) - 1)

    ay = max(0, ay)
    by = min(by, len(grid[0]) - 1)

    for ix in range(ax, bx+1):
        for iy in range(ay, by+1):
            gi = grid[ix][iy]
            if gi == -1:
                continue
            px, py = points[gi]

            dx = px - x
            dy = py - y

            if (dx * dx + dy * dy < r * r):
                yield gi

def findNeighborsInGrid(x, y, r):
    ax = int((x - r) * 1.0 / GRID_SIZE)
    bx = int((x + r) * 1.0 / GRID_SIZE) + 1
    ay = int((y - r) * 1.0 / GRID_SIZE)
    by = int((y + r) * 1.0 / GRID_SIZE) + 1

    ax = max(0, ax)
    bx = min(bx, len(grid) - 1)

    ay = max(0, ay)
    by = min(by, len(grid[0]) - 1)

    for ix in range(ax, bx+1):
        for iy in range(ay, by+1):
            gi = grid[ix][iy]
            if gi == -1:
                continue
            px, py = points[gi]

            dx = px - x
            dy = py - y

            if (dx * dx + dy * dy < r * r):
                yield (px, py)

def isLegalPoint(x, y):
    # first, check to see if it's in bounds
    if (x < 0 or x > X or
        y < 0 or y > Y):
        return False

    for np in findNeighborsInGrid(x, y, DIST_BETWEEN_POINTS):
        return False

    return True

def genDisplacedPoint(x, y, minRadius, maxRadius):
    while True:
        rx = random.uniform(x - maxRadius, x + maxRadius)
        ry = random.uniform(y - maxRadius, y + maxRadius)

        dx = rx - x
        dy = ry - y

        dSqr = dx * dx + dy * dy
        if (dSqr < minRadius * minRadius or
            dSqr > maxRadius * maxRadius):
            continue
        return rx, ry

def addPointToGrid(x, y, i):
    sx = int (x * 1.0 / GRID_SIZE)
    sy = int (y * 1.0 / GRID_SIZE)
    grid[sx][sy] = i
    points.append((x, y))

def fillGrid():
    activeList = []

    hd = DIST_BETWEEN_POINTS / 2.0

    x = random.uniform(hd, X - hd)
    y = random.uniform(hd, Y - hd)

    addPointToGrid(x, y, 0)
    activeList.append((x,y))

    while activeList:
        i = random.randrange(len(activeList))
        x, y = activeList[i]
        anyAdded = False
        for k in range(POPULATION_RETRIES):
            nx, ny = genDisplacedPoint(x, y, DIST_BETWEEN_POINTS, 2*DIST_BETWEEN_POINTS)
            if isLegalPoint(nx, ny):
                #print "placing", len(points), nx, ny
                anyAdded = True
                addPointToGrid(nx, ny, len(points))
                activeList.append((nx, ny))
                break
        if not anyAdded:
            activeList.pop(i)

def drawEdges():
    for x in range(0, X):
        #print "x:",x
        for y in range(0, Y):
            if (isOnBorder(x, y) or isOnEdge(x,y)):
                c = EDGE_COLOR
            else:
                c = BASE_COLOR

            vorScarfImg.putpixel((x, y), c)



makeGrid()
fillGrid()
drawEdges()

vorScarfImg.save("scarf.png")
vorScarfImg.save("scarf.tiff")
