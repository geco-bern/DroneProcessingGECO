####THIS IS JUST A CODE SNIPPET TO CLEAR THE STORAGE SPACE OF METASHAPE PROJECTS

doc = Metashape.app.document

for chunk on doc.chunks:
   if chunk.orthomosaic is not None:
      print('Removing orthoPhotos for: ' + chunk.label)
      chunk.orthomosaic.removeOrthophotos()
