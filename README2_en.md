# Data preparation

Use meshFix or meshLab or python / c ++ libraries to remove singularities. 

- Merge close vertices
- Remove duplicated faces
- Remove duplicated vertices
- Remove faces from non manifold edges
- Select self intersecting faces -> remove
- Remove zero Area faces
- Remove vertices wrt quality


# Full conversion process to csg
```bash
python run_test.py nameOfTest
`` `

or


```bash
./csg_cpp_command test -n nameOfTest
`` `

then convert to Sketch format you SCAD file


```bash
./csg_cpp_command legacy-sketch-tree -i filePathOfSCAD -o outputPath.txt
`` `


then simplification of the CSGs tree
=> Be careful with the choice of Epsilon
```bash
./csg_cpp_command clean-csg  -e espilonValue -i filePathOfSCAD  -o newFilePathOfSCAD
`` `
```bash
./csg_cpp_command legacy-sketch-tree -i newFilePathOfSCAD -o outputPath.txt
`` `
```bash
python sketch2CSGExperimental.py  inputFileInCSGSketchFormat csgInTreeFormatPath simplifiedSsgInTreeFormatPath geometry.js
`` `

# Converting a solution dataset to node-occ format
`` python sketch2CSGInputFolder.py rootFolderOfCsgCppCommandBinary pathOfSolutionFolder```

# Converting a point cloud to CSG
`` `
micmac TiPunch inputPointCloud.ply
manifold_master -i input.ply -o manifold.ply
convert manifold.ply into off 
eventually filter isolated faces or vertices and remove duplicated faces/vertices with MeshLab
python run.py build manifold
`` `