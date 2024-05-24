import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import webbrowser

class BFHighlighter:
    def __init__(self, rpt_file_path):
        self.TIME_PATTERN = re.compile(r'\d{1,2}:\d{2}')  # Regex to find time in format H:MM or HH:MM
        self.QUANTITY_PATTERN = re.compile(r'\s+\d+\s+\d+\s+\d+\s*$')  # Regex to match lines with quantities at the end
        self.START_PATTERN = re.compile(r'^\s*\d{6}')  # Regex to match lines starting with a 6-digit number
        self.LOCATION_ID_PATTERN = re.compile(r'\s+(?:\d+|D\d+|T\d+)\s*$')  # Regex to match location IDs
        self.EXCLAMATION_PATTERN = re.compile(r'!')  # start with !

        self.rpt_file_path = rpt_file_path
        self.crossed_rows = []
        self.pos_quant_indices = []
        self.neg_quant_indices = []
        self.even_quant_indices = []
        self.txt_file_name = "./Blind_Receiver.txt"
        self.rpt_to_txt(rpt_file_path)
        self.updateIndices()

        # print("Negative Quant Indices: ", self.neg_quant_indices)
        # print("Even Quant Indices: ", self.even_quant_indices)
        # print("Positive Quant Indices: ", self.pos_quant_indices)

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

    def determine_section(self, a_indices, b_indices, c_indices, index):
        # Combine the indices with section identifiers
        sections = [(i, 'Pos') for i in a_indices] + [(i, 'Even') for i in b_indices] + [(i, 'Neg') for i in c_indices]
        # Sort the combined list by indices
        sections.sort()

        # Iterate through the sorted sections to find the correct section
        current_section = None
        for i, section in sections:
            if index < i:
                break
            current_section = section

        return current_section


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
            diff_qty = int(quantities[-1])
            return received_qty, order_qty, diff_qty
        # Determine the sign for diff_qty
        if received_qty > order_qty:
            diff_qty = f"+{diff_qty}"
        elif received_qty < order_qty:
            diff_qty = f"-{diff_qty}"
        else:
            diff_qty = f"{diff_qty}"
        return None, None, None

    def extract_pallet_size(self, line):
        """
        Extract the last two quantities from the line.

        :param line: The line from the file.
        :return: Tuple of (received quantity, order quantity) if both are found, else (None, None).
        """
        quantities = re.findall(r'\d+', line)
        if len(quantities) >= 3:
            pallet_size = int(quantities[-2])
            # print("Pallet Size: ",pallet_size)
            return pallet_size
        return None

    def find_closest_timestamped_rows(self, lines, start_index):
        """
        Find the closest 2 timestamped rows chronologically before and after the start index.

        :param lines: The list of lines from the file.
        :param start_index: The starting index to search around.
        :return: A tuple of three lists: previous rows, current row, and future rows.
        """
        full_pallet_rows_with_times = []
        partial_pallet_rows_with_times = []
        pos_sec_rows_with_times = []
        crossed_rows = self.crossed_rows

        # Find valid timestamped rows
        for idx, line in enumerate(lines):
            if self.TIME_PATTERN.search(line) and (self.START_PATTERN.search(line) or self.EXCLAMATION_PATTERN.search(line)): #is a timestamped row
                # pallet_size = self.extract_pallet_size(line)
                # print("Timestamped Row: ", line)
                if self.determine_section(self.pos_quant_indices,self.even_quant_indices, self.neg_quant_indices, idx) == "Pos":
                    pos_sec_rows_with_times.append((line, self.parse_time(self.TIME_PATTERN.search(line).group())))
                else:
                  full_pallet_rows_with_times.append((line, self.parse_time(self.TIME_PATTERN.search(line).group())))

        # Get the target time from the start index
        time_match = self.TIME_PATTERN.search(lines[start_index])
        if time_match:
            target_time = self.parse_time(time_match.group())
        else:
            print("ERROR: CURRENT ROW DOES NOT HAVE TIME STAMP")
            return [], [lines[start_index]], []

        print("Time of Mixed Event: ", target_time.strftime("%H:%M"))

        # Calculate Previous Timestamps in positive sections
        # Filter lines where the time is greater than the target time
        filtered_lines = []
        for line, time in pos_sec_rows_with_times:
        #   print(time, " is greater than ", target_time, " ", time < target_time)
            if time < target_time:
                filtered_lines.append(line)
        # print(filtered_lines)
        sorted_filtered_lines = sorted(
            filtered_lines,
            key=lambda x: self.parse_time(self.TIME_PATTERN.search(x).group())
        )
        # print("Timestamps before: ", target_time, " : ", sorted_filtered_lines)

        previous_rows = []
        previous_rows = sorted_filtered_lines[-2:] #if sorted_filtered_lines else [] #extract the previous two items
        # print("Number of Previous Timestamps: ", len(previous_rows))
        medium_priority_rows = []
        high_priority_row = []
        if(len(previous_rows)==2):
            high_priority_row = previous_rows[1]
            medium_priority_rows = previous_rows[0]
        elif(len(previous_rows)==1):
            high_priority_row = previous_rows[0]
        else:
            high_priority_row = []
            medium_priority_rows = []

        # print("High Priority: ", high_priority_row)
        # print("Medium Priority: ", medium_priority_rows)

        # Calculate Future Timestamps in positive sections
        filtered_lines = []
        for line, time in pos_sec_rows_with_times:
        #   print(time, " is less than target_time", target_time, "  ", time > target_time)
            if time > target_time:
                filtered_lines.append(line)
        # print(filtered_lines)
        sorted_filtered_lines = sorted(
            filtered_lines,
            key=lambda x: self.parse_time(self.TIME_PATTERN.search(x).group())
        )
        # print("Timestamps After: ", target_time, " : ", sorted_filtered_lines)

        future_rows = []
        if sorted_filtered_lines:
            future_rows = sorted_filtered_lines[1:] #extract the first item
        if(len(future_rows) > 0):
            medium_priority_rows.append(future_rows[0])
        # else:
        #     print("NO FUTURE ROWS")

        for line, time in pos_sec_rows_with_times:
            pallet_size = self.extract_pallet_size(line)
            if not(pallet_size % 6 == 0):
                partial_pallet_rows_with_times.append(line)

        low_priority_rows = partial_pallet_rows_with_times
        # print("Low Priority: Partial Pallets")

        if(len(high_priority_row) == 0):
            high_priority_row = lines[start_index]

        return medium_priority_rows, high_priority_row, low_priority_rows

    def updateIndices(self):
        with open(self.txt_file_name, 'r') as txt_file:
            lines = txt_file.readlines()
            for i, line in enumerate(lines):
                if self.QUANTITY_PATTERN.search(line) and self.START_PATTERN.match(line) and not(self.TIME_PATTERN.search(line)):  # finds "Quantity Line"
                  # print("quantity Line: ", line, " Index: ", i)
                    received_qty, order_qty, diff_qty = self.extract_quantities(line)
                    if received_qty < order_qty:
                        self.neg_quant_indices.append(i)
                    elif received_qty > order_qty:
                        self.pos_quant_indices.append(i)
                    else:
                        self.even_quant_indices.append(i)

    def find_highlight_rows(self, txt_filename):
        """
        Finds the rows where received quantity is less than order quantity and
        returns the closest 2 rows with timestamps before and after the last timestamped row in that section

        :param txt_filename: The input .txt file path.
        :return: Three lists of rows to be highlighted: previous rows, current row, and future rows.
        """
        previous_rows = []
        current_row = []
        future_rows = []
        crossed_rows = []

        with open(txt_filename, 'r') as txt_file:
            lines = txt_file.readlines()
            for i, line in enumerate(lines):
              if self.QUANTITY_PATTERN.search(line) and self.START_PATTERN.match(line) and not(self.TIME_PATTERN.search(line)):  # finds "Quantity Line"
                  # print("quantity Line: ", line, " Index: ", i)
                  received_qty, order_qty, diff_qty = self.extract_quantities(line)
                  if received_qty is not None and order_qty is not None and received_qty < order_qty:

                      if i + 1 < len(lines):  # make sure that current line is not the last line
                          i += 1
                          next_line = lines[i]  # updates next_line to be first timestamped line in negative section
                          previous_rows, current_row, future_rows = self.find_closest_timestamped_rows(lines, i)
                          break
        return previous_rows, current_row, future_rows

    def highlight_rows_in_pdf(self, txt_filename, pdf_filename):
        """
        Highlights the rows with the closest times to the given highlight time or
        the rows where received quantity is less than order quantity in the PDF.

        :param txt_filename: The input .txt file path.
        :param pdf_filename: The output .pdf file path.
        """
        crossed_rows = self.crossed_rows
        previous_rows, current_row, future_rows = self.find_highlight_rows(txt_filename)

        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        c.setFont("Courier", 10)  # Use a monospaced font

        with open(txt_filename, 'r') as txt_file:
            y_position = height - 40
            line_height = 12

            for line in txt_file:
                # line_with_diff = line.strip()
                # # Check if line has quantities and add the diff_qty with + or - sign
                # if self.QUANTITY_PATTERN.search(line) and self.START_PATTERN.match(line) and not(self.TIME_PATTERN.search(line)):
                #     print("reached quantity line")
                #     received_qty, order_qty, diff_qty = self.extract_quantities(line)
                #     if received_qty is not None and order_qty is not None:
                #         if diff_qty is not None:
                #           if received_qty > order_qty:
                #             diff_qty = f"+{diff_qty}"
                #           elif received_qty < order_qty:
                #             diff_qty = f"-{diff_qty}"
                #     # Reconstruct the line with the diff_qty with sign
                #     line_parts = line.split()
                #     # Assume the last part is diff_qty
                #     line_parts[-1] = str(diff_qty)
                #     line_with_diff = '              '.join(line_parts)

                # if line in current_row and not(line in crossed_rows):
                if line in current_row:
                    c.setFillColor(colors.red) #high
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)
                elif line in previous_rows:
                    c.setFillColor(colors.orange) #med
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)
                elif line in future_rows: #plot low priority last in the elif structure so it can be ovewritten
                    c.setFillColor(colors.yellow) #low
                    c.rect(30, y_position - 2, width - 60, line_height, fill=True, stroke=False)
                    c.setFillColor(colors.black)

                if line in crossed_rows:
                    c.setFillColor(colors.black)
                    c.setLineWidth(1)  # Set line width for crossing out
                    offset = 2
                    c.line(30, y_position + line_height / 2 - offset, width, y_position + line_height / 2 - offset)

                c.drawString(30, y_position, line.strip())
                # c.drawString(30, y_position, line_with_diff.strip())
                y_position -= line_height

                if y_position < 40:
                    c.showPage()
                    c.setFont("Courier", 10)
                    y_position = height - 40

        c.save()
        print("[RED] Likely Mixed Event Occurence: ", current_row)
        print("[ORANGE] Likely Mixed Pallet: ", previous_rows)  
        # if len(previous_rows) == 1:
        #     print("[ORANGE] Likely Mixed Pallets: ", previous_rows)
        # else: 
        #     for row in previous_rows: 
        #         print("[ORANGE] Likely Mixed Pallets: ", row)           
        for row in future_rows: 
            print("[YELLOW] Partial Pallet in Positive Section: ", row)

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
        self.highlight_rows_in_pdf(self.txt_file_name, 'Blind_Receiver_highlighted.pdf')
        print(f"Highlighted rows written to Blind_Receiver_highlighted.pdf.")
        webbrowser.open_new('Blind_Receiver_highlighted.pdf')

    def updatedCrossedOutRows(self):
        with open(self.txt_file_name, 'r') as txt_file:
            lines = txt_file.readlines()

            for i, line in enumerate(lines):
                if self.TIME_PATTERN.search(line) and (self.START_PATTERN.search(line) or self.EXCLAMATION_PATTERN.search(line)) and self.LOCATION_ID_PATTERN.search(line):
                    # print("Inaccessible Location: ", line)
                    self.crossed_rows.append(line)

    def rpt_to_txt(self, rpt_file):
        self.convert_rpt_to_txt(rpt_file, self.txt_file_name)
        self.updatedCrossedOutRows()

# if __name__ == "__main__":
#     obj=BFHighlighter('BF1.rpt')
#     obj.create_pdf()
#     print("done")
