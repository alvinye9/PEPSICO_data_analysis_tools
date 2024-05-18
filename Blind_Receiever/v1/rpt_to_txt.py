def convert_rpt_to_txt(rpt_filename, txt_filename):
    """
    Converts a .rpt file to a .txt file while maintaining row structure.

    :param rpt_filename: The input .rpt file path.
    :param txt_filename: The output .txt file path.
    """
    with open(rpt_filename, 'r') as rpt_file, open(txt_filename, 'w') as txt_file:
        for line in rpt_file:
            txt_file.write(line)

if __name__ == "__main__":
    rpt_filename = 'input.rpt'  # Replace with your .rpt file path
    txt_filename = 'output.txt'  # Replace with your desired output text file path
    
    # Convert .rpt to .txt
    convert_rpt_to_txt(rpt_filename, txt_filename)
    print(f"Converted {rpt_filename} to {txt_filename}.")
