import Tkinter
import perfect_slider
import tkFileDialog
import tkMessageBox
import ttk
import sys


# Load slider list.


def load_sliders():
    global osu_file_path

    # Opening the osu file and splitting it into lines.
    osu_file = open(osu_file_path, "r")
    osu_lines = [line.rstrip('\n') for line in osu_file]

    # Find the line number in which the objects start.
    line_number = osu_lines.index("[HitObjects]") + 1

    # Making a list with all the perfect sliders.
    hit_object_string_list = osu_lines[line_number:]
    slider_list = map(lambda x: perfect_slider.convert_hit_object(x), hit_object_string_list)

    # Get rid of all the objects which aren't perfect sliders.
    slider_list = filter(lambda x: x is not None, slider_list)

    osu_file.close()

    return slider_list


# Load hit object list in string form.


def load_hit_objects():
    global osu_file_path

    # Opening the osu file and splitting it into lines.
    osu_file = open(osu_file_path, "r")
    osu_lines = [line.rstrip('\n') for line in osu_file]

    # Find the line number in which the objects start.
    line_number = osu_lines.index("[HitObjects]") + 1

    # Making a list with all the hit objects.
    hit_object_string_list = osu_lines[line_number:]

    osu_file.close()

    return hit_object_string_list


# Function used to kill the GUI.


def stop():
    global reloading
    reloading = False

    root.quit()
    root.destroy()


# Function used to kill the GUI, but tell the program not to load file dialog as it is reloading the map.


def reload_map():
    global reloading
    reloading = True

    root.quit()
    root.destroy()


# Function used to kill the program entirely.


def kill():
    sys.exit()


# Function used to get the blanket.


def get_blanket(event=None):
    parsed_slider_time = perfect_slider.parse_into_ms(slider_entry.get())

    # Show error box if the text wasn't able to be parsed.
    if parsed_slider_time is not None:
        slider_found = False
        global slider_list, slider_blanket

        # Try to find the slider in the slider list.
        for i in slider_list:
            if i.time == parsed_slider_time:
                slider_blanket = i
                slider_found = True
                break

        # Calculate blanket coords.
        global blanket_coords
        blanket_coords = slider_blanket.find_blanket()

        if not slider_found:
            error_box = tkMessageBox.showerror("Error", "Slider not found.")
        else:
            # Update labels.
            ms_label["text"] = "Slider found at {}ms.".format(parsed_slider_time)
            coords_label["text"] = "Coordinates: ({}, {}), ({}, {}), ({}, {})".format(
                slider_blanket.start_x, slider_blanket.start_y,
                slider_blanket.mid_x, slider_blanket.mid_y,
                slider_blanket.end_x, slider_blanket.end_y)
            blanket_coords_label["text"] = "Coordinates of blanket: ({:.2f}, {:.2f})".format(
                blanket_coords[0], blanket_coords[1])
            if (slider_blanket.find_blanket()[0] < 0
                    or slider_blanket.find_blanket()[0] > 512
                    or slider_blanket.find_blanket()[1] < 0
                    or slider_blanket.find_blanket()[1] > 384):
                oob_warning_label['text'] = "WARNING: The blanket is off the playfield."
            else:
                oob_warning_label['text'] = ""

    else:
        tkMessageBox.showerror("Error", "That text was not able to be parsed.")


# Function used to blanket the object.


