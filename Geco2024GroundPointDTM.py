import Metashape
import os
import argparse

def process_ground_classification_and_dtm(project_path):
    # Open the existing project
    doc = Metashape.Document()
    doc.open(project_path, ignore_lock=True)

    # Define the base directory for output files (relative paths)
    base_dir = os.path.dirname(project_path)
    export_dir = os.path.join(base_dir, "exports")
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Set the chunk (assuming single chunk processing)
    chunk = doc.chunk

    # Set the coordinate system (EPSG::4326 - WGS 84) or another desired coordinate system
    coord_system = Metashape.CoordinateSystem("EPSG::4326")
    chunk.crs = coord_system

    # Create OrthoProjection object using the same coordinate system
    ortho_proj = Metashape.OrthoProjection()
    ortho_proj.crs = coord_system

    # Classify Ground Points
    print("Classifying Ground Points...")
    chunk.point_cloud.classifyGroundPoints(
        max_angle=40,
        max_distance=2.5,
        max_terrain_slope=35,
        cell_size=20.0,
        erosion_radius=0.5,
        return_number=0,
        keep_existing=False
    )
    doc.save()

    # Build DTM from Classified Ground Points
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
    chunk.exportRaster(path=dtm_path, source_data=Metashape.ElevationData, image_format=Metashape.ImageFormatTIFF, projection=ortho_proj)

    doc.save()

    # Export the processing report
    report_path = os.path.join(export_dir, chunk.label + "_report.pdf")
    print(f"Exporting processing report to {report_path}...")
    chunk.exportReport(report_path)
    doc.save()

def process_multiple_projects(project_paths):
    for project_path in project_paths:
        process_ground_classification_and_dtm(project_path)

def process_multiple_projects_from_file(filepath):
    with open(filepath, 'r') as file:
        project_paths = [line.strip() for line in file.readlines()]
    process_multiple_projects(project_paths)

def main():
    parser = argparse.ArgumentParser(description="Process Ground Classification and DTM for Metashape projects.")
    parser.add_argument('project_paths', type=str, help='Path to the text file containing Metashape project paths.')
    args = parser.parse_args()

    process_multiple_projects_from_file(args.project_paths)

if __name__ == "__main__":
    main()

