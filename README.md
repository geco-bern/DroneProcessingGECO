# Project Automation Script for Agisoft Metashape

**Author**: Jan Ziegler  
**Date**: September 2024

## Overview

The scripts automate several stages of photogrammetry processing in Agisoft Metashape, divided into two steps:

1. **Geco2024AlignDemOrthoExport**: Handles camera alignment, reprojection error filtering, depth map and dense point cloud generation, DEM, and orthomosaic export.
2. **Geco2024GroundPointDTM**: Focuses on classifying ground points and generating the DTM from classified points.

These scripts streamline the processing of multiple projects (but can also be run for single projects), ensuring consistent output formats across various steps.

## Prerequisites

Before running the scripts, certain steps must be completed in Agisoft Metashape. Follow this guide to set up your project and prepare it for automated processing.

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

20240901_lens.psx


2. **Name the Chunk**:
- Each project should have at least one chunk.
- Rename the chunk using the same naming convention as the project:
  ```
  YYYYMMDD_site_name
  ```

Example:

20240901_lens


### 3. Adjust Image Settings

1. **Set Primary Channel to Panchro (Band 3)**:
- Go to **Tools > Set Primary Channel**.
- Select **Panchro (Band 3)** as the primary channel to ensure you're working with the correct wavelength.

2. **Adjust Image Brightness**:
- Adjust the image brightness if necessary by selecting **Tools > Set Brightness...**. Click **Estimate and Apply**.
- Ensure the images are not too dark or too bright, as this can affect the final outputs.

### 4. Calibrate Reflectance

1. **Calibrate Reflectance**:
- Go to **Tools > Calibrate Reflectance**.
- Press **Locate Panels**. If the panels are not automatically recognized, follow the instructions for manual panel detection in the Appendix [here](https://agisoft.freshdesk.com/support/solutions/articles/31000148381-micasense-altum-processing-workflow-including-reflectance-calibration-in-agisoft-metashape-professi).

The values should look like this (sometimes you have to paste the value for Panchro manually to get the correct calibration):
Blue		0.507825
Green		0.509237
Panchro	0.508196
Red		0.509254
Red edge	0.508659
NIR		0.506765
LWIR	


### 5. Save the Project Again

Once the above settings are applied, save the project one more time before running the Python script.

---

## Running the Scripts

### 1. **Geco2024AlignDemOrthoExport**: Pre-Processing (Camera Alignment, DEM, and Orthomosaic)

This script will handle camera alignment, depth map and dense point cloud generation, DEM, and orthomosaic export.

1. **Prepare the Environment**:
   - Ensure you have a Python environment with the Agisoft Metashape API installed.

2. **Clone the Repository**:
   - Clone the repository containing the script:
     ```bash
     git clone https://github.com/yourusername/repository-name.git
     ```

3. **Run the Pre-Processing Script**:
   - Execute the script in the terminal by specifying the path to the text file containing the project paths:
     ```bash
     python Geco2024AlignDemOrthoExport.py project_paths.txt
     ```

   The text file (`project_paths.txt`) should contain the paths of all the `.psx` project files, each on a new line. Example:

/path/to/20240901_lens.psx /path/to/20240902_saillon.psx

yaml


4. **Outputs of the Pre-Processing Script**:
- After the pre-processing script runs, you will find the following outputs in the `exports` directory for each project:
  - **DEM** (`YYYYMMDD_site_name_DEM.tif`)
  - **Orthomosaic** (`YYYYMMDD_site_name_Ortho.tif`)
  - The script skips ground point classification and DTM generation.

---

### 2. **Geco2024GroundPointDTM**: Ground Point Classification and DTM Generation

This script will handle the classification of ground points and generate the DTM from classified points.

1. **Run the Ground Point Classification and DTM Script**:
- After the pre-processing script has been run, execute the second script to classify ground points and generate the DTM:
  ```bash
  python Geco2024GroundPointDTM.py project_paths.txt
  ```

2. **Outputs of the Ground Point Classification and DTM Script**:
- After this script runs, you will find the following additional outputs in the `exports` directory for each project:
  - **DTM** (`YYYYMMDD_site_name_DTM.tif`)
  - **Processing report** (`YYYYMMDD_site_name_report.pdf`)

---

## Notes

- **GPU Settings**: Ensure that your system has GPU enabled for faster processing. The scripts include settings to leverage GPU acceleration for depth map generation.
- **Error Handling**: If the script encounters any errors, check the terminal output to diagnose issues with the input project files or settings.

Feel free to contribute to this repository by submitting pull requests or opening issues for feature requests or bug reports.

---

This guide ensures that the project is correctly set up before running the two Python scripts, following consistent naming conventions and adjusting key settings in Metashape.
