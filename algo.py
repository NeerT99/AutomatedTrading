# Import the necessary modules
import algoTrader
import time
from datetime import datetime

# Set the interval and number of hours to run for
INTERVAL = 0.2
HOURS = 1

# Calculate the total number of minutes and intervals
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
minutes = HOURS * 60
runtime = int(minutes / INTERVAL)
sleeptime = INTERVAL * 60 # Run for 1hr with intervals of 5mins
i = 0

# Print a message to indicate that the loop is starting
print(current_time+':', 'Algo is Running...')

# Start the while loop
while i < runtime:
    # Sleep for the specified amount of time
    time.sleep(sleeptime)

    # Print the current time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time+':')

    # Run the algoTrader function and handle any errors
    try:
        algoTrader.algoTrader()
        i = i + 1

    except:
        print('Error...')
        i = i + 1

# Print a final message when the loop has finished running
print(
    'The Money Printer has Finished Running...', '\n',
    'Please Contact Jerome Powell to Restart it.'
    )

