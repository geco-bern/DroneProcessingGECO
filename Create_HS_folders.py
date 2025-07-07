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
            "\nEnter the path to your MAIN PROJECT FOLDER (e.g., C:\\Hyperspectral_Projects or /home/user/hyperspectral): "
        ).strip()
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
    site_name = input("\nEnter the SITE NAME (e.g., Saillon, Lens): ").strip()
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
            print("Invalid date format. Please use YYYYMMDD (e.g., 20250707).")

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
        "02_Processed/Processed_Images",
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
            (flight_path / sub_dir).mkdir(parents=True, exist_ok=True)
            print(f"  Created: {flight_path / sub_dir}")

        print(f"\nSuccessfully created the folder structure for '{site_name}' flight '{flight_folder_name}'!")
        print(f"Root of new flight structure: {flight_path}")

    except Exception as e:
        print(f"\nAn error occurred while creating folders: {e}")
        print("Please check your permissions and the specified paths.")

if __name__ == "__main__":
    create_project_structure()