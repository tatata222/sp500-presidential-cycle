from bs4 import BeautifulSoup
import json

with open('yearly_chart.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')
    
scripts = soup.find_all('script')
# Find the script containing Plotly data
for script in scripts:
    if script.string and 'Plotly.newPlot(' in script.string:
        print("Found Plotly data!")
        # We can extract the args.
        start_idx = script.string.find('[{"')
        end_idx = script.string.find('}],', start_idx) + 2
        try:
            data = json.loads(script.string[start_idx:end_idx])
            print(f"Num traces: {len(data)}")
            # just output type of trace 0
            print(f"Trace 0 type: {data[0]['type']}")
        except Exception as e:
            print("Failed to parse json:", e)
