README

# Inicialitzacio
source venv/bin/activate

# requeriments
python3 -m pip install -r requirements.txt

# Use
Gather data using NDIAnalysis. Use /time:xx for better results (Ctrl+C tents to abrupt ends)
NDIAnalysis.exe /source:"TALKSHOW01 (VCONF 7)" /time:300 > TALKSHOW01_VCONF7_2.txt
Move file to the computer with this software
python3 ndi-graph-analysis.py -f TALKSHOW01_VCONF7_2.txt

Output at TALKSHOW01_VCONF7_2.txt.png