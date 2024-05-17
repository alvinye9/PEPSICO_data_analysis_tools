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

def find_closest_times(txt_filename, highlight_time, num_closest=4):
    """
    Finds the rows with the closest times to the given highlight time.

    :param txt_filename: The input .txt file path.
    :param highlight_time: The time to be highlighted.
    :param num_closest: The number of closest rows to find.
    :return: The closest rows.
    """
    target_time = parse_time(highlight_time)
    time_pattern = re.compile(r'\d+:\d{2}')  # Regex to find time in format H:MM
    rows_with_times = []

    with open(txt_filename, 'r') as txt_file:
        for line in txt_file:
            match = time_pattern.search(line)
            if match:
                row_time_str = match.group()
                row_time = parse_time(row_time_str)
                if row_time:
                    time_diff = abs((row_time - target_time).total_seconds())
                    rows_with_times.append((line.strip(), time_diff))

    # Sort by time difference and get the closest rows
    rows_with_times.sort(key=lambda x: x[1])
    closest_rows = [row for row, _ in rows_with_times[:num_closest]]

    return closest_rows

def highlight_rows_in_file(txt_filename, output_filename, highlight_time, num_closest=4):
    """
    Highlights the rows with the closest times to the given highlight time by surrounding them with asterisks.

    :param txt_filename: The input .txt file path.
    :param output_filename: The output .txt file path.
    :param highlight_time: The time to be highlighted.
    :param num_closest: The number of closest rows to find and highlight.
    """
    closest_rows = find_closest_times(txt_filename, highlight_time, num_closest)

    with open(txt_filename, 'r') as txt_file, open(output_filename, 'w') as out_file:
        for line in txt_file:
            stripped_line = line.strip()
            if stripped_line in closest_rows:
                out_file.write(f"**{stripped_line}**\n")
            else:
                out_file.write(line)

if __name__ == "__main__":
    txt_filename = 'output.txt'  # The text file generated in step 1
    output_filename = 'highlighted_output.txt'  # The output text file with highlighted rows
    highlight_time = "0:53"  # Replace with your desired highlight time
    num_closest = 4  # Number of closest rows to highlight

    # Highlight the closest rows in the output file
    highlight_rows_in_file(txt_filename, output_filename, highlight_time, num_closest)

    print(f"Highlighted rows written to {output_filename}.")
