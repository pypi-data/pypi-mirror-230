import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
import os


def create_custom_grid(input_shapefile, output_folder, num_rows, num_cols):
    # Read the input shapefile
    gdf = gpd.read_file(input_shapefile)

    # Calculate the bounding box of the input shapefile
    bounds = gdf.total_bounds

    # Calculate the grid cell size based on the number of rows and columns
    grid_size_x = (bounds[2] - bounds[0]) / num_cols
    grid_size_y = (bounds[3] - bounds[1]) / num_rows

    # Create a list to hold the grid polygons
    grid_polygons = []

    # Create the grid polygons based on the custom number of rows and columns
    for row in range(num_rows):
        for col in range(num_cols):
            xmin = bounds[0] + col * grid_size_x
            xmax = xmin + grid_size_x
            ymin = bounds[1] + row * grid_size_y
            ymax = ymin + grid_size_y
            polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])

            # Check if the grid cell intersects with the input shapefile
            if any(polygon.intersects(geom) for geom in gdf.geometry):
                grid_polygons.append(polygon)

    # Create a GeoDataFrame for the grid
    grid_gdf = gpd.GeoDataFrame({'geometry': grid_polygons})

    # Save the grid as a shapefile
    grid_shapefile = os.path.join(output_folder, "grid.shp")
    grid_gdf.to_file(grid_shapefile, driver='ESRI Shapefile')

    return grid_shapefile


def spatially_split_shapefile(input_shapefile, grid_shapefile, output_folder, threshold):
    # Read the input shapefile
    gdf = gpd.read_file(input_shapefile)

    # Read the grid shapefile
    grid_gdf = gpd.read_file(grid_shapefile)

    # Spatially split the input shapefile based on the grid
    for i, grid_polygon in enumerate(grid_gdf.geometry):
        # Create an empty list to store selected geometries
        selected_geometries = []

        # Iterate through the polygons and select the ones that intersect with the current grid cell
        for j, polygon in gdf.iterrows():
            if polygon.geometry.centroid.intersects(grid_polygon):
                selected_geometries.append(polygon.geometry)

        # Merge the selected geometries into a single geometry (if multiple)
        if len(selected_geometries) > 1:
            merged_geometry = cascaded_union(selected_geometries)
        elif len(selected_geometries) == 1:
            merged_geometry = selected_geometries[0]
        else:
            continue  # No selected geometries for this cell, skip it

        # Create a GeoDataFrame with the merged geometry
        selection = gpd.GeoDataFrame({'geometry': [merged_geometry]})

        # Save the selection as a new shapefile only if it's not empty
        if not selection.empty:
            output_shapefile = os.path.join(output_folder, f"chunk_{i}_{threshold}.shp")
            selection.to_file(output_shapefile, driver='ESRI Shapefile')

if __name__ == "__main__":
    input_shapefile = r"C:\Users\pfefer\Documents\Acre\SHP_zone\plots_tmp.shp"  # Replace with your input shapefile
    output_folder = r"C:\Users\pfefer\Documents\test"  # Specify the output folder
    num_rows = 5  # Number of rows in the grid
    num_cols = 5  # Number of columns in the grid

    # Step 1: Create the custom grid
    grid_shapefile = create_custom_grid(input_shapefile, output_folder, num_rows, num_cols)

    # Step 2: Spatially split the shapefile based on the grid
    spatially_split_shapefile(input_shapefile, grid_shapefile, output_folder, 'low')

for tc in ['high', 'low']:
    input_shapefile = r"C:\Users\pfefer\Documents\Acre\SHP_zone\plots_tmp.shp"  # Replace with your input shapefile
    output_folder = r"C:\Users\pfefer\Documents\test"  # Specify the output folder
    num_rows = 5  # Number of rows in the grid
    num_cols = 5  # Number of columns in the grid
    grid_shapefile = create_custom_grid(input_shapefile, output_folder, num_rows, num_cols)

    # Step 2: Spatially split the shapefile based on the grid
    spatially_split_shapefile(input_shapefile, grid_shapefile, output_folder, 'low')
