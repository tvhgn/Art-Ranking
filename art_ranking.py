#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
Created on	05/30 09:21:50 2024

@Author  :   Tom van Hogen 
'''


from psychopy import visual, event, gui, core
from datetime import datetime
from random import shuffle
import csv
import os
import time

# Custom functions
# Draw the grid of images and text boxes
def draw_grid():
    instruction.draw()
    for image, text_box in zip(images, text_boxes):
        image.draw()     
        text_box.draw()
        
# Validation function for text boxes
def validate_input(input_text):
    try:
        num = int(input_text)
        if 1 <= num <= 36:
            return True
        else:
            return False
    except ValueError:
        return False
    
def validate_textboxes(textboxes):
    for textbox in textboxes:
        if textbox.hasFocus and not validate_input(textbox.text):
            textbox.reset()
            
def focus_painting(mouseObject, paintings, window, textboxes):
    # Parameters for enlarged painting
    new_size = (1.5, 1.5)
    new_pos = (0, 0)  # Center of the screen in norm units
    # Check for each painting if the mouse is pressed on it. 
    # If so, center the painting and enlarge it for better visibility.
    for painting in paintings:
        if mouseObject.isPressedIn(painting, buttons=[0]):
            for textbox in textboxes:
                textbox.autoDraw = False
            # Remember old size and position to revert back to later on
            original_size = painting.size
            original_pos = painting.pos
            print(original_size)
            painting.size = new_size
            painting.pos = new_pos
            # Draw painting again and flip to screen
            painting.draw()
            window.flip()
            time.sleep(1)  # Pause for 1 second to allow user to view the enlarged painting
            
            # Wait for mouse release to reset the painting
            while not any(mouseObject.getPressed()):
                pass
            
            # Reset painting parameters
            painting.size = original_size
            painting.pos = original_pos
            
            # Make textboxes visible again
            for textbox in textboxes:
                textbox.autoDraw = True
            
            # Draw the grid again
            draw_grid()
            window.flip()
            # Reset mouse events
            event.clearEvents('mouse')

#### MAIN CODE ####
# Is there a secondary window? Set parameter
secondary_screen = False
if secondary_screen:
    screen_num = 1
else:
    screen_num = 0
    
# Input subject number
sub_num = input("Enter subject: ")

# Get the current date and time
current_datetime = datetime.now()
# Format the date and time as a string in the format ddmmyy_hhmmss
current_datetime = current_datetime.strftime('%d%m%y_%H%M%S')

# Create unique filename
filename = "_".join([sub_num, "art_ranking.csv", current_datetime])
output_file = os.path.join("data", filename)

# Initialize window and mouse
win = visual.Window(fullscr=True, color=(0.5, 0.5, 0.5), screen=screen_num)
mouse = event.Mouse()

# Define grid parameters
rows = 6
cols = 6
image_size = (0.15, 0.15)
text_box_height = 0.06
text_box_width = 0.1
text_box_spacer = 0.05
letter_size = text_box_height * 0.8
grid_spacing_x = 2 * image_size[0]
grid_spacing_y = 2 * image_size[1]
start_x = -0.9 + grid_spacing_x / 2
start_y = 0.9 - grid_spacing_y / 2

# Intialize variables
image_paths = []

# Load stimuli subdirectories
subfolders = os.listdir("stimuli")

# Iterate over subfolders
for subfolder in subfolders:
    # Split string into separate categories
    for file in os.listdir(os.path.join("stimuli", subfolder)):
        if file.endswith(".jpg"):
            image_paths.append(os.path.join("stimuli", subfolder, file))

# Shuffle image_paths
shuffle(image_paths)

# Create stimuli
images = []
text_boxes = []
for i in range(rows):
    for j in range(cols):
        img_path = image_paths[i * cols + j]
        pos_x = start_x + j * grid_spacing_x
        pos_y = start_y - i * grid_spacing_y
        
        # Create image stimulus
        image_stim = visual.ImageStim(win, image=img_path, pos=(pos_x, pos_y), size=image_size)
        images.append(image_stim)
        
        # Create text box stimulus
        text_box_stim = visual.TextBox2(win, text='', pos=(pos_x, pos_y - (image_size[1] + text_box_height - text_box_spacer)), 
                                        letterHeight=letter_size, size=(text_box_width, text_box_height), alignment='center',
                                        borderColor='black', fillColor='white', color='black', placeholder="", autoDraw=True, editable=True)
        text_boxes.append(text_box_stim)

# Instruction message
instruction = visual.TextStim(win, text="Rank each painting from 1 (highest) to 36 (lowest). Press 's' to save and exit.", 
                              pos=(0, 0.9), height=0.05 ,color='black')

# Run the experiment
running = True
current_state = False
while running:
    draw_grid()
    win.flip()
    
    # Enlarge painting if user clicks on it
    focus_painting(mouse, images, win, text_boxes)
    
    # Validate input to make sure only numbers between 1 and 36 are entered.
    validate_textboxes(text_boxes)
        
    # Check for keyboard events
    keys = event.getKeys()
    if 's' in keys:
        running = False
        save_and_exit = True
    if 'escape' in keys:
        running = False
        save_and_exit = False


# Collect and save rankings if 's' was pressed
if save_and_exit:
    rankings = []
    
    # TO-DO: Check if there are no empty or duplicate values. 
    
    for i, text_box in enumerate(text_boxes):
        ranking = text_box.text
        rankings.append((image_paths[i], ranking))

    # Save rankings to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image', 'Ranking'])
        for image_path, ranking in rankings:
            writer.writerow([image_path, ranking])

# Close the window
win.close()
core.quit()