import csv

def convert_rpt_to_csv(rpt_filename, csv_filename, delimiter='\t'):
    """
    Converts a .rpt file to a .csv file.

    :param rpt_filename: The input .rpt file path.
    :param csv_filename: The output .csv file path.
    :param delimiter: The delimiter used in the .rpt file.
    """
    with open(rpt_filename, 'r') as rpt_file:
        lines = rpt_file.readlines()

    with open(csv_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        for line in lines:
            row = line.strip().split(delimiter)
            writer.writerow(row)

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

    # Debug: Print the first few lines of the file
    print("First few lines of the .rpt file:")
    for line in lines[:5]:
        print(line)

    headers = lines[0].strip().split(delimiter)
    headers = [header.strip() for header in headers]  # Remove extra spaces
    data = []
    for line in lines[1:]:
        values = line.strip().split(delimiter)
        values = [value.strip() for value in values]  # Remove extra spaces
        row = dict(zip(headers, values))
        data.append(row)
    
    return headers, data

if __name__ == "__main__":
    rpt_filename = 'input.rpt'  # Replace with your .rpt file path
    # csv_filename = 'output.csv'  # Replace with your desired .csv file path
    # delimiter = '\t'  # Replace with your .rpt file delimiter if different

    # convert_rpt_to_csv(rpt_filename, csv_filename, delimiter)


    # Read the data from the .rpt file
    headers, data = read_rpt_file(rpt_filename, delimiter='\t')

    # Debug: Print headers and a sample row
    print("Headers:", headers)
    if data:
        print("Sample row:", data[0])