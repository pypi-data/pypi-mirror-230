import matplotlib
import numpy as np

def colorize_raster(raster, colors=["black", "black", "darkgreen"]):
    raster = raster.squeeze(axis=0)
    cmap = matplotlib.colors.ListedColormap(colors) # this is an object from matplotlib
    norm = matplotlib.colors.Normalize(vmin=np.min(raster), vmax=np.max(raster)) # this is a function from matplotlib
    colored_image = cmap(norm(raster))
    return colored_image