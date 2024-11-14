import Metashape
import os
import argparse
import tqdm

def process_multiple_projects_from_file(filepath):
   print(f"Reading project paths from file: {filepath}")
   with open(filepath, 'r') as file:
      project_paths = [line.strip() for line in file.readlines()]
   print(f"Found {len(project_paths)} project paths.")
   return project_paths

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

def main():
   parser = argparse.ArgumentParser(description="Clear storage space of Metashape projects.")
   parser.add_argument('project_paths', type=str, help='Path to the text file containing Metashape project paths.')
   args = parser.parse_args()

   print("Starting the storage clearing process.")
   project_paths = process_multiple_projects_from_file(args.project_paths)
   for project_path in project_paths:
      clear_storage_space(project_path)
   print("Storage clearing process completed.")
   for project_path in tqdm.tqdm(project_paths, desc="Clearing storage space"):
      clear_storage_space(project_path)

if __name__ == "__main__":
   main()


