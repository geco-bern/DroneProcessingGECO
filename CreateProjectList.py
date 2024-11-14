import os
import Metashape


def find_metashape_projects(directory, extension=".psx"):
    metashape_projects = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                metashape_projects.append(os.path.join(root, file))
    return metashape_projects

if __name__ == "__main__":
    directory = "/data/scratch/jaziegler/testProjects"  # Replace with your directory path
    projects = find_metashape_projects(directory)
    for project in projects:
        print(project)
        
    def has_orthomosaic(project_path):
        doc = Metashape.Document()
        doc.open(project_path, ignore_lock=True)
        for chunk in doc.chunks:
            if chunk.orthomosaic is not None:
                return True
        return False
    
    def write_projects_to_file(projects, filename):
        with open(filename, 'w') as file:
            for project in projects:
                file.write(f"{project}\n")

        projects_with_orthomosaic = []
        projects_without_orthomosaic = []

        for project in projects:
            if has_orthomosaic(project):
                projects_with_orthomosaic.append(project)
            else:
                projects_without_orthomosaic.append(project)


        write_projects_to_file(projects_with_orthomosaic, "projects_with_orthomosaic.txt")
        write_projects_to_file(projects_without_orthomosaic, "projects_without_orthomosaic.txt")