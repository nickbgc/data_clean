import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Function to separate city and state
def separate_city_state(address):
    if not isinstance(address, str):  # check if the input is not a string
        return pd.Series([None, None])
    try:
        city, state = address.rsplit(' ', 1)
        return pd.Series([city.strip(), state.strip()])
    except ValueError:
        return pd.Series([address, None])

# Function to separate 5-digit ZIP and ZIP+4
def separate_zip_zip4(row):
    if '-' in row:
        zip5, zip4 = row.split('-', 1)
    elif len(row) == 9:
        zip5, zip4 = row[:5], row[5:]
    else:
        zip5, zip4 = row, None

    # Add leading zeros to 5-digit ZIP if its length is less than 5
    zip5 = zip5.zfill(5)
    return pd.Series([zip5, zip4], index=['5DigitZip', 'Zip+4'])

def clean_data(input_file, output_file):
    # Load the messy data using ISO-8859-1 encoding
    df = pd.read_csv(input_file, encoding='ISO-8859-1')

    # Create new columns based on the old ones
    df['name'] = df['1ST LINE OF NAME & ADDRESS']
    df['address'] = df['2ND LINE OF NAME & ADDRESS'] + ', ' + df['3RD LINE OF NAME & ADDRESS'] + ', ' + df['4TH LINE OF NAME & ADDRESS']
    df['city'] = df['5TH LINE OF NAME & ADDRESS']
    df['state'] = df['6TH LINE OF NAME & ADDRESS']
    df['zip'] = df['ZIP CODE FOR SORTING']
    df['cusip'] = df['CUSIP']

    # Trim extra spaces from the city column
    df['city'] = df['city'].str.strip()

    # Separate CITY and STATE where they are combined in CITY column
    df.loc[df['state'].isna(), ['city', 'state']] = df[df['state'].isna()]['city'].apply(separate_city_state)

    # Correct inconsistencies in ZIP
    df['zip'] = df['zip'].apply(lambda x: x if isinstance(x, str) and x.isnumeric() else 'UNKNOWN')

    # Apply the function to separate 5-digit ZIP and ZIP+4
    df[['5DigitZip', 'Zip+4']] = df['zip'].apply(separate_zip_zip4)

    # Replace 'UNKNOWN' and similar placeholders with NaN for a cleaner DataFrame
    df.replace('UNKNOWN', pd.NA, inplace=True)
    df.replace('None', pd.NA, inplace=True)
    df.replace('', pd.NA, inplace=True)

    # Drop the original columns
    columns_to_drop = [
        '1ST LINE OF NAME & ADDRESS', '2ND LINE OF NAME & ADDRESS', '3RD LINE OF NAME & ADDRESS',
        '4TH LINE OF NAME & ADDRESS', '5TH LINE OF NAME & ADDRESS', '6TH LINE OF NAME & ADDRESS',
        '7TH LINE OF NAME & ADDRESS', 'ZIP CODE FOR SORTING', 'CUSIP', 'zip', 'Zip+4'
    ]
    df = df.drop(columns=columns_to_drop)

    # Save the cleaned DataFrame
    df.to_csv(output_file, index=False)

def select_input_file():
    filepath = filedialog.askopenfilename(title="Select a CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    if filepath:
        input_file_var.set(filepath)

def select_output_file():
    filepath = filedialog.asksaveasfilename(title="Save cleaned file as", defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    if filepath:
        output_file_var.set(filepath)

def process_file():
    try:
        input_file = input_file_var.get()
        output_file = output_file_var.get()

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input and output files first!")
            return

        clean_data(input_file, output_file)

        messagebox.showinfo("Info", "File cleaned successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("CSV Cleaner")

input_file_var = tk.StringVar()
output_file_var = tk.StringVar()

tk.Label(app, text="Drag and drop a CSV file or select using the button below:").pack(pady=20)
tk.Button(app, text="Select Input CSV", command=select_input_file).pack(pady=10)
tk.Label(app, textvariable=input_file_var).pack(pady=10)
tk.Button(app, text="Select Save Location", command=select_output_file).pack(pady=10)
tk.Label(app, textvariable=output_file_var).pack(pady=10)
tk.Button(app, text="Start Cleaning", command=process_file).pack(pady=20)

app.mainloop()
