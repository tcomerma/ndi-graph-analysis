# NDI-GRAPH-ANALYSIS

Tool to graph the results of NDIAnalysis.exe and make trobleshooting easier.

## Author
Toni Comerma
march 2021

# Samples
You can find samples of NDIAnalysis output at /samples along with some graphs like [this](samples/C9-Cam2.txt.png) and [that](samples/TALKSHOW01_VCONF7_3.txt.png)

# Usage
## First time

- Download
- Load environment
```
source venv/bin/activate
```
- Install dependencies
```
python3 -m pip install -r requirements.txt
```

## Use
- If using virtualenv
```
source venv/bin/activate
```
- Gather data using NDIAnalysis. Use /time:xx for better results (Ctrl+C tents to abrupt ends)
```
NDIAnalysis.exe /source:"TALKSHOW01 (VCONF 7)" /time:300 > TALKSHOW01_VCONF7_2.txt
```
- Move file to the computer with this software
- Run the took
```
python3 ndi-graph-analysis.py -f TALKSHOW01_VCONF7_2.txt
```
Output at TALKSHOW01_VCONF7_2.txt.png

## Results

### Video data rate
Overall bandwith of the stream

### Video @sender 
Inter-frame time as created at sender. High variance could be a symptom of problems at the source device (cpu, too many clients,...).
Time hould be around 1000/framerate. e.g. 25fps=40, 50fps=20,...
### Video @receiver
Inter-frame time as receiver by NDIAnalysis.exe. High variance indicates problems during transmision (most likely network) 

### Video @receiver - @sender
The result of substracting both values. Could help to diagnose network issues

## Notes
- Do not move/minimize/... the window where NDIAnalysis.exe is running. It will alter the results.