def blanket_object(event=None):
    global osu_file_path

    # Open osu file, write all lines to a list
    with open(osu_file_path, 'r') as osu_file:
        data = osu_file.readlines()

    parsed_object_time = perfect_slider.parse_into_ms(object_entry.get())
    # Show error box if the text wasn't able to be parsed.
    if parsed_object_time is not None:
        hit_object_found = False
        object_line = ""

        # Try to find the hit object in the list.
        for i in hit_object_list:
            if int(i.split(",")[2]) == parsed_object_time:
                object_line = i
                hit_object_found = True
                break

        if not hit_object_found:
            error_box = tkMessageBox.showerror("Error", "Hit object not found.")
        elif ms_label["text"] == "":
            error_box = tkMessageBox.showerror("Error", "Slider blanket not selected.")
        else:
            new_string = ""

            # Create string for coords.
            coords_string = "{:.0f},{:.0f},".format(blanket_coords[0], blanket_coords[1])

            # If object is a slider, change all slider points too.
            if int(object_line.split(",")[3]) & 0b10:
                slider_type = object_line.split(",")[5].split("|")[0]
                delta_x = int(round(blanket_coords[0]) - int(object_line.split(",")[0]))
                delta_y = int(round(blanket_coords[1]) - int(object_line.split(",")[1]))

                # Start changing all coordinates of slider points.
                slider_points = []
                for i in object_line.split(",")[5].split("|")[1:]:
                    print i
                    slider_points.append([str(int(i.split(":")[0]) + delta_x),
                                          str(int(i.split(":")[1]) + delta_y)])

                # Convert slider points to string.
                slider_points_string_list = []
                for i in slider_points:
                    slider_points_string_list.append(":".join(i))

                # Create string for slider points
                slider_points_string = "{}|{}".format(slider_type, "|".join(slider_points_string_list))

                # Now, remove the old coordinates of the object's string and insert the new ones.
                new_string = "{}{},{},{}\n".format(coords_string, ",".join(object_line.split(",")[2:5]),
                                                   slider_points_string, ",".join(object_line.split(",")[6:]))
                print ",".join(object_line.split(",")[6:])
                print new_string

            elif int(object_line.split(",")[3]) & 0b1:  # if object is a hitcircle
                # Now, remove the old coordinates of the object's string and insert the new ones.
                new_string = "{}{}\n".format(coords_string, ",".join(object_line.split(",")[2:]))

            else:
                tkMessageBox.showerror("Error", "This type of hit object is invalid/a spinner.")

            # Find old object's line number and replace with the new object.
            try:
                line_number = data.index("{}\n".format(object_line))
                data[line_number] = new_string

                # Rewrite all data.
                with open(osu_file_path, 'w') as osu_file:
                    osu_file.writelines(data)

            except ValueError:
                tkMessageBox.showerror("Error", "The hit object to be blanketed was not found.\n"
                                       + "Please click the \"Reload map\" button after making changes to your map.")

    else:
        tkMessageBox.showerror("Error", "That text was not able to be parsed.")


reloading = False

while True:
    # Ask user for file dialog.
    if not reloading:
        Tkinter.Tk().withdraw()
        osu_file_path = tkFileDialog.askopenfilename(title="Select an osu file", filetypes=(("osu files", "*.osu"),))

    hit_object_list = load_hit_objects()
    slider_list = load_sliders()

    # Show warning message if the map has no perfect sliders.
    if len(slider_list) == 0:
        tkMessageBox.showerror("Error", "The map you have picked does not have any perfect sliders.")
    else:
        # Start GUI!
        root = Tkinter.Tk()
        root.resizable(width=False, height=False)
        root.wm_attributes("-topmost", 1)
        root.title("Weighted Objects")

        Tkinter.Label(root, fg="red", text="Found {} perfect sliders.".format(len(slider_list))).grid(
            row=0, column=0, columnspan=3)

        Tkinter.Label(root, fg="black", text="Copy-paste a slider to find its blanket:").grid(row=1, column=0)

        slider_entry = Tkinter.Entry(root)
        slider_entry.grid(row=1, column=1)
        slider_entry.bind("<Return>", get_blanket)

        Tkinter.Button(root, fg="blue", text="Check blanket!", command=get_blanket).grid(row=1, column=2)

        ms_label = Tkinter.Label(root, fg="black")
        ms_label.grid(row=2, column=0, columnspan=3)

        coords_label = Tkinter.Label(root, fg="black")
        coords_label.grid(row=3, column=0, columnspan=3)

        blanket_coords_label = Tkinter.Label(root, fg="black")
        blanket_coords_label.grid(row=4, column=0, columnspan=3)

        oob_warning_label = Tkinter.Label(root, fg="red")
        oob_warning_label.grid(row=5, column=0, columnspan=3)

        Tkinter.Label(root, fg="black", text="Copy-paste an object to blanket it:").grid(row=6, column=0)

        object_entry = Tkinter.Entry(root)
        object_entry.grid(row=6, column=1)
        object_entry.bind("<Return>", blanket_object)

        Tkinter.Button(root, fg="blue", text="Blanket object!", command=blanket_object).grid(row=6, column=2)

        Tkinter.Button(root, fg="blue", text="Reload map", command=reload_map).grid(row=7, column=0, columnspan=3)

        Tkinter.Button(root, fg="red", text="Choose another map", command=stop).grid(row=8, column=0, columnspan=3)

        # If window is closed, stop the program.
        root.protocol("WM_DELETE_WINDOW", kill)

        root.mainloop()
