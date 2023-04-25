from ij import IJ, ImagePlus, ImageStack
from ij.plugin import Concatenator
from ij.io import FileSaver
from javax.swing import JFrame, JProgressBar
import os
import time

# Record the start time
total_start_time = time.time()

# Set a destination folder where all files related to this project will be stored
destination_folder = "D:/stitching/"
# tiles that are placed into an array in the order of 1-n, name doesn't matter here. It should be in the form of Name.Filetype
tiles = ['tile1_1.tif', 'tile1_2.tif', 'tile1_3.tif', 'tile1_4.tif']

# The folder that contains the original tiles
input_directory = os.path.join(destination_folder, "input")
# The folder that contains the sliced tiles, subfolders will be numbered according to the slice
output_directory = os.path.join(destination_folder, "split")
# The folder that contains the final 3D stack and the stitched slices 
result_directory = os.path.join(destination_folder, "stitched")
# Where the final 3D stack will be
final_result_directory = os.path.join(result_directory, "final_stack")
# Create the input, output, and result folders if they don't exist
for folder in [input_directory, output_directory, result_directory, final_result_directory]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Get the number of slices in the first stack
stack1 = IJ.openImage(os.path.join(input_directory, tiles[0]))
slices = stack1.getStackSize()

# Initialize the final 3D stack
final_stack = None

# Iterate through all the tiles
for i, tile in enumerate(tiles):
    # Open the TIFF stack
    stack = IJ.openImage(os.path.join(input_directory, tile))

    # Iterate through all the slices
    for slice in range(1, 100):
        # Create a subfolder for each slice in the output directory
        slice_folder = os.path.join(output_directory, "slice_{}".format(slice))
        if not os.path.exists(slice_folder):
            os.makedirs(slice_folder)

        # Extract the specific slice from the TIFF stack and save it in the subfolder
        stack.setSlice(slice)
        img = ImagePlus("tile_{}_{}".format(slice, i + 1), stack.getProcessor())
        output_filename = os.path.join(slice_folder, "tile_{}_{}.tif".format(slice, i + 1))
        FileSaver(img).saveAsTiff(output_filename)
 		

# Iterate through all the subfolders to stitch the 4 images in each subfolder
for slice in range(1, 100):
    slice_folder = os.path.join(output_directory, "slice_{}".format(slice))

    # Stitch the 4 images using the Grid/Collection stitching plugin
    stitch_args = "type=[Grid: column-by-column] order=[Defined by TileConfiguration] directory={} output_textfile_name=TileConfiguration.txt file_names=tile_{}_{{i}}.tif grid_size_x=2 grid_size_y=2 tile_overlap=10 fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)]".format(slice_folder, slice)
    IJ.run("Grid/Collection stitching", stitch_args)

    # Save the stitched image to the result folder
    stitched_image = IJ.getImage()
    stitched_filename = os.path.join(result_directory, "stitched_image_{}.tif".format(slice))
    FileSaver(stitched_image).saveAsTiff(stitched_filename)

	# Initialize the final 3D stack with the dimensions of the first stitched image
    if final_stack is None:
        final_stack = ImageStack(stitched_image.getWidth(), stitched_image.getHeight())

    # Add the stitched image to the final 3D stack
    final_stack.addSlice(stitched_image.getProcessor())

    # Close the stitched image
    IJ.run("Close")
	
# Save the final 3D stack
final_image = ImagePlus("Final_Stitched_Stack", final_stack)
final_filename = os.path.join(final_result_directory, "final_stitched_stack.tif")
FileSaver(final_image).saveAsTiffStack(final_filename)
# Record the end time
total_end_time = time.time()
total_time = total_end_time - total_start_time
average_time_per_slice = total_time / slices

print("Total time taken: {:.2f} seconds".format(total_time))
print("Average time per slice: {:.2f} seconds".format(average_time_per_slice))