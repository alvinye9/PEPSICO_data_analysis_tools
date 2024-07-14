import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext
from FaultPlotter import FaultPlotter
from BlindReceiverHighlighter import BFHighlighter
from RecirculationProcessor import RecirculationProcessor
from MixIdentifier import MixIdentifier
import sys
from PIL import Image, ImageTk
import os
import warnings

# Suppress the specific FutureWarning from pandas globally
warnings.simplefilter(action='ignore', category=FutureWarning)
class GUI:
    def __init__(self):
        # Create the output directory to store subsequent files
        output_dir = "./Data_Analysis_Suite_Output_Files"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.root = tk.Tk()
        self.root.title("Alvin's PEPSICO Data Analysis Suite")
        
        # # Determine the path to the image
        # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        # image_path = os.path.join(base_path,  'logo.png')
        
        # # Load and resize the image
        # self.original_image = Image.open(image_path)
        # self.resized_image = self.original_image.resize((150, 100), Image.LANCZOS)
        # self.logo = ImageTk.PhotoImage(self.resized_image)

        # # Create a label for the image and place it at the top left corner
        # logo_label = tk.Label(self.root, image=self.logo)
        # logo_label.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)
        
        self.create_buttons_with_info()

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=30)
        self.text_area.pack(pady=20)

        sys.stdout = TextRedirector(self.text_area, "stdout")
        sys.stderr = TextRedirector(self.text_area, "stderr")

        self.root.mainloop()

    def create_buttons_with_info(self):
        # Create buttons with info
        self.create_button_with_info("Highlight Blind Receiver (.rpt)", self.browse_rpt, 
                                     "How to Gather Dataset From ICS:\n 1. Reports -> Trip Operations -> Blind Receiver/Cover Sheet\n 2. Enter Trip #\n 3. Check 'Pallet Details'\n 4. Click checkmark at the top left of screen to export data")
        self.create_button_with_info("Plot Fault Data (.csv)", self.browse_csv, 
                                     "How to Gather Fault Data From ATOM:\n 1. Click Stats on the left tab\n 2. Select Vehicle Alarms\n 3. Select Vehicle Alarm Summary\n 4. Ensure group is 'Vehicle Alarm Type'\n 5. Select Date Range\n 6. Click execute\n 7. Click 'export' to export data")
        self.create_button_with_info("Process Recirculation Data (.rpt)", self.run_recirculation_processor, 
                                     "How to Gather Dataset from ICS:\n 1. Reports -> Warehouse Operations -> Location Event\n 2. For most accurate results, under 'Available Locations' select Fork_21 to Fork_25 ONLY\n 3. Click Green right arrow\n 4. Check 'all groups' and click green search button\n 5. Check 'all events' at the bottom of the screen\n 6. Click checkmark at the top left of screen to export data" )
        self.create_button_with_info("Process Pallet History Data (copy-and-paste))", self.show_mix_identifier_input,
                                     "How to Gather Pallet History Data from ICS:\n 1. Misc -> Pallet History\n 2. Input Desired Location and Timeframe\n 3. Copy all the Pallet History Info\n 4. Click 'Process Pallet History Data' button in Data Analysis Suite GUI\n 5. Paste coped info into large text box and enter Location into small text box") 
    
    def create_button_with_info(self, button_text, command, info_text):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, anchor=tk.W)

        # button = tk.Button(frame, text=button_text, command=command)
        button = tk.Button(frame, text=button_text, command=lambda: self.close_all_windows_and_execute(command))
        button.pack(side=tk.LEFT)

        info_button = tk.Button(frame, text="?", command=lambda: self.show_info(button_text, info_text), width=2)
        info_button.pack(side=tk.LEFT, padx=5)
        frame.pack(pady=10, anchor=tk.CENTER)

    def show_info(self, title, text):
        self.info_popup = tk.Toplevel(self.root)
        self.info_popup.title(title)
        self.info_popup.geometry("400x200")

        label = tk.Label(self.info_popup, text=text, wraplength=380, justify=tk.LEFT)
        label.pack(pady=10, padx=10)

        # close_button = tk.Button(self.info_popup, text="X", command=self.info_popup.destroy)
        # close_button.pack(pady=10)

    def browse_rpt(self):
        file_path = filedialog.askopenfilename(filetypes=[("RPT files", "*.rpt")])
        if file_path:
            BFH = BFHighlighter(file_path)
            BFH.create_pdf()

    def browse_csv(self):
        """
        Opens a file dialog to browse for a .csv file and plots the faults.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            fault_plotter = FaultPlotter(file_path)
            fault_plotter.plot_faults()
            # fault_plotter.plot_faults_html()

    def run_recirculation_processor(self):
        file_path = filedialog.askopenfilename(filetypes=[("RPT files", "*.rpt")])
        if file_path:
            RCProcessor = RecirculationProcessor(file_path)
            RCProcessor.create_sorted_csv()
            
    def show_mix_identifier_input(self):
        # Create a new window for input
        self.input_window = tk.Toplevel(self.root)
        self.input_window.title("Input Pallet History Data")

        # Create location entry
        self.location_label = tk.Label(self.input_window, text="Enter location here (e.g., AGVO_01):")
        self.location_label.pack(pady=5)
        self.location_entry = tk.Entry(self.input_window, width=50)
        self.location_entry.pack(pady=5)
        
        # Add a title or text above the larger text entry box
        self.text_entry_title = tk.Label(self.input_window, text="Paste Pallet History Data here:")
        self.text_entry_title.pack(pady=5)

        # Create text area for input text
        self.input_text_area = scrolledtext.ScrolledText(self.input_window, wrap=tk.WORD, width=100, height=10)
        self.input_text_area.pack(pady=10)

        # Create button to run MixIdentifier
        self.process_button = tk.Button(self.input_window, text="Run Mix Identifier", command=self.run_mix_identifier)
        self.process_button.pack(pady=10)

    def run_mix_identifier(self):
        location_input = self.location_entry.get()
        input_text = self.input_text_area.get("1.0", tk.END)
        mix_identifier = MixIdentifier(location_input, input_text)
        mix_identifier.update_values()
        # mix_identifier.plot_data()
        # mix_identifier.create_csv()
        
    def close_all_windows_and_execute(self, command):
        # Close all child windows
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        # Execute the command
        command()
    
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)

    def flush(self):
        pass

if __name__ == "__main__":
    GUI()
