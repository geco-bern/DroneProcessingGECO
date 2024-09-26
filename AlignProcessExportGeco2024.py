import Metashape
import os
import argparse

def process_project(project_path):
    # Open the existing project
    doc: object = Metashape.Document()
    doc.open(project_path, ignore_lock=True)

    # Define the base directory for output files (relative paths)
    base_dir = os.path.dirname(project_path)
    export_dir = os.path.join(base_dir, "exports")
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Set the chunk (assuming single chunk processing, but can be modified for multiple)
    chunk = doc.chunk

    # Set the coordinate system (EPSG::2056 - CH1903+ / LV95)
    # coord_system = Metashape.CoordinateSystem("EPSG::2056")

    # Set the coordinate system (EPSG::4326 - WGS 84)
    coord_system = Metashape.CoordinateSystem("EPSG::4326")
    chunk.crs = coord_system

    # Create OrthoProjection object using the same coordinate system
    ortho_proj = Metashape.OrthoProjection()
    ortho_proj.crs = coord_system

    # Settings GPU enabled

    # Apply Raster Transform
    print("Applying raster transform and exporting...")
    chunk.raster_transform.formula = [
        'B1 * (B3 / (0.2 * B1 + 0.2 * B2 + 0.2 * B4 + 0.2 * B5 + 0.2 * B6)) / 32768',
        'B2 * (B3 / (0.2 * B1 + 0.2 * B2 + 0.2 * B4 + 0.2 * B5 + 0.2 * B6)) / 32768',
        'B4 * (B3 / (0.2 * B1 + 0.2 * B2 + 0.2 * B4 + 0.2 * B5 + 0.2 * B6)) / 32768',
        'B5 * (B3 / (0.2 * B1 + 0.2 * B2 + 0.2 * B4 + 0.2 * B5 + 0.2 * B6)) / 32768',
        'B6 * (B3 / (0.2 * B1 + 0.2 * B2 + 0.2 * B4 + 0.2 * B5 + 0.2 * B6)) / 32768',
        '(B7 / 100) - 273.15'
    ]
    chunk.raster_transform.enabled = True

    # Step 0: Load script to align cameras, filter tie points for reprojection error and calibrate camera

    # Align cameras if not already aligned
    if not chunk.cameras[0].transform:
        print("Aligning cameras...")
        chunk.matchPhotos(downscale=1, keypoint_limit=40000, tiepoint_limit=10000, generic_preselection=True,
                          reference_preselection=True)
        chunk.alignCameras()
    else:
        print("Cameras are already aligned. Skipping.")

    doc.save()

    # Gradual selection based on reprojection error
    print("Gradual selection for reprojection error...")
    f = Metashape.TiePoints.Filter()  # Create filter object
    threshold = 0.5  # Create reprojection error threshold
    f.init(chunk, criterion=Metashape.TiePoints.Filter.ReprojectionError)  # Init with reprojection error criterion
    f.removePoints(threshold)  # Remove points with reprojection error greater than the threshold
    doc.save()

    # Optimize camera alignment by adjusting intrinsic parameters
    print("Optimizing camera alignment...")
    chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True, adaptive_fitting=False)
    doc.save()

    # Step 1: Build Depth Maps and Dense Point Cloud (Redundancy Check)
    if not chunk.depth_maps:
        print("Building Depth Maps...")
        chunk.buildDepthMaps(downscale=1, filter_mode=Metashape.MildFiltering)
    else:
        print("Depth Maps already exist. Skipping.")

    if not chunk.point_cloud:
        print("Building Point Cloud...")
        chunk.buildPointCloud(
            source_data=Metashape.DataSource.DepthMapsData,
            point_colors=True
        )
    else:
        print("Point Cloud already exists. Skipping.")
    doc.save()

    # Step 2: Build DEM (Redundancy Check)
    if not chunk.elevations:
        print("Building DEM...")
        chunk.buildDem(
            source_data=Metashape.PointCloudData,
            interpolation=Metashape.EnabledInterpolation,
            projection=ortho_proj
        )
    else:
        print("DEM already exists. Skipping.")
    doc.save()

    # Step 3: Build Orthomosaic (Redundancy Check)
    if not chunk.orthomosaic:
        print("Building Orthomosaic...")
        chunk.buildOrthomosaic(
            surface_data=Metashape.ElevationData,
            blending_mode=Metashape.DisabledBlending,
            projection=ortho_proj
        )
    else:
        print("Orthomosaic already exists. Skipping.")
    doc.save()

    # Step 4 & 5: Export DEM and Orthomosaic
    if chunk.elevation:
        dem_path = os.path.join(export_dir, chunk.label + "_DEM.tif")
        print(f"Exporting DEM to {dem_path}...")
        chunk.exportRaster(
            path=dem_path,
            source_data=Metashape.ElevationData,
            image_format=Metashape.ImageFormatTIFF,
            projection=ortho_proj
        )

    if chunk.orthomosaic:
        ortho_path = os.path.join(export_dir, chunk.label + "_Ortho.tif")
        print(f"Exporting Orthomosaic to {ortho_path}...")
        chunk.exportRaster(
            path=ortho_path,
            source_data=Metashape.OrthomosaicData,
            image_format=Metashape.ImageFormatTIFF,
            projection=ortho_proj
        )
    doc.save()

    # Step 6: Build DTM from Classified Ground Points
    print("Classifying Ground Points...")
    chunk.point_cloud.classifyGroundPoints(
        max_angle=40,  # Allow steeper slopes
        max_distance=2.5,  # Adjust for vegetation
        max_terrain_slope=35,  # Handle sloped terrain
        cell_size=20.0,  # Smaller grid size for better detail
        erosion_radius=0.5,  # Remove isolated points
        return_number=0,  # Use last return (-1) for LiDAR (or 0 for photogrammetry)
        keep_existing=False  # Reclassify all points
    )
    doc.save()

    print("Building DTM from classified ground points...")
    ground_points = [Metashape.PointClass.Ground]
    chunk.buildDem(
        source_data=Metashape.PointCloudData,
        interpolation=Metashape.EnabledInterpolation,
        projection=ortho_proj,
        classes=ground_points
    )

    dtm_path = os.path.join(export_dir, chunk.label + "_DTM.tif")
    print(f"Exporting DTM to {dtm_path}...")
    chunk.exportRaster(
        path=dtm_path,
        source_data=Metashape.ElevationData,
        image_format=Metashape.ImageFormatTIFF,
        projection=ortho_proj
    )
    doc.save()

    # Export the processing report
    report_path = os.path.join(export_dir, chunk.label + "_report.pdf")
    print(f"Exporting processing report to {report_path}...")
    chunk.exportReport(report_path)
    doc.save()


def process_multiple_projects(project_paths):
    for project_path in project_paths:
        process_project(project_path)


def process_multiple_projects_from_file(filepath):
    """Read project paths from a text file and process each."""
    with open(filepath, 'r') as file:
        project_paths = [line.strip() for line in file.readlines()]
    process_multiple_projects(project_paths)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Process Metashape projects from a text file.")
    parser.add_argument('project_paths', type=str, help='Path to the text file containing Metashape project paths.')
    args = parser.parse_args()

    # Process the projects from the text file
    process_multiple_projects_from_file(args.project_paths)


if __name__ == "__main__":
    main()