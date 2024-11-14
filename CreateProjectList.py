import os
import Metashape


def find_metashape_projects(directory, extension=".psx"):
    print(f"Searching for Metashape projects in directory: {directory}")
    metashape_projects = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                project_path = os.path.join(root, file)
                print(f"Found Metashape project: {project_path}")
                metashape_projects.append(project_path)
    return metashape_projects

if __name__ == "__main__":
    directory = "/data/scratch/jaziegler/testProjects"  # Replace with your directory path
    print(f"Starting search in directory: {directory}")
    projects = find_metashape_projects(directory)
    print(f"Total projects found: {len(projects)}")
    for project in projects:
        print(project)
        
    def has_orthomosaic(project_path):
        print(f"Checking for orthomosaic in project: {project_path}")
        doc = Metashape.Document()
        doc.open(project_path, ignore_lock=True)
        for chunk in doc.chunks:
            if chunk.orthomosaic is not None:
                print(f"Orthomosaic found in project: {project_path}")
                return True
        print(f"No orthomosaic found in project: {project_path}")
        return False
    
    def write_projects_to_file(projects, filename):
        print(f"Writing projects to file: {filename}")
        with open(filename, 'w') as file:
            for project in projects:
                file.write(f"{project}\n")
        print(f"Finished writing projects to file: {filename}")

    projects_with_orthomosaic = []
    projects_without_orthomosaic = []

    for project in projects:
        if has_orthomosaic(project):
            projects_with_orthomosaic.append(project)
        else:
            projects_without_orthomosaic.append(project)

    print(f"Projects with orthomosaic: {len(projects_with_orthomosaic)}")
    print(f"Projects without orthomosaic: {len(projects_without_orthomosaic)}")

    output_dir = directory
    write_projects_to_file(projects_with_orthomosaic, os.path.join(output_dir, "projects_with_orthomosaic.txt"))
    write_projects_to_file(projects_without_orthomosaic, os.path.join(output_dir, "projects_without_orthomosaic.txt"))