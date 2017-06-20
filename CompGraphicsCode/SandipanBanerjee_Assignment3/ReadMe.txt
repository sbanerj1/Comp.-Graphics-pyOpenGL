Steps to run ForceDirectedGraph.py:-

1. Open cmd (command prompt) script
2. Go to the directory location (cd .../SandipanBanerjee_Assignment3)
3. Type 'python ForceDirectedGraph.py' and press Enter
4. Nodes should start taking positions based on the forces acting on them
5. Edges between two nodes have thickness (also attractive force) commensurate of the force value in the data file
6. Collision is detected if center of two nodes are within 0.5 pixels, program automatically shift them a little apart in that case
7. Press 'e' or 'E' to toggle between drawing and undrawing edges
8. Press 'n' or 'N' to toggle between drawing and undrawing nodes
9. Press 'a' or 'A' to toggle between drawing and undrawing the whole graph
10. Press 'g' or 'G' to toggle between drawing only nodes in each group and nodes connected to them
11. Press 'r' or 'R' to restart with nodes having random position
12. Drawing stops after 5000 iterations, usually nodes stabilize within that time

I couldn't implement the dragging of the nodes successfully.