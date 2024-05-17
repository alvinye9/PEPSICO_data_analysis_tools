def read_rpt_file(rpt_filename, delimiter='\t'):
    """
    Reads a .rpt file and returns a list of dictionaries representing the data.
    Assumes the first row contains the column headers.

    :param rpt_filename: The input .rpt file path.
    :param delimiter: The delimiter used in the .rpt file.
    :return: List of dictionaries with the data.
    """
    with open(rpt_filename, 'r') as rpt_file:
        lines = rpt_file.readlines()

    headers = lines[0].strip().split(delimiter)
    headers = [header.strip() for header in headers]  # Remove extra spaces
    data = []
    for line in lines[1:]:
        values = line.strip().split(delimiter)
        values = [value.strip() for value in values]  # Remove extra spaces
        row = dict(zip(headers, values))
        data.append(row)
    
    return headers, data

def highlight_columns_in_text(output_filename, headers, data, highlight_value, column_name, columns_to_highlight):
    """
    Creates a text file with specific columns highlighted based on a value in a given column.

    :param output_filename: The output text file path.
    :param headers: List of column headers.
    :param data: List of dictionaries containing the data.
    :param highlight_value: The value to be highlighted.
    :param column_name: The column name to check for the highlight value.
    :param columns_to_highlight: List of column names to be highlighted.
    """
    highlight_start = '\033[43m'  # ANSI escape code for yellow background
    highlight_end = '\033[0m'     # ANSI escape code to reset formatting

    with open(output_filename, 'w') as text_file:
        # Write headers
        for header in headers:
            if header in columns_to_highlight:
                text_file.write(f"{highlight_start}{header}{highlight_end}\t")
            else:
                text_file.write(f"{header}\t")
        text_file.write("\n")

        # Write data rows
        for row in data:
            for header in headers:
                value = row.get(header, "")
                if row.get(column_name) == highlight_value and header in columns_to_highlight:
                    text_file.write(f"{highlight_start}{value}{highlight_end}\t")
                else:
                    text_file.write(f"{value}\t")
            text_file.write("\n")

if __name__ == "__main__":
    rpt_filename = 'input.rpt'  # Replace with your .rpt file path
    output_filename = 'highlighted_output.txt'  # Replace with your desired output text file path

    # Read the data from the .rpt file
    headers, data = read_rpt_file(rpt_filename, delimiter='\t')

    # Debug: Print headers and a sample row
    print("Headers:", headers)
    if data:
        print("Sample row:", data[0])

    # Specify the value to be highlighted and the column name
    highlight_value = "0:53"
    column_name = "Received"

    # Specify the columns to be highlighted
    columns_to_highlight = ["Document", "Code", "Description", "Quantity", "Quantity", "Difference"]

    # Create the highlighted text file
    highlight_columns_in_text(output_filename, headers, data, highlight_value, column_name, columns_to_highlight)
