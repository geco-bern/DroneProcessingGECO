import os
from pathlib import Path
import datetime

def create_project_structure():
    """
    Prompts the user for site, date, and flight ID, then creates
    the specified hyperspectral project folder structure.
    """
    print("--- Hyperspectral Project Folder Creator ---")
    print("This script will create a standardized folder structure for your flights.")

    # --- 1. Get Main Project Folder (where Site folders will reside) ---
    while True:
        main_project_folder_str = input(
            "\nEnter the path to your MAIN PROJECT FOLDER (e.g., D:\\Hyperspectral_Projects default): "
        ).strip()
        if not main_project_folder_str:
            main_project_folder_str = "D:\\Hyperspectral_Projects"  # Default path if empty !!!! CHANGE THIS TO YOUR DEFAULT PATH
        # Ensure the path is a valid directory
        main_project_path = Path(main_project_folder_str)
        if main_project_path.exists() and main_project_path.is_dir():
            print(f"Using main project folder: {main_project_path}")
            break
        else:
            print(f"Error: '{main_project_folder_str}' is not a valid or existing directory.")
            if input("Attempt to create it? (y/n): ").lower() == 'y':
                try:
                    main_project_path.mkdir(parents=True, exist_ok=True)
                    print(f"Main project folder '{main_project_path}' created.")
                    break
                except Exception as e:
                    print(f"Failed to create main project folder: {e}")
            else:
                print("Please provide a valid main project folder to continue.")


    # --- 2. Get Site Name ---
    site_name = input("\nEnter the SITE NAME (e.g., Saillon, Lens, Bern_S1P1G1 (Thermebodewald Plot1 and Gradient), Bern_S1P2 (Thermebodewald Plot2), Bern_S2P1G1 (Drakau Plot1 and Gradient), Bern_S2P3(Drakau Plot 3)): ").strip()
    if not site_name:
        print("Site name cannot be empty. Exiting.")
        return

    # --- 3. Get Flight Date ---
    while True:
        flight_date_str = input("Enter the FLIGHT DATE (YYYYMMDD, e.g., 20250707): ").strip()
        try:
            # Validate date format
            datetime.datetime.strptime(flight_date_str, '%Y%m%d')
            break
        except ValueError:
            print("Invalid date format. Please use `YYYYMMDD` (e.g., 20250707).")

    # --- 4. Get Flight ID ---
    flight_id = input("Enter the FLIGHT ID (e.g., Flight1, Run_A, leave empty for default 'Flight1'): ").strip()
    if not flight_id:
        flight_id = "Flight1"

    # Construct the flight folder name
    flight_folder_name = f"{flight_date_str}_{flight_id}"

    # --- Define the core structure relative to the flight folder ---
    # This list defines all the subdirectories that will be created
    # within each specific flight folder.
    flight_sub_structure = [
        "01_Raw/HS_Sensor_Data",
        "01_Raw/Applanix_Raw_Data",
        "01_Raw/SWIPOS_Base_Data",
        "02_Processed/Processed_GPS_IMU",
        "02_Processed/DEM",
        "02_Processed/Processed_Images", # This is where ortho.ini and lidar.ini will go
        "03_Results/Analysis_Products",
        "03_Results/Reports_and_Logs",
    ]

    # --- Construct full paths ---
    site_path = main_project_path / site_name
    flight_path = site_path / flight_folder_name

    # --- Create common top-level folders if they don't exist ---
    general_doc_path = main_project_path / "General_Project_Documentation"
    site_doc_path = site_path / "Documentation"

    try:
        general_doc_path.mkdir(parents=True, exist_ok=True)
        print(f"\nEnsured 'General_Project_Documentation' exists at: {general_doc_path}")
    except Exception as e:
        print(f"Warning: Could not ensure 'General_Project_Documentation' exists: {e}")

    try:
        site_doc_path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured '{site_name}/Documentation' exists at: {site_doc_path}")
    except Exception as e:
        print(f"Warning: Could not ensure '{site_name}/Documentation' exists: {e}")


    # --- Create the flight-specific structure ---
    print(f"\nAttempting to create structure for: {flight_path}")
    if flight_path.exists():
        print(f"Warning: Flight folder '{flight_folder_name}' already exists for site '{site_name}'. Skipping creation.")
        print("You might want to choose a different Flight ID if this is a new mission.")
        return

    try:
        # Create the main flight folder
        flight_path.mkdir(parents=True, exist_ok=True) # exist_ok=True handles if site_path already exists

        # Create all subdirectories within the flight folder
        for sub_dir in flight_sub_structure:
            current_dir_path = flight_path / sub_dir
            current_dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {current_dir_path}")

            # Special handling for 'Processed_Images' to create .ini files
            if sub_dir == "02_Processed/Processed_Images":
                # Content for ortho.ini
                ortho_ini_content = """Lens EFL (mm) = 8.02
Ortho Lens EFL (mm) = 8.295
Array Pixel Pitch (um) = 5.86
Alpha (deg) = 0
Beta (deg) = 0
Gamma (deg) = 0
Roll offset (deg) = -0.38
Pitch offset (deg) = 0.2
Yaw offset (deg) = 0
Roll (right positive) = 1
Pitch (front up positive) = 0
Yaw (north-east positive) = 1
Time Offset = 0
Altitude Offset = 0
Col binning = 1
Correct Timestamps = 1
Zero DEM = 0
Invert Columns = 0
Correct Position = 1
saveOnlyLL = 1
usePostProcess = 1
usePPS = 0
OrthoFieldsSensor = 0
OrthoFieldsGpsUnit = 0
geoidCorrection = 0"""
                ortho_ini_file_path = current_dir_path / "ortho.ini"
                try:
                    with open(ortho_ini_file_path, 'w') as f:
                        f.write(ortho_ini_content)
                    print(f"    Created file: {ortho_ini_file_path}")
                except Exception as file_e:
                    print(f"    Warning: Could not create ortho.ini file: {file_e}")

                # Content for lidar.ini
                lidar_ini_content = """[LidarTools]
demInterpolate=true
matchHsData=true
demNoDataValue=-9999
fromSeconds=146.09
toSeconds=151.6
rollOffset=90.17
rollRightPositive=true
pitchOffset=0.084
pitchFrontUpPositive=false
yawOffset=0.244
yawNorthEastPositive=true
gpsOffsetX=0.114
gpsOffsetY=-0.022
gpsOffsetZ=0.037
timeOffset=0
usePostProcessFile=true
usePpsTxtFile=false
saveTimestamps=true
invertLaserAngle=false
laserAngleRotation=0
rotationalOffset=-90
minRotationalAngle=0
maxRotationalAngle=360
minDistance=1
minLaserAngle=-20
maxLaserAngle=20
maxIntensity=128
doubleSpinBoxSpacing=0.25
demOutputValues=mean"""
                lidar_ini_file_path = current_dir_path / "lidar.ini"
                try:
                    with open(lidar_ini_file_path, 'w') as f:
                        f.write(lidar_ini_content)
                    print(f"    Created file: {lidar_ini_file_path}")
                except Exception as file_e:
                    print(f"    Warning: Could not create lidar.ini file: {file_e}")


        print(f"\nSuccessfully created the folder structure for '{site_name}' flight '{flight_folder_name}'!")
        print(f"Root of new flight structure: {flight_path}")

    except Exception as e:
        print(f"\nAn error occurred while creating folders: {e}")
        print("Please check your permissions and the specified paths.")

if __name__ == "__main__":
    create_project_structure()

