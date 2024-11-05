'''
==VDP_GUI Main script==
Allows the user to scroll through defect thresholds on HPG ventilation images to 
visually select best defect distribution. You can select a 'rating' for your final
defect images from Terrible to Excellent, and you can make cases with common issues
(low SNR, artifacts, coil shading, etc.). You can also enter any notes you'd like in
the text box. Once a rating is selected, the window data including the chosen threshold
and VDP are saved in an xlsx file which is either created (first run) or opened
if it already exists - so you can stop at anytime and come back without losing results.
INPUTS:
The program reads data from a folder 'Niftis' which is contained wihin the same parent
folder as the running script or executable. These Niftis each contain a 4D numeric array
of dimension [rows, columns, slices, dataset] where dataset = 0 is the raw HPG ventilation,
dataset = 1 is the binary mask, and dataset = 2 is the N4 bias corrected image set
OUTPUTS:
The program creates an xlsx which is populated with the results of each dataset analysis.
The xlsx is created if it doesn't exist or is empty. If it does exist, the code checks for
which cells are populated from previous runs and begins the analysis script at the next
available row. That way you can close the program at anytime and not lost progress - it 
will just open up where you left off.

First version, 1/20/2024, RP Thomen (thomenr@health.missouri.edu)
Latest version, 3/26/2024, RPT
Please send feedback!
'''

import os
import random
import time
import numpy as np
import PySimpleGUI as sg
import GUIhelperzz as gui


## -- This will check if the program is 'frozen' (compiled into exe by pyistaller) or just run as python code
## -- The data folder 'Niftis' needs to be in the same directory as the exe
parent_dir = gui.get_executable_directory()
print(f"The executable is located in: {parent_dir}")
os.chdir(parent_dir)
dataFolder = os.path.join(parent_dir,'Niftis\\') 

## -- Results will be organized into an xlsx file
XLname = 'XenonGuiResults.xlsx'

## -- If the file already exists, we want to open it and pickup where we left off. Otherwise we will create it.
workbook, xlsx_filePath = gui.open_or_create_excel_file(parent_dir, XLname)
worksheet = workbook[workbook.sheetnames[0]]

## -- Check the 'B' column of XL file for an empty cell. We'll start here
startCase=1
while worksheet['C'][startCase].value is not None:
    startCase += 1

totalCases = len(worksheet['A'])
print(f'You are on case {startCase} out of {totalCases}')

## -- Pull column A from XL as the fileList
fileList = [worksheet['A'][k].value for k in range(len(worksheet['A']))]

## -- Column B stores a 1 or 0 indicating whether raw or N4 data is to be displayed
N4view = [worksheet['B'][k].value for k in range(len(worksheet['B']))]

