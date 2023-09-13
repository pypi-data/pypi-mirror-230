import pandas as pd
import numpy as np
import datetime

# Start and end date for the range
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 1, 2)  # Example: 1 day's range

# Generate Timestamps in 5-minute steps
date_range = pd.date_range(start=start_date, end=end_date, freq='5T').to_list()

# Remove the last timestamp to make it exactly one day (24*12 = 288 data points)
date_range.pop()

# Generate AvgValue values for each timestamp
avg_values = np.random.rand(len(date_range)) * 100

# Create the DataFrame
df = pd.DataFrame({
    'Timestamp': date_range,
    'AvgValue': avg_values
})

# Display the table
print(df)