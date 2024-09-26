# Project Automation Script for Agisoft Metashape

**Author**: Jan Ziegler  
**Date**: September 2024

## Overview

The script automates several stages of photogrammetry processing in Agisoft Metashape, including:

- Camera alignment
- Gradual selection of tie points based on reprojection error
- Depth map and dense point cloud generation
- DEM and orthomosaic generation
- DTM creation from classified ground points
- Raster transformations and final report export

The script is designed to streamline the processing of multiple projects (but can also be run for single projects) while maintaining consistent output formats.

## Prerequisites

Before running this script, certain steps must be completed in Agisoft Metashape. This guide explains how to correctly set up your project and prepare it for processing.

### 1. Load Images into Metashape

1. **Start a New Project**:
   - Open Agisoft Metashape and create a new project.
   - Go to **Workflow > Add Photos** to load the images that you want to process.

2. **Check Image Alignment**:
   - Ensure all images are properly loaded and contain the necessary metadata (such as RTK data if applicable).

### 2. Save the Project and Chunk with a Specific Naming Convention

1. **Save the Project**:
   - Save the project using the following naming convention:
     ```
     YYYYMMDD_site_name.psx
     ```
     Where:
     - `YYYYMMDD`: The date of the project.
     - `site_name`: A descriptive name for the project site.

   Example:  
   ```
   20240901_lens.psx
   ```

2. **Name the Chunk**:
   - Each project should have at least one chunk.
   - Rename the chunk using the same naming convention as the project:
     ```
     YYYYMMDD_site_name
     ```

   Example:
   ```
   20240901_lens
   ```

### 3. Adjust Image Settings

1. **Set Primary Channel to Panchro (Band 3)**:
   - Go to **Tools > Set Primary Channel**.
   - Select **Panchro (Band 3)** as the primary channel to ensure you're working with the correct wavelength.

2. **Adjust Image Brightness**:
   - Adjust the image brightness if necessary by selecting **Tools > Set Brightness...**. Click **Estimate and Apply**
   - Ensure the images are not too dark or too bright, as this can affect the final outputs.

### 4. Calibrate Reflectance

1. **Calibrate Reflectance**:
   - Go to **Tools > Calibrate Reflectance**.
   - Press locate panels. If the panels are not automatically recognized, follow the instructions for manual panel detection in the Appendix [here](https://agisoft.freshdesk.com/support/solutions/articles/31000148381-micasense-altum-processing-workflow-including-reflectance-calibration-in-agisoft-metashape-professi) 

### 5. Save the Project Again

Once the above settings are applied, save the project one more time before running the Python script.

---

## Running the Script

Once the pre-processing steps are complete, the project can be processed using the Python script. The script automates various steps, including camera alignment, depth map generation, DEM, and DTM exports.

1. **Prepare the Environment**:
   - Make sure you have a Python environment with the Agisoft Metashape API installed.
   
2. **Clone the Repository**:
   - Clone the repository containing the script:
     ```
     git clone https://github.com/yourusername/repository-name.git
     ```
   
3. **Run the Script**:
   - Execute the script in the terminal by specifying the path to the text file containing the project paths:
     ```
     python metashape_script.py project_paths.txt
     ```

   The text file (`project_paths.txt`) should contain the paths of all the `.psx` project files, each on a new line. Example:
   ```
   /path/to/20240901_lens.psx
   /path/to/20240902_saillon.psx
   ```

4. **Outputs**:
   - After the script runs, you will find the following outputs in the `exports` directory for each project:
     - **DEM** (`YYYYMMDD_site_name_DEM.tif`)
     - **Orthomosaic** (`YYYYMMDD_site_name_Ortho.tif`)
     - **DTM** (`YYYYMMDD_site_name_DTM.tif`)
     - **Processing report** (`YYYYMMDD_site_name_report.pdf`)

---

## Notes

- **GPU Settings**: Ensure that your system has GPU enabled for faster processing. The script includes settings to leverage GPU acceleration for depth map generation.
- **Error Handling**: If the script encounters any errors, check the terminal output to diagnose issues with the input project files or settings.
  
Feel free to contribute to this repository by submitting pull requests or opening issues for feature requests or bug reports.

---

This guide ensures that the project is correctly set up before running the Python script, following consistent naming conventions and adjusting key settings in Metashape.
