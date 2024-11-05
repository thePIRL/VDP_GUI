# VDP_GUI
Code for user defined thresholding for VDP of HPG ventilation images.\
Feedback welcome!

## Questions/Hypotheses this code hopes to address
 - When given control over the defect theshold, what value are radiologists likely to select based on visual defect inspection alone?
 - How reproducible is the selected threshold?
 - How variable is the selected threshold among different observers? Radiologists? Physicists?
 - Does N4 bias correction affect this threshold?
 - Of the commonly defined thresholds in literature (mean-anchored, linear binning, kmeans, etc.), which does visual inspection by radiologists most closely align with?
 - How much does the disease state affect selection reproducibility?
 - How much does N4 correction/artifacts/coil shading/etc affect confidence in selected threshold?

## Version info and requirements
Version 240121_RPT, 1/21/2024, RP Thomen (thomenr@health.missouri.edu)\
Compiled with python 3.9.2\
matplotlib==3.7.2\
nibabel==5.2.0\
numpy==1.24.4\
openpyxl==3.1.2\
Pillow==10.2.0\
PySimpleGUI==4.60.5\
scipy==1.12.0\
SimpleITK==2.3.1\
skimage==0.0

## File Info
### VDP_GUI.exe
I used the PyInstaller module to compile the full code into an executable. This should run on any windows machine, all you need is to make sure there's a folder called 'Niftis' containing your 4D data arrays in the same path as the exe. Note that if you're on a computer supplied by your institution, running an exe is likely forbidded by your IT security (mine sure is, and I even have admin privileges). In this case, just run the VDP_GUI.py using your favorite python interpreter.

### VDP_GUI.py 
This is the main script of the  Allows the user to scroll through defect thresholds on HPG ventilation images to visually select best defect distribution. You can select a 'rating' for your finaldefect images from Terrible to Excellent, and you can make cases with common issues (low SNR, artifacts, coil shading, etc.). You can also enter any notes you'd like in the text box. Once a rating is selected, the window data including the chosen threshold and VDP are saved in an xlsx file which is either created (first run) or opened if it already exists - so you can stop at anytime and come back without losing results.
 - INPUTS:
The program reads data from a folder 'Niftis' which is contained wihin the same parent folder as the running script or executable. These Niftis each contain a 4D numeric array of dimension [rows, columns, slices, dataset] where dataset = 0 is the raw HPG ventilation,  dataset = 1 is the binary mask, and dataset = 2 is the N4 bias corrected image set
 - OUTPUTS:
The program creates an xlsx which is populated with the results of each dataset analysis. The xlsx is created if it doesn't exist or is empty. If it does exist, the code checks for which cells are populated from previous runs and begins the analysis script at the next available row. That way you can close the program at anytime and not lost progress - it will just open up where you left off.

### GUIhelperzz.py
This includes all the helper function for VDP_GUI.py and the HPG class structure

### Add N4correction to Niftis.py
This script is what I used to calculate the N4 bias corrected images for each HPG vent dataset and combine them into 1 4D array (raw HPG ventilation images, masks, N4bias corrected vent images). Not used as part of the main script

### Niftis
This directory should contain all the datasets you wish to examine in Nifti format as 4Darrays (described above and in the file comments)