import pandas as pd
import matplotlib.pyplot as plt
import webbrowser

class FaultPlotter:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def plot_faults(self):
    # Read the CSV file, skipping the first row
        data = pd.read_csv(self.csv_file_path, skiprows=1, header=None)

        # Dynamically rename the columns based on the number of columns in the data
        num_columns = data.shape[1]
        column_names = ['Name'] + [str(i) for i in range(1, num_columns - 1)] + ['Total']
        data.columns = column_names

        # Calculate the total faults for each vehicle (sum across columns, excluding the first column and first row)
        vehicle_totals = data.iloc[1:, 1:-1].sum(axis=0)

        # Drop the 'Total' column before transposing
        data = data.drop(columns=['Total'])

        # Transposing the data to align it correctly
        data = data.set_index('Name').transpose().reset_index()

        # Renaming the index column
        data.rename(columns={'index': 'Vehicle Number'}, inplace=True)

        # Convert Vehicle Number to int for proper sorting
        data['Vehicle Number'] = data['Vehicle Number'].astype(int)

        # Melt the DataFrame to long format for easier plotting
        melted_data = data.melt(id_vars=['Vehicle Number'], var_name='Fault Type', value_name='Fault Count')

        # Convert Fault Count to numeric, forcing errors to NaN
        melted_data['Fault Count'] = pd.to_numeric(melted_data['Fault Count'], errors='coerce')

        # Replace NaN values with 0
        melted_data['Fault Count'].fillna(0, inplace=True)

        # Filter out the 'Name' from the Fault Type
        melted_data = melted_data[melted_data['Fault Type'] != 'Name']

        # Sort the melted data by Vehicle Number
        melted_data = melted_data.sort_values(by='Vehicle Number')

        # Plotting the stacked bar graph
        plt.figure(figsize=(18, 10))  # Increase the figure size for a larger plot

        # Create a pivot table for easier plotting, sorted by Vehicle Number
        pivot_table = melted_data.pivot(index='Vehicle Number', columns='Fault Type', values='Fault Count').fillna(0)
        pivot_table = pivot_table.sort_index()

        # Plot each fault type in a stacked manner
        bottom = None
        colors = plt.cm.get_cmap('tab20', len(pivot_table.columns))

        for i, fault_type in enumerate(pivot_table.columns):
            bars = plt.bar(pivot_table.index.astype(str), pivot_table[fault_type], bottom=bottom, label=fault_type, color=colors(i))
            if bottom is None:
                bottom = pivot_table[fault_type]
            else:
                bottom += pivot_table[fault_type]

        # Calculate the maximum bar height for y-axis limit adjustment
        max_height = vehicle_totals.max()
        plt.ylim(0, max_height + 10)

        # Annotating the bars with the total number of faults for each vehicle
        for i, total in enumerate(vehicle_totals):
            plt.text(i, total, f'{int(total)}', ha='center', va='bottom')

        plt.xlabel('Vehicle Number')
        plt.ylabel('Fault Count')
        plt.title('Faults by Vehicle Number')
        plt.xticks(rotation=90)
        plt.grid(axis='y')

        # Adjust the legend to be below the plot and reduce font size
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), title='Fault Types', ncol=4, fontsize='small')

        # Adjust layout to make space for the legend
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig("Fault_Data.jpg")
        webbrowser.open_new('Fault_Data.jpg')
        plt.show()
