import re
import matplotlib.pyplot as plt
import csv
from datetime import datetime

class MixIdentifier:
    def __init__(self, loc_input, text_input):
        self.location_input = loc_input
        self.input_text = text_input# Define the input text (copied from ICS)

        # Initialize lists to store extracted pallet IDs and timestamps
        self.to_pallets = []
        self.to_times = []
        self.from_pallets = []
        self.from_times = []
        self.timestamps = []
        self.time_range = ""
        self.unique_pallets = None

        # Define the pattern to match EVT2 lines with 'To AGVO_01' or 'From AGVO_01'
        self.pattern = re.compile(r'EVT2 Opr .*? Moved Moveable (\w+) From (\w+) .*? To (\w+) .*? Shift: C')
        self.time_pattern = re.compile(r'EVT1 (\w+ \d+ \d+:\d+:\d+) I-OPRMOVMOV')

    def update_values(self):
        try:
            # Iterate through the lines and extract the pallet IDs and timestamps
            current_time = None
            for line in self.input_text.split('\n'):
                time_match = self.time_pattern.match(line.strip())
                if time_match:
                    current_time = datetime.strptime(time_match.group(1), '%b %d %H:%M:%S')
                    self.timestamps.append(current_time)
                match = self.pattern.match(line.strip())
                if match:
                    pallet_id = match.group(1)
                    from_location = match.group(2)
                    to_location = match.group(3)
                    if to_location == self.location_input:
                        self.to_pallets.append(pallet_id)
                        self.to_times.append(current_time)
                    elif from_location == self.location_input:
                        self.from_pallets.append(pallet_id)
                        self.from_times.append(current_time)

            # Find the earliest and latest timestamps
            start_time = min(self.timestamps)
            end_time = max(self.timestamps)
            self.time_range = f"{start_time.strftime('%b %d %H:%M:%S')} - {end_time.strftime('%b %d %H:%M:%S')}"

            # Find unique pallets and maintain order
            self.unique_pallets = list(dict.fromkeys(self.to_pallets + self.from_pallets))
            self.plot_data()
            self.create_csv()
        except Exception as e:
            print(f"Pallet data not correctly formatted,  please check that you are only copying and pasting the correct info: {e}")


    def plot_data(self):
        # Plot the results
        plt.figure(figsize=(12, 8))

        # Draw text and lines
        for i, pallet_id in enumerate(self.unique_pallets):
            if pallet_id in self.to_pallets:
                plt.text(-0.05, self.to_pallets.index(pallet_id) , "(" + pallet_id + ") " + str(self.to_times[self.to_pallets.index(pallet_id)]), va='center', ha='right', fontsize=12, color='blue')
            if pallet_id in self.from_pallets:
                plt.text(1.05, self.from_pallets.index(pallet_id), "(" + pallet_id + ") " + str(self.from_times[self.from_pallets.index(pallet_id)]), va='center', ha='left', fontsize=12, color='green')
            if pallet_id in self.to_pallets and pallet_id in self.from_pallets:
                plt.plot([0, 1], [self.to_pallets.index(pallet_id), self.from_pallets.index(pallet_id)], 'k-', lw=1)
            plt.text(-0.5, -1.0, "To: " + self.location_input )
            plt.text(1.2, -1.0, "From: " + self.location_input )

        plt.gca().invert_yaxis()
        plt.xticks([0, 1], ['To AGVO_01', 'From AGVO_01'])
        plt.title(f'Pallet IDs To and From AGVO_01\nTime Range: {self.time_range}')
        plt.axis('off')

        plt.tight_layout()
        plt.savefig('./Data_Analysis_Suite_Output_Files/Pallet_History_Data_Diagram.png')
        plt.show()

    def create_csv(self):
        # Write the output to a CSV file
        with open('./Data_Analysis_Suite_Output_Files/Pallet_History_Data.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['To Pallet IDs', 'To Times', 'From Pallet IDs', 'From Times'])
            csv_writer.writerow([f'Time Range: {self.time_range}', '', '', ''])
            max_len = max(len(self.to_pallets), len(self.from_pallets))
            for i in range(max_len):
                to_pallet = self.to_pallets[i] if i < len(self.to_pallets) else ''
                to_time = self.to_times[i].strftime('%H:%M:%S') if i < len(self.to_times) else ''
                from_pallet = self.from_pallets[i] if i < len(self.from_pallets) else ''
                from_time = self.from_times[i].strftime('%H:%M:%S') if i < len(self.from_times) else ''
                csv_writer.writerow([to_pallet, to_time, from_pallet, from_time])

        print(f"CSV file 'Pallet_History_Data.csv' and image 'Pallet_History_Data_Diagram.png' created successfully.")

if __name__ == "__main__":
  input_text = """
    EVT1 Jul 13 15:00:16 I-OPRMOVMOV
    EVT2 Opr AGV19 Moved Moveable FE3VER9U From AGV19 (Type T) To AGVO_01 (Type S) With 48 Of 06508801 (070124) Shift: C
    EVT1 Jul 13 15:01:42 I-OPRMOVMOV
    EVT2 Opr AGV06 Moved Moveable FE3VETQX From AGV06 (Type T) To AGVO_01 (Type S) With 60 Of 10607301 (071524) Shift: C
    EVT1 Jul 13 15:05:56 I-OPRMOVMOV
    EVT2 Opr AGV09 Moved Moveable FE3VES7U From AGV09 (Type T) To AGVO_01 (Type S) With 66 Of 10525401 (070124) Shift: C
    EVT1 Jul 13 15:07:21 I-OPRMOVMOV
    EVT2 Opr AGV05 Moved Moveable FC3UP800 From AGV05 (Type T) To AGVO_01 (Type S) With 36 Of 09507001 (071524) Shift: C
    EVT1 Jul 13 15:10:43 I-OPRMOVMOV
    EVT2 Opr 331 Moved Moveable FE3VF45Y From AGVO_01 (Type S) To FORK28 (Type T) With 42 Of 11649201 (072924) Shift: C
    EVT1 Jul 13 15:12:36 I-OPRMOVMOV
    EVT2 Opr 344 Moved Moveable FE3VEU17 From AGVO_01 (Type S) To FORK60 (Type T) With 66 Of 10525401 (070124) Shift: C
    EVT1 Jul 13 15:13:19 I-OPRMOVMOV
    EVT2 Opr 371 Moved Moveable FE3VER9U From AGVO_01 (Type S) To FORK41 (Type T) With 48 Of 06508801 (070124) Shift: C
    EVT1 Jul 13 15:15:15 I-OPRMOVMOV
    EVT2 Opr 366 Moved Moveable FE3VETQX From AGVO_01 (Type S) To FORK75 (Type T) With 60 Of 10607301 (071524) Shift: C
    EVT1 Jul 13 15:41:56 I-OPRMOVMOV
    EVT2 Opr AGV12 Moved Moveable FE3VF45Y From AGV12 (Type T) To AGVO_01 (Type S) With 42 Of 11649201 (072924) Shift: C
    EVT1 Jul 13 15:43:14 I-OPRMOVMOV
    EVT2 Opr 371 Moved Moveable FE3VES7U From AGVO_01 (Type S) To FORK41 (Type T) With 66 Of 10525401 (070124) Shift: C
    EVT1 Jul 13 15:43:20 I-OPRMOVMOV
    EVT2 Opr AGV07 Moved Moveable FE3VF48R From AGV07 (Type T) To AGVO_01 (Type S) With 42 Of 11648701 (072924) Shift: C
    EVT1 Jul 13 15:48:56 I-OPRMOVMOV
    EVT2 Opr AGV10 Moved Moveable FE3VEXVQ From AGV10 (Type T) To AGVO_01 (Type S) With 42 Of 09019501 (071524) Shift: C
    EVT1 Jul 13 15:50:31 I-OPRMOVMOV
    EVT2 Opr 353 Moved Moveable FE3VF45Y From AGVO_01 (Type S) To FORK19 (Type T) With 42 Of 11649201 (072924) Shift: C
    EVT1 Jul 13 15:59:35 I-OPRMOVMOV
    EVT2 Opr 314 Moved Moveable FC3UP800 From AGVO_01 (Type S) To FORK39 (Type T) With 36 Of 09507001 (071524) Shift: C
    EVT1 Jul 13 16:00:20 I-OPRMOVMOV
    EVT2 Opr 371 Moved Moveable FE3VF48R From AGVO_01 (Type S) To FORK41 (Type T) With 42 Of 11648701 (072924) Shift: C
    EVT1 Jul 13 16:00:50 I-OPRMOVMOV
    EVT2 Opr 345 Moved Moveable FE3VEXVQ From AGVO_01 (Type S) To FORK79 (Type T) With 42 Of 09019501 (071524) Shift: C
    EVT1 Jul 13 16:13:37 I-OPRMOVMOV
    EVT2 Opr AGV07 Moved Moveable FE3VF4AS From AGV07 (Type T) To AGVO_01 (Type S) With 66 Of 10525001 (072924) Shift: C
    EVT1 Jul 13 16:15:56 I-OPRMOVMOV
    EVT2 Opr AGV16 Moved Moveable FE3VF4AN From AGV16 (Type T) To AGVO_01 (Type S) With 42 Of 11649201 (072924) Shift: C
    EVT1 Jul 13 16:18:28 I-OPRMOVMOV
    EVT2 Opr AGV13 Moved Moveable FE3VEN2E From AGV13 (Type T) To AGVO_01 (Type S) With 78 Of 08372901 (070124) Shift: C
    EVT1 Jul 13 16:19:58 I-OPRMOVMOV
    EVT2 Opr AGV10 Moved Moveable FE3VEW9M From AGV10 (Type T) To AGVO_01 (Type S) With 42 Of 09019501 (071524) Shift: C
    EVT1 Jul 13 16:25:47 I-OPRMOVMOV
    EVT2 Opr AGV06 Moved Moveable FE3VF4AZ From AGV06 (Type T) To AGVO_01 (Type S) With 36 Of 07717701 (071524) Shift: C
    EVT1 Jul 13 16:29:15 I-OPRMOVMOV
    EVT2 Opr AGV03 Moved Moveable FC3VGAUU From AGV03 (Type T) To AGVO_01 (Type S) With 48 Of 11646001 (071524) Shift: C
    EVT1 Jul 13 16:29:15 I-OPRMOVMOV
    EVT2 Opr 338 Moved Moveable FE3VF4AS From AGVO_01 (Type S) To FORK27 (Type T) With 66 Of 10525001 (072924) Shift: C
    EVT1 Jul 13 16:29:54 I-OPRMOVMOV
    EVT2 Opr 134 Moved Moveable FE3VF4AN From AGVO_01 (Type S) To FORK71 (Type T) With 42 Of 11649201 (072924) Shift: C
    EVT1 Jul 13 16:30:49 I-OPRMOVMOV
    EVT2 Opr 138 Moved Moveable FE3VEN2E From AGVO_01 (Type S) To FORK15 (Type T) With 78 Of 08372901 (070124) Shift: C
"""
  location_input = "AGVO_02"
  obj=MixIdentifier(location_input, input_text)
  obj.update_values()
  obj.plot_data()


