import Metashape
import os
import argparse

def process_multiple_projects_from_file(filepath):
   with open(filepath, 'r') as file:
      project_paths = [line.strip() for line in file.readlines()]
   return project_paths

def clear_storage_space(project_path):
   doc = Metashape.Document()
   doc.open(project_path, ignore_lock=True)
   for chunk in doc.chunks:
      if chunk.orthomosaic is not None:
         print('Removing orthoPhotos for: ' + chunk.label)
         chunk.orthomosaic.removeOrthophotos()
   doc.save()

def main():
   parser = argparse.ArgumentParser(description="Clear storage space of Metashape projects.")
   parser.add_argument('project_paths', type=str, help='Path to the text file containing Metashape project paths.')
   args = parser.parse_args()

   project_paths = process_multiple_projects_from_file(args.project_paths)
   for project_path in project_paths:
      clear_storage_space(project_path)

if __name__ == "__main__":
   main()

