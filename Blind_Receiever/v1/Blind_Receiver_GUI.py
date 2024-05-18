import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import tkinter as tk
from tkinter import filedialog, simpledialog

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
                    rows_with_times.append((line, time_diff))

    # Sort by time difference and get the closest rows
    rows_with_times.sort(key=lambda x: x[1])
    closest_rows = [row for row, _ in rows_with_times[:num_closest]]

    return closest_rows

def highlight_rows_in_pdf(txt_filename, pdf_filename, highlight_time, num_closest=4):
    """
    Highlights the rows with the closest times to the given highlight time in the PDF.

    :param txt_filename: The input .txt file path.
    :param pdf_filename: The output .pdf file path.
    :param highlight_time: The time to be highlighted.
    :param num_closest: The number of closest rows to find and highlight.
    """
    closest_rows = find_closest_times(txt_filename, highlight_time, num_closest)

    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    c.setFont("Courier", 10)  # Use a monospaced font

    # highlight_height = 10  # Adjust the height of the highlighted area
    
    with open(txt_filename, 'r') as txt_file:
        y_position = height - 40
        line_height = 12

        for line in txt_file:
            if line in closest_rows:
                c.setFillColor(colors.yellow)
                c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                c.setFillColor(colors.black)

            c.drawString(30, y_position, line.strip())
            y_position -= line_height

            if y_position < 40:
                c.showPage()
                c.setFont("Courier", 10)
                y_position = height - 40

    c.save()

def browse_file():
    """
    Opens a file dialog to browse for a .rpt file and converts it to a .txt file.
    """
    file_path = filedialog.askopenfilename(filetypes=[("RPT files", "*.rpt")])
    if file_path:
        convert_rpt_to_txt(file_path, 'output.txt')

def convert_rpt_to_txt(rpt_filename, txt_filename):
    """
    Converts a .rpt file to a .txt file while maintaining row structure.

    :param rpt_filename: The input .rpt file path.
    :param txt_filename: The output .txt file path.
    """
    with open(rpt_filename, 'r') as rpt_file, open(txt_filename, 'w') as txt_file:
        for line in rpt_file:
            txt_file.write(line)

def create_pdf():
    """
    Prompts the user for a desired time and creates the highlighted PDF.
    """
    highlight_time = simpledialog.askstring("Input", "Enter the desired time (H:MM):")
    if highlight_time:
        highlight_rows_in_pdf('output.txt', 'Blind_Receiver_highlighted.pdf', highlight_time)
        print(f"Highlighted rows written to highlighted_output.pdf.")

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("RPT to PDF Highlighter")

    # Create a button to browse for the .rpt file
    browse_button = tk.Button(root, text="Browse for .rpt file", command=browse_file)
    browse_button.pack(pady=20)

    # Create a button to create the PDF with highlighted rows
    create_pdf_button = tk.Button(root, text="Create Highlighted PDF", command=create_pdf)
    create_pdf_button.pack(pady=20)

    # Run the main loop
    root.mainloop()
