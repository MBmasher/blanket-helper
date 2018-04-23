from __future__ import division

class PerfectSlider():
    def __init__(self, start_x, start_y, mid_x, mid_y, end_x, end_y, time):
        self.start_x = start_x
        self.start_y = start_y
        self.mid_x = mid_x
        self.mid_y = mid_y
        self.end_x = end_x
        self.end_y = end_y
        self.time = time

    # Calculate the coordinates of a circle which would blanket.

    def find_blanket(self):
        # Calculate slope of the lines between start-mid and mid-end.
        start_delta_x = self.mid_x - self.start_x
        start_delta_y = self.mid_y - self.start_y
        mid_delta_x = self.end_x - self.mid_x
        mid_delta_y = self.end_y - self.mid_y

        start_slope = start_delta_y / start_delta_x
        mid_slope = mid_delta_y / mid_delta_x

        # Calculate centre.
        centre_x = ((start_slope * mid_slope * (self.start_y - self.end_y) + mid_slope * (self.start_x + self.mid_x)
                     - start_slope * (self.mid_x + self.end_x))
                    / (2.0 * (mid_slope - start_slope)))

        centre_y = (-1 * (centre_x - (self.start_x + self.mid_x) / 2.0) / start_slope
                    + (self.start_y + self.mid_y) / 2.0)

        return (centre_x, centre_y)


# Converts a line from .osu file into PerfectSlider, return None if not a three point slider


def convert_hit_object(line):
    split_line = line.split(",")

    # If the object is a slider which has an attribute of "Perfect" (3 point slider made of a circle arc)
    if (int(split_line[3]) & 0b10) and split_line[5].split("|")[0] == "P":
        mid_coords = split_line[5].split("|")[1]
        end_coords = split_line[5].split("|")[2]

        return PerfectSlider(int(split_line[0]),
                             int(split_line[1]),
                             int(mid_coords.split(":")[0]),
                             int(mid_coords.split(":")[1]),
                             int(end_coords.split(":")[0]),
                             int(end_coords.split(":")[1]),
                             int(split_line[2]))
    else:
        return None


# Parse the text from a copy pasted hit object into a ms time, return None if not a valid object.


def parse_into_ms(text):
    # Split text into time units: minutes, seconds, milliseconds.
    timestamp = text.split(" ")[0]
    time_units = timestamp.split(":")

    if len(time_units) != 3:
        return None

    for i in time_units:
        try:
            a = int(i)
        except ValueError:
            return None

    # Convert minutes:seconds:milliseconds to milliseconds.
    ms = int(time_units[2])
    ms += int(time_units[1]) * 1000
    ms += int(time_units[0]) * 60000

    return ms