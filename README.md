# NDI-GRAPH-ANALYSIS

Tool to graph the results of NDIAnalysis.exe and make trobleshooting easier.

## Author
Toni Comerma
march 2021


# Usage
## First time

- Download
- Load environment
'''
source venv/bin/activate
'''
- Install dependencies
'''
python3 -m pip install -r requirements.txt
'''

## Use
- If using virtualenv
'''
source venv/bin/activate
'''
- Gather data using NDIAnalysis. Use /time:xx for better results (Ctrl+C tents to abrupt ends)
'''
NDIAnalysis.exe /source:"TALKSHOW01 (VCONF 7)" /time:300 > TALKSHOW01_VCONF7_2.txt
'''
- Move file to the computer with this software
- Run the took
'''
python3 ndi-graph-analysis.py -f TALKSHOW01_VCONF7_2.txt
'''
Output at TALKSHOW01_VCONF7_2.txt.png