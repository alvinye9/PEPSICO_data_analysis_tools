import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import webbrowser

class FaultPlotter:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def plot_faults(self):
        try:
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

            # Create a pivot table for easier plotting, sorted by Vehicle Number
            pivot_table = melted_data.pivot(index='Vehicle Number', columns='Fault Type', values='Fault Count').fillna(0)
            pivot_table = pivot_table.sort_index()

            # Create the interactive plot
            fig = go.Figure()

            # Add bars for each fault type
            for fault_type in pivot_table.columns:
                fig.add_trace(
                    go.Bar(
                        x=pivot_table.index.astype(str),
                        y=pivot_table[fault_type],
                        name=fault_type,
                    )
                )

            # Add annotations for the total faults
            for i, total in enumerate(vehicle_totals):
                fig.add_annotation(
                    x=str(i),  
                    y=total,
                    text=str(int(total)),
                    showarrow=False,
                    xref="x",
                    yshift=10,
                    font=dict(size=12, color='black')
                )

            # Update the layout to include an interactive legend
            fig.update_layout(
                barmode='stack',
                xaxis_title='Vehicle Number',
                yaxis_title='Fault Count',
                title='Faults by Vehicle Number',
                legend_title='Fault Types',
                hovermode='closest'
            )
            # Save the plot as a PNG file
            fig.write_image('Fault_Data.png')
            print("The plot has been saved as 'Fault_Data.png'")
            
            # Save the plot to an HTML file and open it in a browser
            fig.write_html('Fault_Data.html')
            webbrowser.open_new('Fault_Data.html')


            
        except pd.errors.EmptyDataError:
            print("Error: The CSV file is empty.")
        except pd.errors.ParserError:
            print("Error: The CSV file format is incorrect.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Usage example
plotter = FaultPlotter('path_to_your_file.csv')
plotter.plot_faults()
