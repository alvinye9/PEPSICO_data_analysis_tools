import csv
import re
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import webbrowser

## INCLUDE NOTE IN GUI TO ONLY EXPORT DATA FOR FORK_21 TO FORK_25
class RecirculationProcessor:
    def __init__(self, csv_file_path):
        # Define the input file name
        self.input_file = csv_file_path
        # circulation_data = defaultdict(list)
        # self.create_sorted_csv(input_file)
        # self.plot_data(circulation_data)
        self.datetime_entries = []

    def create_sorted_csv(self):
        # Define the headers for the CSV file
        headers = ["Location", "Operator", "Event", "Pallet ID", "Product", "Description", "Code Date", "Number of Cases", "Date", "Time"]

        # Initialize data structures
        circulation_data = defaultdict(list)
        datetime_entries = self.datetime_entries

        # Read the input file
        with open(self.input_file, "r") as file:
            lines = file.readlines()

        # Define a regex pattern to match the relevant rows
        pattern = re.compile(r'^\s*(\w+)?\s+(\w+)\s+(Pallet Moved (From|To))\s+(\w+)\s+(\w+)\s+(.+?)\s+(\d{6})\s+(\d+)\s+(\d{2}/\d{2})\s+(\d{2}:\d{2})$')

        # Store the last known location to handle lines without location information
        last_location = ""

        # Process each line directly to extract data
        for line in lines:
            match = pattern.match(line)
            if match:
                event = match.group(3).strip()
                if event == "Pallet Moved To":
                    location = match.group(1) if match.group(1) else last_location
                    operator = match.group(2)
                    pallet_id = match.group(5)
                    product = match.group(6)
                    description = match.group(7).strip()
                    code_date = match.group(8)
                    number_of_cases = match.group(9)
                    date = match.group(10)
                    time = match.group(11)

                    # Update the last known location
                    last_location = location

                    # Append the extracted data to the circulation data
                    row = {
                        "Location": location,
                        "Operator": operator,
                        "Event": event,
                        "Pallet ID": pallet_id,
                        "Product": product,
                        "Description": description,
                        "Code Date": code_date,
                        "Number of Cases": number_of_cases,
                        "Date": date,
                        "Time": time
                    }
                    circulation_data[pallet_id].append(row)
                    datetime_entries.append(f"{date} {time}")

        # Sort the pallet IDs by the number of circulations, descending
        sorted_circulation_data = sorted(circulation_data.items(), key=lambda x: len(x[1]), reverse=True)

        # Write the sorted circulation data to a new CSV file
        output_circulation_file = "./Data_Analysis_Suite_Output_Files/circulation_data_sorted.csv"
        with open(output_circulation_file, 'w', newline='') as csvfile:
            fieldnames = ['Pallet ID', 'Product ID', 'Circulation Number', 'Location (Inflow)', 'Date', 'Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for pallet_id, entries in sorted_circulation_data:
                if len(entries) > 1:  # Only consider pallet IDs that appear more than once
                    for i, entry in enumerate(entries):
                        writer.writerow({
                            'Pallet ID': pallet_id,
                            'Product ID': entry['Product'],
                            'Circulation Number': i + 1,
                            'Location (Inflow)': entry['Location'],
                            'Date': entry['Date'],
                            'Time': entry['Time']
                        })

        print(f"Circulation data has been successfully written to {output_circulation_file} saved in ./Data_Analysis_Suite_Output_Files")
        webbrowser.open(output_circulation_file)
        self.plot_data(circulation_data)


    def plot_data(self,circulation_data):
        # Get the number of recirculations for each pallet ID
        recirculation_counts = {k: len(v) for k, v in circulation_data.items() if len(v) > 1}
        
        # Count occurrences of each recirculation count
        occurrence_counts = Counter(recirculation_counts.values())

        # Prepare data for plotting
        recirculation_numbers = sorted(occurrence_counts.keys())
        occurrences = [occurrence_counts[n] for n in recirculation_numbers]

        # Sort datetime entries to find the earliest and latest
        datetime_entries = sorted(self.datetime_entries)
        earliest_datetime = datetime_entries[0]
        latest_datetime = datetime_entries[-1]

        # Create the plot
        plt.figure(figsize=(10, 6))
        bars = plt.bar(recirculation_numbers, occurrences, color='skyblue')
        plt.xlabel('Number of Recirculations')
        plt.ylabel('Occurrence of Recirculation Counts')
        plt.title(f'Number of Recirculations From {earliest_datetime} to {latest_datetime}')
        plt.xticks(recirculation_numbers)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()

        # Annotate each bar with the count
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', fontweight='bold')

        # Save the plot
        output_plot = './Data_Analysis_Suite_Output_Files/recirculation_data_plot.png'
        plt.savefig(output_plot)

        print(f"Circulation data has been successfully plotted to {output_plot} saved in ./Data_Analysis_Suite_Output_Files")
        plt.show()

    # if __name__ == "__main__":
    #     obj=RecirculationProcessor('input_2.rpt')
    #     obj.create_sorted_csv()
    #     print("done")