## -- For loop goes through each case in the worksheet starting at the first blank case
for k in range(startCase,len(worksheet['A'])):

    # Start a timer
    case_start_time = time.time()
    print(f'Opening case {k}, {fileList[k]}')

    ## -- The data are stored in Nifti format as 4D arrays of dimension [rows, columns, slices, set]
    ## -- The 'set' is 0 = raw ventilation images, 1 = binary mask, 2 = N4bias corrected images
    nii_data, _, _ = gui.load_Nifti_file(f"{dataFolder}{fileList[k]}")

    ## -- The HPG class stores all analysis/display attributes (check the GUIhelperzz file for explanation)
    HPG1 = gui.HPG(nii_data[:,:,:,0],nii_data[:,:,:,1],nii_data[:,:,:,2])

    HPG1.HPtoMontage(useBias=N4view[k])
    sliceRange = 4

    ## -- Build the GUI using the PySimpleGUI module -- ##
    sg.theme('black')
    input_column = [
        [sg.Button('Toggle Mask Border',key='mask_border')],
        [sg.Text('Defect Identification Quality: '),
         sg.Radio('Terrible','quality',key='quality1'),
         sg.Radio('Bad','quality',key='quality2'),
         sg.Radio('OK','quality',key='quality3'),
         sg.Radio('Good','quality',key='quality4'),
         sg.Radio('Excellent','quality',key='quality5')],
        [sg.Text(f"Your VDP Estimate:"),sg.InputText(size=(5,1),key='vdp')],
        [sg.Text(f"Guess the Disease:"),sg.Radio('Healthy','disease',key='healthy'),sg.Radio('Asthma','disease',key='asthma'),sg.Radio('CF','disease',key='CF'),sg.Radio('COPD','disease',key='COPD')],
        [sg.Text(f"Disease Severity:   "),sg.Radio('None','severity',key='sev0'),sg.Radio('Mild','severity',key='sev1'),sg.Radio('Moderate','severity',key='sev2'),sg.Radio('Severe','severity',key='sev3')]]
    artifacts_column = [[sg.Checkbox("Artifacts",default=False,key='c1',pad=(0,0))],
        [sg.Checkbox("Coil Shading",default=False,key='c2',pad=(0,0))],
        [sg.Checkbox("Segmentation Errors",default=False,key='c3',pad=(0,0))],
        [sg.Checkbox("Low SNR",default=False,key='c4',pad=(0,0))],
        [sg.Checkbox("Slices need different thresholds",default=False,key='c5',pad=(0,0))],
        [sg.Checkbox("Defects in vasculature",default=False,key='c6',pad=(0,0))],
        [sg.Checkbox("Partial Voluming",default=False,key='c7',pad=(0,0))]]
    layout = [
        [sg.Image(key='-RAWIMAGE-')],
        [sg.Image(key='-DEFECTIMAGE-')],
        [sg.Image(key='-FILLIMAGE-',visible=False)],
        [sg.Slider(range=(sliceRange, HPG1.HP.shape[2]-sliceRange), default_value=int(HPG1.HP.shape[2]/2),expand_x=True, enable_events=True,orientation='horizontal', key='-SLIDER-')],
        [sg.Column(input_column),sg.VSeperator(),sg.Column(artifacts_column)],
        [sg.Text(f"Notes:"),sg.Input('',enable_events=True,key='notes', font=('Arial Bold', 12),size = (100,1), justification='left')],
        [sg.Button('Save and Load Next Subject',key='-done-')]
    ]
    window = sg.Window('Window Title', layout, return_keyboard_events=True, margins=(0, 0), finalize=True, size= (2400,700), resizable=True, element_justification='c')

    # the slider is initialized to the middle slice of the dataset
    slider_value = int(HPG1.HP.shape[2]/2)
    nCol = int(HPG1.HP.shape[1]) 

    # - We need some initial threshold to calculate the defectArray. Let's randomize this between 40 and 100.
    # - This will help us avoid 'anchoring' bias in the results
    initThreshold = random.randint(40, 100)
    threshold = initThreshold
    HPG1.calculateDefectArray(threshold/100)

    ## -- These helper functions simply update the 3 display windows
    showBorder = False
    gui.drawArray(window,HPG1.HPmontage,nCol,slider_value, sliceRange,'-RAWIMAGE-')
    gui.drawArray(window,HPG1.defectMontage(border=showBorder),nCol,slider_value, sliceRange,'-DEFECTIMAGE-')
    #gui.drawArray(window,HPG1.borderMontage(),nCol,slider_value, sliceRange,'-FILLIMAGE-')


    while True:
        event, values = window.read() # read the window values
        #print(event, values) # helpful for debugging to print any events/values

        # if the GUI window is closed we break the While loop
        # the For loop continues, but without a button press will experience a TypeError in the worksheet assignments below and kill the app
        # (...not the cleanest approach but works!)
        if event == sg.WIN_CLOSED:
            break
        
        # - Scroll-up events increase the threshold by 1, recalculate the defectArray, and update the windows
        elif ('mask_border') in event:
            showBorder = not showBorder
            gui.drawArray(window,HPG1.defectMontage(border=showBorder),nCol,slider_value, sliceRange,'-DEFECTIMAGE-')


        elif event in ('MouseWheel:Down', 'Down:40', 'Next:34'):
            threshold-=1
            HPG1.calculateDefectArray(threshold/100)
            gui.drawArray(window,HPG1.defectMontage(border=showBorder),nCol,slider_value, sliceRange,'-DEFECTIMAGE-')
            #gui.drawArray(window,HPG1.borderMontage(),nCol,slider_value, sliceRange,'-FILLIMAGE-')
            #window['vdp'].update(f"Current VDP: {HPG1.VDP}") # can have the window update the VDP if you want

        # - Scroll-down events decrease the threshold by 1, recalculate the defectArray, and update the windows
        elif event in ('MouseWheel:Up', 'Up:38', 'Prior:33'):
            threshold+=1
            HPG1.calculateDefectArray(threshold/100)
            gui.drawArray(window,HPG1.defectMontage(border=showBorder),nCol,slider_value, sliceRange,'-DEFECTIMAGE-')
            #gui.drawArray(window,HPG1.borderMontage(),nCol,slider_value, sliceRange,'-FILLIMAGE-')
            #window['vdp'].update(f"Current VDP: {HPG1.VDP}") # can have the window update the VDP if you want

        # - slider events change the slice display range in the window (all 3 windows must be updated here)
        elif event in ('-SLIDER-'):
            slider_value = int(values['-SLIDER-'])
            gui.drawArray(window,HPG1.HPmontage,nCol,slider_value, sliceRange,'-RAWIMAGE-')
            gui.drawArray(window,HPG1.defectMontage(border=showBorder),nCol,slider_value, sliceRange,'-DEFECTIMAGE-')
            #gui.drawArray(window,HPG1.borderMontage(),nCol,slider_value, sliceRange,'-FILLIMAGE-')

        # - a button press assigns a defect quality rank and breaks the while loop
        elif ('-done-') in event:
            break
        else:
            pass

    # - Once out of the for loop we fill the xlsx worksheet and save
    time_to_complete = time.time() - case_start_time
    print(f'This case took you {np.round(time_to_complete)} seconds to review. \n')
    window.close()
    #worksheet.cell(k+1, 9, fileList[k])
    worksheet.cell(k+1, 3, initThreshold)
    worksheet.cell(k+1, 4, threshold)
    worksheet.cell(k+1, 5, HPG1.VDP)
    
    if not values['vdp'] == '':
        worksheet.cell(k+1, 6, int(values['vdp']))

    rank = -1
    if values['quality1']: rank = 1
    if values['quality2']: rank = 2
    if values['quality3']: rank = 3
    if values['quality4']: rank = 4
    if values['quality5']: rank = 5
    worksheet.cell(k+1, 7, rank)

    disease = ''
    if values['healthy']: disease = 'healthy'
    if values['asthma']: disease = 'asthma'
    if values['CF']: disease = 'CF'
    if values['COPD']: disease = 'COPD'
    worksheet.cell(k+1, 8, f'{disease}')

    severity = -1
    if values['sev0']: severity = 0
    if values['sev1']: severity = 1
    if values['sev2']: severity = 2
    if values['sev3']: severity = 3
    worksheet.cell(k+1, 9, int(severity))
    worksheet.cell(k+1, 10, int(values['c1']))
    worksheet.cell(k+1, 11, int(values['c2']))
    worksheet.cell(k+1, 12, int(values['c3']))
    worksheet.cell(k+1, 13, int(values['c4']))
    worksheet.cell(k+1, 14, int(values['c5']))
    worksheet.cell(k+1, 15, int(values['c6']))
    worksheet.cell(k+1, 16, int(values['c7']))
    worksheet.cell(k+1, 17, time_to_complete)
    worksheet.cell(k+1, 18, values['notes'])
    workbook.save(os.path.join(parent_dir, XLname))

# - When all cases are complete close the workbook
workbook.close()
