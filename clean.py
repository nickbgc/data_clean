import pandas as pd

# Function to separate city and state
def separate_city_state(address):
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

# Load the messy data (replace 'messy_data.csv' with your actual file path)
df = pd.read_csv('messy_data.csv')

# Your initial column renaming and cleaning steps here

# Trim extra spaces from the CITY column
df['CITY'] = df['CITY'].str.strip()

# Separate CITY and STATE where they are combined in CITY column
df.loc[df['STATE'].isna(), ['CITY', 'STATE']] = df[df['STATE'].isna()]['CITY'].apply(separate_city_state)

# Correct inconsistencies in ZIP
df['ZIP'] = df['ZIP'].apply(lambda x: x if x.isnumeric() else 'UNKNOWN')

# Apply the function to separate 5-digit ZIP and ZIP+4
df[['5DigitZip', 'Zip+4']] = df['ZIP'].apply(separate_zip_zip4)

# Replace 'UNKNOWN' and similar placeholders with NaN for a cleaner DataFrame
df.replace('UNKNOWN', pd.NA, inplace=True)
df.replace('None', pd.NA, inplace=True)
df.replace('', pd.NA, inplace=True)

# Save the cleaned DataFrame (replace 'cleaned_data.csv' with your desired output file path)
df.to_csv('cleaned_data.csv', index=False)
