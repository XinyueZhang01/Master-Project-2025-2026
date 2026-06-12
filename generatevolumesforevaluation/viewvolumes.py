import numpy as np
import pyvista as pv

vol = np.load('D:/BaiduNetdiskDownload/generatevolumes/volumes_3d_v4/fail/volume_fail_003.npy')

grid = pv.ImageData()
grid.dimensions = np.array(vol.shape) + 1
grid.cell_data["values"] = vol.flatten(order="F")

plotter = pv.Plotter()
plotter.add_mesh(
    grid.threshold(0.5),
    show_edges=False
)
plotter.show()