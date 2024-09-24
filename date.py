import pandas as pd
from datetime import datetime

def format_date(date_str):
    """
    Function to convert a date string like 'February 28, 1963' into 'YYYY-MM-DD' format.
    """
    input_format = "%B %d, %Y"  # Example: February 28, 1963
    try:
        # Parse the date string to a datetime object
        date_obj = datetime.strptime(date_str, input_format)
        # Convert the datetime object to a string in 'YYYY-MM-DD' format
        output_format = "%Y-%m-%d"
        formatted_date = date_obj.strftime(output_format)
        return formatted_date
    except ValueError:
        # Handle the case if the date format is incorrect or missing
        return date_str

# Example dataframe with a date column
df = pd.DataFrame({
    'Name': ['John', 'Alice', 'Bob'],
    'Date of Birth': ['February 28, 1963', 'July 4, 1985', 'December 15, 1990']
})

# Apply the format_date function to the 'Date of Birth' column
df['Date of Birth'] = df['Date of Birth'].apply(format_date)

# Display the updated dataframe
print(df)
