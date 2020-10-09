import tkinter as tk
from tkinter import ttk
from scan_details import ScanDetails
import pandas as pd

class MainGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_intro_frame()
        self.create_explanation_frame()
        self.create_table_frame()
        self.create_bottom_frame()
        # self.create_widgets()

    def create_intro_frame(self):
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP,fill=tk.X)

        # Main label at the top
        self.main_label = tk.Label(self.top_frame)
        self.main_label.config(dict(
            text='CryptoScanner',
            font=("Courier", 30),
        ))
        self.main_label.pack(side=tk.TOP)

    def create_explanation_frame(self):
        self.explanation_frame = tk.Frame(self)
        self.explanation_frame.pack(fill=tk.X)

                # Scanner status explanation label
        texts = ['Scanner status explanation : ','● Stopped','● Initialising','● Running']
        colours = ['black','red','orange','green']

        for index,text in enumerate(texts):
            tk.Label(self.explanation_frame, text=text, fg=colours[index]).grid(row=1, column=index)
        
        tk.Button(self.explanation_frame, text='Add Scan', command=self.add_scan).grid(row=1, column=5)

    def create_table_frame(self):
        self.middle_frame = tk.Frame(self)
        self.middle_frame.pack(fill=tk.X)

        # Creating table headers
        headers = ('Status', 'Name', 'Exchange', 'Interval', 'Config Description')
        widths = [15, 15, 10, 10, 40]

        for index, header in enumerate(headers):
            tk.Label(
                self.middle_frame,
                text=header,
                width=widths[index],
                borderwidth=0,
                fg='white',
                bg='black',
                font=('Courier',12,'bold')
            ).grid(row=3, column=index, sticky="nsew", padx=1, pady=1)
        tk.Label(
                self.middle_frame,
                text='Actions',
                # width=widths[index],
                borderwidth=0,
                fg='white',
                bg='black',
                font=('Courier',12,'bold')
            ).grid(row=3, column=len(headers), columnspan=4, sticky="nsew", padx=1, pady=1)

        # Getting table data
        self.scan_table_data = self.initialise_scans_table()

        for row, row_data in self.scan_table_data.iterrows():
            for col, (col_name, col_data) in enumerate(row_data.items()):
                if col_name == 'status':
                    if col_data.lower() == 'running':
                        fg = 'green'
                    elif col_data.lower() == 'initialising':
                        fg = 'orange'
                    else:
                        fg = 'red'
                    tk.Label(self.middle_frame, text='● '+col_data, fg=fg).grid(row=4+row, column=col)
                elif col_name == 'config_description':
                    tk.Label(self.middle_frame, text=col_data, wraplength=300).grid(row=4+row, column=col)
                else:
                    tk.Label(self.middle_frame, text=col_data).grid(row=4+row, column=col)
            tk.Button(self.middle_frame, text='start', command=self.start_scan).grid(row=4+row, column=len(self.scan_table_data.columns))
            tk.Button(self.middle_frame, text='stop', command=self.stop_scan).grid(row=4+row, column=len(self.scan_table_data.columns)+1)
            tk.Button(self.middle_frame, text='edit', command=self.edit_scan).grid(row=4+row, column=len(self.scan_table_data.columns)+2)
            tk.Button(self.middle_frame, text='remove', command=self.remove_scan).grid(row=4+row, column=len(self.scan_table_data.columns)+3)

    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM,fill=tk.X)

        # Disclaimer label
        disclaimer_txt = '\n\n\n\nThe information provided here is for general information only. It should not be taken as constituting professional advice. We are not financial advisors. You should onsider seeking independent legal, financial, taxation or other advice to check how the tool information relates to your unique circumstances. We are not liable for any loss caused, whether due to negligence or otherwise arising from the use of, or reliance on, the information provided directly or indirectly, by the use of this tool.'
        disclaimer_label = tk.Label(self.bottom_frame)
        disclaimer_label.config(dict(
            text=disclaimer_txt,
            font=("Courier", 8),
            wraplength = 480,
        ))
        disclaimer_label.pack(
            side=tk.BOTTOM,
        )

    # command functions
    def add_scan(self):
        print("hi there, everyone!")

    def initialise_scans_table(self):
        data = {'status':['Running', 'Stopped', 'Initialising'],
                'name':['scanner 1', 'scanner 2', 'scanner 3'],
                'exchange':['binance', 'binance', 'binance'],
                'interval':['5m', '10m', '15m'],
                'config_description':['lalala','blahblahblah','all we ever do is blah blah blah and do actually care about what they say so yayaya'],}
        return pd.DataFrame(data)

    def start_scan(self):
        print('hellos')

    def stop_scan(self):
        print('str')
    
    def edit_scan(self):
        print('str')

    def remove_scan(self):
        print('str')

root = tk.Tk()
root.title("CryptoScanner")
root.geometry("850x400")
app = MainGui(master=root)
app.mainloop()







            # print(self.scan_table_data.columns)
        # for index, row in enumerate(self.scan_table_data['status']):
        #     if row.lower() == 'running':
        #         fg = 'green'
        #     elif row.lower() == 'initialising':
        #         fg = 'orange'
        #     else:
        #         fg = 'red'

        #     tk.Label(self.middle_frame, text='● '+row, fg=fg).grid(row=4+index, column=0)


        # for index, row in enumerate(self.scan_table_data[])

        # for index, header in enumerate(self.scan_table_data):
        #     if header['status'] == 'running':
        #         tag='green'
        #     elif header['status'] == :
        #         pass
        #     tk.Label(self.middle_frame, text=header[''])


        # list_box = ttk.Treeview(self.middle_frame, columns=headers, show='headings')
        # for index, header in enumerate(headers):
        #     tk.Label(self.middle_frame, text=header, bg='grey75').grid(row=3, column=index)
        #     list_box.heading(header, text=header)
        #     list_box.column(header, minwidth=widths[index], width=widths[index])

        # list_box.grid(row=3, column=0, columnspan=6)

        # df_col = self.scan_table_data.columns.values

        # print(tuple(self.scan_table_data.iloc[1,:]))
        # # listBox.insert("", "end", values=(i, name, score))
        # for i in range(len(self.scan_table_data)):
        #     data_row = self.scan_table_data.iloc[i,:]

        #     if data_row['status'].lower == 'running':
        #         tag='green'
        #     elif data_row['status'].lower == 'initialising':
        #         tag='orange'
        #     else:
        #         tag='red'
            
        #     values = tuple(data_row.tolist())
        #     print(values)
        #     # list_box.insert('', 2, values=values)
        #     list_box.insert('','end', values=tk.Button(self.middle_frame))
        #     # list_box.insert('', 'end', values=tuple(self.scan_table_data.iloc[i,:]))


# status_explanation_label = tkinter.Label(window)
# status_explanation_label.config(dict(
#     text=''
# ))

# add_scan_button = tkinter.Button(window)
# add_scan_button.config(dict(
#     text='Add Scan'
# ))



# button_widget = tkinter.Button(window,text="Welcome to DataCamp's Tutorial on Tkinter")


# # Placing widgets into window
# main_label.place()


# tkinter.mainloop()

