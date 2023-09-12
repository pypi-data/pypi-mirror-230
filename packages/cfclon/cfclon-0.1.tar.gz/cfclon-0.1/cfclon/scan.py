import matplotlib.pyplot as plt
import matplotlib.patches as patches

def is_inside_polygon(point, polygon):
    """Check if the point is inside the polygon using ray casting method."""
    x, y = point
    odd_nodes = False
    j = len(polygon) - 1  # Last vertex

    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if yi < y and yj >= y or yj < y and yi >= y:
            if xi + (y - yi) / (yj - yi) * (xj - xi) < x:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def is_on_polygon_edge(point, polygon):
    """Check if a point is on the edge of the polygon."""
    x, y = point
    for i in range(len(polygon)):
        px1, py1 = polygon[i]
        px2, py2 = polygon[(i + 1) % len(polygon)]
        
        # Calculate the cross product
        cross_product = (y - py1) * (px2 - px1) - (x - px1) * (py2 - py1)
        
        # If the cross product is zero, the point is on the line
        if abs(cross_product) < 1e-8 and min(px1, px2) <= x <= max(px1, px2) and min(py1, py2) <= y <= max(py1, py2):
            return True
    return False

def pixel_partially_or_fully_inside_polygon(x, y, polygon):
    """Check if any of the four vertices of the pixel are inside the polygon."""
    return (
        is_inside_polygon((x, y), polygon) or 
        is_inside_polygon((x+1, y), polygon) or 
        is_inside_polygon((x, y-1), polygon) or 
        is_inside_polygon((x+1, y-1), polygon)
    )

def pixel_area_inside_polygon_v6(x, y, polygon):
    """Check with a moderate increase in sample points if any part of the pixel's internal area is inside the polygon."""
    samples_fraction = [i/20 for i in range(1, 20)]
    samples = [(x + frac, y - frac2) for frac in samples_fraction for frac2 in samples_fraction]
    
    return any(is_inside_polygon(sample, polygon) for sample in samples)

def modified_scan_line_fill_v18(polygon, grid_resolution):
    # Find Ymin and Ymax
    Ymin = min(polygon, key=lambda t: t[1])[1]
    Ymax = max(polygon, key=lambda t: t[1])[1]
    
    filled_pixels = []
    boundary_pixels = []

    # For each scan line from Ymin to Ymax
    for y in range(Ymin, Ymax + 1):
        for x in range(grid_resolution):
            pixel_vertices_inside = pixel_partially_or_fully_inside_polygon(x, y, polygon)
            pixel_area_inside = pixel_area_inside_polygon_v6(x, y, polygon)
            
            if pixel_vertices_inside and pixel_area_inside:
                all_vertices = [
                    (x, y),
                    (x+1, y),
                    (x, y-1),
                    (x+1, y-1)
                ]
                
                # Check if all vertices of the pixel are inside the polygon or on its edge
                if all(is_inside_polygon(vertex, polygon) or is_on_polygon_edge(vertex, polygon) for vertex in all_vertices):
                    filled_pixels.append((x, y))
                else:
                    boundary_pixels.append((x, y))
            elif pixel_area_inside:  # If pixel area is inside but not all vertices are
                boundary_pixels.append((x, y))

    return filled_pixels, boundary_pixels

def plot_scan_line_fill_v16(filled_pixels, boundary_pixels, polygon, grid_resolution):
    """Plot the scan-line fill results."""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')

    # Plot the grid
    for x in range(grid_resolution):
        ax.axhline(x, color='grey', linewidth=0.5)
        ax.axvline(x, color='grey', linewidth=0.5)

    # Plot the polygon
    polygon_x = [point[0] for point in polygon] + [polygon[0][0]]  # Closing the loop
    polygon_y = [point[1] for point in polygon] + [polygon[0][1]]  # Closing the loop
    ax.plot(polygon_x, polygon_y, color='blue')

    # Fill the pixels that are fully inside the polygon
    for pixel in filled_pixels:
        rect = patches.Rectangle((pixel[0], pixel[1]-1), 1, 1, edgecolor='none', facecolor='red')
        ax.add_patch(rect)

    # Fill the boundary pixels
    for pixel in boundary_pixels:
        rect = patches.Rectangle((pixel[0], pixel[1]-1), 1, 1, edgecolor='none', facecolor='orange')
        ax.add_patch(rect)

    # Set limits and show the plot
    ax.set_xlim(0, grid_resolution)
    ax.set_ylim(0, grid_resolution)
    ax.set_title("Modified Scan-Line Fill Algorithm (Version 18) Demonstration")
    plt.show()

# To run the code and visualize the results, execute:
if __name__ == '__main__':
    filled_pixels_v18, boundary_pixels_v18 = modified_scan_line_fill_v18(polygon_complex, grid_resolution)
    print(filled_pixels_v18)
    print("=========")
    print(boundary_pixels_v18)
    plot_scan_line_fill_v16(filled_pixels_v18, boundary_pixels_v18, polygon_complex, grid_resolution)

