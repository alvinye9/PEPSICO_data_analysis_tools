import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import tkinter as tk
from tkinter import filedialog, simpledialog


class RPTtoPDFHighlighter:
    def __init__(self):
        self.TIME_PATTERN = re.compile(r'\d{1,2}:\d{2}')  # Regex to find time in format H:MM or HH:MM
        self.QUANTITY_PATTERN = re.compile(r'\s+\d+\s+\d+\s+\d+\s*$')  # Regex to match lines with quantities at the end
        self.START_PATTERN = re.compile(r'^\s*\d{6}')  # Regex to match lines starting with a 6-digit number
        self.root = tk.Tk()
        self.root.title("RPT to PDF Highlighter")

        browse_button = tk.Button(self.root, text="Browse for .rpt file", command=self.browse_file)
        browse_button.pack(pady=20)

        create_pdf_button = tk.Button(self.root, text="Create Highlighted PDF", command=self.create_pdf)
        create_pdf_button.pack(pady=20)

        self.root.mainloop()

    @staticmethod
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

    def extract_quantities(self, line):
        """
        Extract the last two quantities from the line.

        :param line: The line from the file.
        :return: Tuple of (received quantity, order quantity) if both are found, else (None, None).
        """
        quantities = re.findall(r'\d+', line)
        if len(quantities) >= 3:
            received_qty = int(quantities[-2])
            order_qty = int(quantities[-3])
            return received_qty, order_qty
        return None, None

    def find_closest_timestamped_rows(self, lines, start_index):
        """
        Find the closest 2 timestamped rows before and after the start index.

        :param lines: The list of lines from the file.
        :param start_index: The starting index to search around.
        :return: A tuple of three lists: previous rows, current row, and future rows.
        """
        rows_with_times = []

        # Collect all rows with timestamps and their times
        for line in lines:
            if self.TIME_PATTERN.search(line) and self.START_PATTERN.match(line):
                rows_with_times.append((line, self.parse_time(self.TIME_PATTERN.search(line).group())))

        # Get the target time from the start index
        target_time = self.parse_time(self.TIME_PATTERN.search(lines[start_index]).group())

        # Separate rows into previous, current, and future
        previous_rows = sorted([line for line, time in rows_with_times if time < target_time], key=lambda x: self.parse_time(self.TIME_PATTERN.search(x).group()))[-2:]
        current_row = [lines[start_index]]
        future_rows = sorted([line for line, time in rows_with_times if time > target_time], key=lambda x: self.parse_time(self.TIME_PATTERN.search(x).group()))[:2]

        return previous_rows, current_row, future_rows

    def find_highlight_rows(self, txt_filename):
        """
        Finds the rows where received quantity is less than order quantity and
        highlights the closest 2 rows with timestamps before and after the subsequent timestamped row.

        :param txt_filename: The input .txt file path.
        :return: Three lists of rows to be highlighted: previous rows, current row, and future rows.
        """
        previous_rows = []
        current_row = []
        future_rows = []

        with open(txt_filename, 'r') as txt_file:
            lines = txt_file.readlines()

            for i, line in enumerate(lines):
                if self.QUANTITY_PATTERN.search(line) and self.START_PATTERN.match(line):
                    received_qty, order_qty = self.extract_quantities(line)
                    if received_qty is not None and order_qty is not None and received_qty < order_qty:
                        if i + 1 < len(lines):
                            next_line = lines[i + 1]
                            if self.TIME_PATTERN.search(next_line) and self.START_PATTERN.match(next_line):
                                current_row = [next_line]
                                prev, curr, fut = self.find_closest_timestamped_rows(lines, i + 1)
                                previous_rows.extend(prev)
                                future_rows.extend(fut)
                                break

        return previous_rows, current_row, future_rows

    def highlight_rows_in_pdf(self, txt_filename, pdf_filename):
        """
        Highlights the rows with the closest times to the given highlight time or
        the rows where received quantity is less than order quantity in the PDF.

        :param txt_filename: The input .txt file path.
        :param pdf_filename: The output .pdf file path.
        """
        previous_rows, current_row, future_rows = self.find_highlight_rows(txt_filename)

        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        c.setFont("Courier", 10)  # Use a monospaced font

        with open(txt_filename, 'r') as txt_file:
            y_position = height - 40
            line_height = 12

            for line in txt_file:
                if line in current_row:
                    c.setFillColor(colors.yellow)
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)
                elif line in previous_rows:
                    c.setFillColor(colors.red)
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)
                elif line in future_rows:
                    c.setFillColor(colors.green)
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)

                c.drawString(30, y_position, line.strip())
                y_position -= line_height

                if y_position < 40:
                    c.showPage()
                    c.setFont("Courier", 10)
                    y_position = height - 40

        c.save()

    def browse_file(self):
        """
        Opens a file dialog to browse for a .rpt file and converts it to a .txt file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("RPT files", "*.rpt")])
        if file_path:
            self.convert_rpt_to_txt(file_path, 'output.txt')

    @staticmethod
    def convert_rpt_to_txt(rpt_filename, txt_filename):
        """
        Converts a .rpt file to a .txt file while maintaining row structure.

        :param rpt_filename: The input .rpt file path.
        :param txt_filename: The output .txt file path.
        """
        with open(rpt_filename, 'r') as rpt_file, open(txt_filename, 'w') as txt_file:
            for line in rpt_file:
                txt_file.write(line)

    def create_pdf(self):
        """
        Prompts the user for a desired time and creates the highlighted PDF.
        """
        self.highlight_rows_in_pdf('output.txt', 'Blind_Receiver_highlighted.pdf')
        print(f"Highlighted rows written to Blind_Receiver_highlighted.pdf.")


if __name__ == "__main__":
    RPTtoPDFHighlighter()
