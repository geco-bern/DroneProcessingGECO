import Metashape
import os
import argparse
import subprocess
import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(project_path, log_dir):
    """Configure logging to file and console"""
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # File handler
    log_file = os.path.join(log_dir, f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)  # Ensure the parent directory exists
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return log_file


def process_project_preprocessing(project_path):
    # Open the existing project
    doc = Metashape.Document()
    doc.open(project_path, ignore_lock=True)

    # Define the base directory for output files (relative paths)
    base_dir = os.path.dirname(project_path)
    export_dir = os.path.join(base_dir, "exports")
    log_dir = os.path.join(base_dir, "logs")
    reference_dir = os.path.join(base_dir, "references")
    if not os.path.exists(reference_dir):
        os.makedirs(reference_dir)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"processing_log_{current_time}.log")
    setup_logging(log_file_path, log_dir)

    # Set the chunk (assuming single chunk processing, but can be modified for multiple)
    chunk = doc.chunk

    # Set the coordinate system (EPSG::4326 - WGS 84) or another desired coordinate system
    coord_system = Metashape.CoordinateSystem("EPSG::4326")
    chunk.crs = coord_system

    # Create OrthoProjection object using the same coordinate system
    ortho_proj = Metashape.OrthoProjection()
    ortho_proj.crs = coord_system

    # Set the image compression for exports
    compression = Metashape.ImageCompression()
    compression.tiff_compression = Metashape.ImageCompression.TiffCompressionLZW
    compression.jpeg_quality = 99
    compression.tiff_big = True
    compression.tiff_overviews = True
    compression.tiff_tiled = True

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
    
    # Set the primary channel to Panchro band
    panchro_band_found = False
    for s in chunk.sensors:
        if "Panchro" in s.label:
            print(f"Setting primary channel to {s.label}")
            logging.info(f"Setting primary channel to {s.label}")
            chunk.primary_channel = s.layer_index
            panchro_band_found = True
            break

    if not panchro_band_found:
        print("Error: Panchro band not found in the sensor labels.")
        logging.error("Panchro band not found in the sensor labels.")
        raise ValueError("Panchro band not found in the sensor labels.")



    alignment_done = Path(reference_dir) / "CamerasAligned.txt"
    if not alignment_done.exists():
        print("Aligning cameras...")
        logging.info("Aligning cameras...")
        chunk.matchPhotos(
            downscale=1,
            generic_preselection=True,
            reference_preselection=True,
            reference_preselection_mode=Metashape.ReferencePreselectionSource,
            tiepoint_limit=10000,
            reset_matches=True
        )
        chunk.alignCameras(reset_alignment=True)
        doc.save()
        
        # Mark alignment as done
        alignment_done.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        with open(alignment_done, 'w') as done_file:
            done_file.write("Alignment of Multispectral Images step completed.\n")
    else:
        print("Alignment already completed. Skipping...")
        logging.info("Alignment already completed. Skipping...")

    doc.save()

    # Gradual selection based on reprojection error
    print("Gradual selection for reprojection error...")
    f = Metashape.TiePoints.Filter()
    threshold = 0.5
    f.init(chunk, criterion=Metashape.TiePoints.Filter.ReprojectionError)
    f.removePoints(threshold)
    doc.save()

    # Optimize camera alignment by adjusting intrinsic parameters
    print("Optimizing camera alignment...")
    chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True, adaptive_fitting=False)
    doc.save()

    # Build Depth Maps and Dense Point Cloud
    if not chunk.depth_maps:
        print("Building Depth Maps...")
        chunk.buildDepthMaps(downscale=1, filter_mode=Metashape.MildFiltering)
    else:
        print("Depth Maps already exist. Skipping.")

    if not chunk.point_cloud:
        print("Building Point Cloud...")
        chunk.buildPointCloud(source_data=Metashape.DataSource.DepthMapsData, point_colors=True)
    else:
        print("Point Cloud already exists. Skipping.")
    doc.save()

    # Build Model (Redundancy Check)

    print("Building Model...")
    chunk.buildModel(surface_type=Metashape.HeightField, source_data=Metashape.PointCloudData,
                         face_count=Metashape.MediumFaceCount)

    # Decimate and smooth the model to use as an orthorectification surface
    print("Decimating and smoothing the model...")
    chunk.decimateModel(face_count=len(chunk.model.faces) // 2)
    smooth_val = 100   #Example smoothing strength, adjust as needed
    chunk.smoothModel(smooth_val)

    # Build Orthomosaic from the model data
    print("Building Orthomosaic from the model data...")
    chunk.buildOrthomosaic(surface_data=Metashape.ModelData, blending_mode=Metashape.DisabledBlending, projection=ortho_proj)
    ortho_file_model = os.path.join(export_dir, chunk.label + "model_ortho.tif")
    chunk.exportRaster(path=ortho_file_model, source_data=Metashape.OrthomosaicData, image_format=Metashape.ImageFormatTIFF, image_compression=compression, raster_transform=Metashape.RasterTransformValue, projection=ortho_proj)
    doc.save()

    # Build DEM
    print("Building DEM...")
    chunk.buildDem(source_data=Metashape.PointCloudData, interpolation=Metashape.EnabledInterpolation, projection=ortho_proj)
    doc.save()

    # Build Orthomosaic from DEM
    print("Building Orthomosaic from DEM...")
    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData, blending_mode=Metashape.DisabledBlending, projection=ortho_proj)
    doc.save()

    # Export DEM and Orthomosaic
    dem_path = os.path.join(export_dir, chunk.label + "_DEM.tif")
    print(f"Exporting DEM to {dem_path}...")
    chunk.exportRaster(path=dem_path, source_data=Metashape.ElevationData, image_format=Metashape.ImageFormatTIFF, image_compression=compression, projection=ortho_proj)

    ortho_path_DEM = os.path.join(export_dir, chunk.label + "DEM_ortho.tif")
    print(f"Exporting Orthomosaic to {ortho_path_DEM}...")
    chunk.exportRaster(path=ortho_path_DEM, source_data=Metashape.OrthomosaicData, image_format=Metashape.ImageFormatTIFF, image_compression=compression, raster_transform=Metashape.RasterTransformValue, projection=ortho_proj)
    
    # Export the processing report
    report_path = os.path.join(export_dir, chunk.label + "_report.pdf")
    print(f"Exporting processing report to {report_path}...")
    chunk.exportReport(report_path)
    doc.save()
    # Clean up the project flder and get rid of the temporary files (see the ClearinStorageSpace.py script)
    
    #clear_storage_space(project_path)
    
    #doc.save()
    
def clear_storage_space(project_path):
   print(f"Opening project: {project_path}")
   doc = Metashape.Document()
   doc.open(project_path, ignore_lock=True)
   for chunk in doc.chunks:
      if chunk.orthomosaic is not None:
         print(f'Removing orthoPhotos for chunk: {chunk.label}')
         chunk.orthomosaic.removeOrthophotos()
   doc.save()
   print(f"Storage space cleared for project: {project_path}")
def process_multiple_projects(project_paths):
            processed_projects = set()
            for project_path in project_paths:
                if project_path not in processed_projects:
                    process_project_preprocessing(project_path)
                    processed_projects.add(project_path)
def process_multiple_projects_from_file(filepath):
            with open(filepath, 'r') as file:
                project_paths = [line.strip() for line in file.readlines()]
            process_multiple_projects(project_paths)

def main():
            parser = argparse.ArgumentParser(description="Process Metashape projects (Pre-Processing).")
            parser.add_argument('project_paths', type=str, help='Path to the text file containing Metashape project paths.')
            args = parser.parse_args()

            process_multiple_projects_from_file(args.project_paths)

if __name__ == "__main__":
            main()

