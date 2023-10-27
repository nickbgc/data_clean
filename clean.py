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

# Load the messy data using ISO-8859-1 encoding
df = pd.read_csv('IBNmessy.csv', encoding='ISO-8859-1')

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
df.to_csv('cleaned_data.csv', index=False)
