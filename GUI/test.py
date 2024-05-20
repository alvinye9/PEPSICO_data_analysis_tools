import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext
from FaultPlotter import FaultPlotter
from BlindReceiverHighlighter import BFHighlighter
import sys
from PIL import Image, ImageTk
import os

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alvin's PEPSICO Data Analysis Suite")
        
        # Determine the path to the image
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_path, 'resources', 'logo.png')
        
        # # Load and resize the image
        # self.original_image = Image.open(image_path)
        # self.resized_image = self.original_image.resize((150, 100), Image.LANCZOS)
        # self.logo = ImageTk.PhotoImage(self.resized_image)

        # # Create a label for the image and place it at the top left corner
        # logo_label = tk.Label(self.root, image=self.logo)
        # logo_label.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)
        
        browse_button = tk.Button(self.root, text="Highlight Blind Receiver (.rpt)", command=self.browse_rpt)
        browse_button.pack(pady=20)

        plot_button = tk.Button(self.root, text="Plot Fault Data (.csv)", command=self.browse_csv)
        plot_button.pack(pady=20)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=30)
        self.text_area.pack(pady=20)

        sys.stdout = TextRedirector(self.text_area, "stdout")
        sys.stderr = TextRedirector(self.text_area, "stderr")

        self.root.mainloop()

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
