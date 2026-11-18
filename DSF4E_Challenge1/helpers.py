import ezdxf
import matplotlib.pyplot as plt
import math
from shapely.geometry import Point, LineString, Polygon
import numpy as np

def get_dxf_bound(path):
    """Compute bounding box (width, height) for a DXF file."""
    try:
        doc = ezdxf.readfile(path)
        msp = doc.modelspace()

        from ezdxf import bbox
        box = bbox.extents(msp)
        width = box.extmax.x - box.extmin.x
        height = box.extmax.y - box.extmin.y

        return width, height

    except Exception as ex:
        print(f"Error reading {path}: {ex}")
        return None, None


def get_cutting_length(path):
    """Compute the total cutting length of all entities in a DXF file."""
    try:
        doc = ezdxf.readfile(path)
    except ezdxf.DXFError:
        print(f"DXF read error: {path}")
        return None

    msp = doc.modelspace()
    total_length = 0.0

    for e in msp:
        try:
            etype = e.dxftype()

            if etype == "LINE":
                s, t = e.dxf.start, e.dxf.end
                total_length += math.dist((s[0], s[1]), (t[0], t[1]))

            elif etype == "CIRCLE":
                total_length += 2 * math.pi * e.dxf.radius

            elif etype == "ARC":
                if e.dxf.end_angle < e.dxf.start_angle:
                    e.dxf.end_angle += 360

                theta = math.radians(abs(e.dxf.end_angle - e.dxf.start_angle))
                total_length += e.dxf.radius * theta

            elif etype == "LWPOLYLINE":
                pts = [(float(p[0]), float(p[1])) for p in e.get_points() if len(p) >= 2]
                if len(pts) >= 2:
                    line = LineString(pts)
                    length = line.length
                    if e.closed:
                        length += math.dist(pts[-1], pts[0])
                    total_length += length

            elif etype == "POLYLINE":
                pts = [(v.dxf.x, v.dxf.y) for v in e.vertices if hasattr(v, "dxf")]
                if len(pts) >= 2:
                    line = LineString(pts)
                    length = line.length
                    if e.is_closed:
                        length += math.dist(pts[-1], pts[0])
                    total_length += length

        except Exception as ex:
            print(f"Error in {path}, entity {etype}: {ex}")

    return total_length


def get_number_of_holes(path, area_tolerance=1e-3):
    """
    Estimate the number of holes (internal cutouts) in a DXF file.

    Args:
        path (str): DXF file path.
        area_tolerance (float): small threshold to ignore degenerate loops.

    Returns:
        int: Number of detected holes.
    """
    try:
        doc = ezdxf.readfile(path)
        msp = doc.modelspace()

        loops = []  # store shapely geometries for closed shapes
        circles = []  # store circle geometries

        for e in msp:
            etype = e.dxftype()

            if etype == "CIRCLE":
                c = e.dxf.center
                r = e.dxf.radius
                circles.append(Point(c[0], c[1]).buffer(r))

            elif etype in ("LWPOLYLINE", "POLYLINE"):
                pts = []
                if etype == "LWPOLYLINE":
                    pts = [(float(p[0]), float(p[1])) for p in e.get_points()]
                    closed = bool(e.closed)
                else:
                    pts = [(float(v.dxf.x), float(v.dxf.y)) for v in e.vertices if hasattr(v, "dxf")]
                    closed = e.is_closed

                if closed and len(pts) > 2:
                    poly = Polygon(pts)
                    if abs(poly.area) > area_tolerance:
                        loops.append(poly)

        # Start by counting all circles as holes
        hole_count = len(circles)

        # Add closed loops that are *inside* another larger loop
        for i, poly in enumerate(loops):
            is_inside = any(other.contains(poly) for j, other in enumerate(loops) if j != i)
            if is_inside:
                hole_count += 1

        return hole_count

    except Exception as ex:
        print(f"Error reading {path}: {ex}")
        return 0


def load_dxf_geometry(file_path):
    """Extract 2D geometry from DXF file into Shapely objects."""
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    polygons = []
    lines = []

    for e in msp:
        etype = e.dxftype() 
        


        # Closed 2D polyline
        if etype == "LWPOLYLINE" and e.closed:
            points = [(p[0], p[1]) for p in e.get_points()]
            polygons.append(Polygon(points))

        # Open 2D polyline
        elif etype == "LWPOLYLINE" and not e.closed:
            points = [(p[0], p[1]) for p in e.get_points()]
            lines.append(LineString(points))

        # Old-style 3D polyline (2D projection)
        elif etype == "POLYLINE":
            points = [(v.dxf.x, v.dxf.y) for v in e.vertices]
            if e.is_closed:
                polygons.append(Polygon(points))
            else:
                lines.append(LineString(points))

        # Circle
        elif etype == "CIRCLE":
            c = e.dxf.center
            r = e.dxf.radius
            circle = Point(c[0], c[1]).buffer(r, resolution=64)
            polygons.append(circle)

        # Line
        elif etype == "LINE":
            s, t = e.dxf.start, e.dxf.end
            lines.append(LineString([(s[0], s[1]), (t[0], t[1])]))

        elif etype == "ARC":
            center_x = e.dxf.center[0]
            center_y = e.dxf.center[1] 
            start_angle = e.dxf.start_angle
            end_angle = e.dxf.end_angle
            radius = e.dxf.radius
            if end_angle < start_angle:
                end_angle += 360
            theta = np.radians(np.linspace(start_angle,end_angle,100))
            x = center_x + radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            arc = LineString(np.column_stack([x, y]))
            lines.append(arc)




    return polygons, lines

def plot_dxf(file_path):
    """Plot the geometry using matplotlib."""
    polygons, lines = load_dxf_geometry(file_path)

    plt.figure(figsize=(8, 8))
    ax = plt.gca()
    ax.set_aspect("equal", "box")

    # Plot polygons
    for poly in polygons:
        x, y = poly.exterior.xy
        plt.plot(x, y, color="black", linewidth=0.8)

    # Plot lines
    for line in lines:
        x, y = line.xy
        plt.plot(x, y, color="black", linewidth=0.8)

    plt.title(f"DXF Shape: {file_path}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

