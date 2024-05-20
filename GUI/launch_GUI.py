import tkinter as tk
from tkinter import filedialog, simpledialog
from FaultPlotter import FaultPlotter
from BlindReceiverHighlighter import BFHighlighter

class GUI:
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Alvin's PEPSICO Data Analysis Suite")

        browse_button = tk.Button(self.root, text="Highlight Blind Receiver (.rpt)", command=self.browse_rpt)
        browse_button.pack(pady=20)

        plot_button = tk.Button(self.root, text="Plot Fault Data (.csv)", command=self.browse_csv)
        plot_button.pack(pady=20)

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


if __name__ == "__main__":
    GUI()
