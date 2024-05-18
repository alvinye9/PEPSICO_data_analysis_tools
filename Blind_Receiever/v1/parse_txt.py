from datetime import datetime
import re

def parse_time(time_str):
    """
    Parse the time in the format "H:MM".

    :param time_str: The time string to parse.
    :return: The datetime object.
    """
    try:
        return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        return None

def find_closest_time(txt_filename, highlight_time):
    """
    Finds the row with the closest time to the given highlight time.

    :param txt_filename: The input .txt file path.
    :param highlight_time: The time to be highlighted.
    :return: The closest row.
    """
    target_time = parse_time(highlight_time)
    closest_row = None
    closest_diff = None

    time_pattern = re.compile(r'\d+:\d{2}')  # Regex to find time in format H:MM

    with open(txt_filename, 'r') as txt_file:
        for line in txt_file:
            match = time_pattern.search(line)
            if match:
                row_time_str = match.group()
                row_time = parse_time(row_time_str)
                if row_time:
                    time_diff = abs((row_time - target_time).total_seconds())
                    if closest_diff is None or time_diff < closest_diff:
                        closest_diff = time_diff
                        closest_row = line.strip()

    return closest_row

if __name__ == "__main__":
    txt_filename = 'output.txt'  # The text file generated in step 1
    highlight_time = "0:53"  # Replace with your desired highlight time

    # Find the closest time
    closest_row = find_closest_time(txt_filename, highlight_time)

    if closest_row:
        print("Closest Row:")
        print(closest_row)
    else:
        print("No matching row found.")
