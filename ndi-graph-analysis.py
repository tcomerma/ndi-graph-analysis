#####################################################################
#  ndi-graph-analysis.py
#
#  Genera gràfiques a partir del output de l'eina d'analisi de Newtek
#
#####################################################################

# Imports
import textfsm
import matplotlib.pyplot as plt
import numpy
import argparse
import datetime
import csv


def is_float(value):
    try:
        float(value)
        return True
    except:
        return False


def cm_to_inch(value):
    return value/2.54


def convert_date_delta(data):
    t = ""
    delta = 0
    for i in data:
        if t == "":
            i['delta'] = 0
            t = datetime.datetime.strptime(i['Timestamp'], '%H:%M:%S.%f')
        else:
            i['delta'] = delta + \
                (datetime.datetime.strptime(
                    i['Timestamp'], '%H:%M:%S.%f') - t).microseconds
            delta = i['delta']
            i['delta'] /= 1000
            t = datetime.datetime.strptime(i['Timestamp'], '%H:%M:%S.%f')


def convert_text_2_float(data):
    fields = ['Framerate', 'Average_video_bitrate', 'Min_video_delay_recv', 'Avg_video_delay_recv',
              'Dev_video_delay_recv', 'Max_video_delay_recv', 'Min_video_delay_send', 'Avg_video_delay_send',
              'Dev_video_delay_send', 'Max_video_delay_send']
    for i in fields:
        for j in data:
            j[i] = float(j[i]) if is_float(j[i]) else 0


def create_graph(data, name):
    time = [i['delta'] for i in data]
    bitrate = [i['Average_video_bitrate'] for i in data]
    bitrate_avg = sum(bitrate)/len(bitrate)

    fig, (ax1, ax2, ax3) = plt.subplots(3, constrained_layout=True)
    fig.suptitle(f'graphs for {name}. 5 secs/sample')
    fig.set_figheight(cm_to_inch(29.7))
    fig.set_figwidth(cm_to_inch(21))

    ax1.set(xlabel='time (s)', ylabel='bitrate (Mbps)', title="Video data rate")
    ax1.set_ylim([0, 1.20*max(bitrate)])
    ax1.grid(True)
    ax1.plot(time, bitrate, label=f"bitrate ({bitrate_avg:.2f})")
    ax1.legend()

    Min = [i['Min_video_delay_send'] for i in data]
    Avg = [i['Avg_video_delay_send'] for i in data]
    Max = [i['Max_video_delay_send'] for i in data]
    Dev_up = [(i['Avg_video_delay_send'] + i['Dev_video_delay_send'])
              for i in data]
    Dev_down = [(i['Avg_video_delay_send'] - i['Dev_video_delay_send'])
                for i in data]
    Dev = [i['Dev_video_delay_send'] for i in data]
    Min_avg = sum(Min)/len(Min)
    Max_avg = sum(Max)/len(Max)
    Avg_avg = sum(Avg)/len(Avg)
    Dev_avg = sum(Dev)/len(Dev)
    ax2.set(xlabel='time (s)', ylabel='time between frames (ms)',
            title="Video @sender")
    ax2.grid(True)
    ax2.plot(time, Max, label=f"max ({Max_avg:.2f})")
    ax2.plot(time, Avg, label=f"avg ({Avg_avg:.2f})")
    ax2.plot(time, Min, label=f"min ({Min_avg:.2f})")
    ax2.fill_between(time, Dev_up, Dev_down, alpha=0.2, label=f"dev ({Dev_avg:.2f})")
    ax2.legend()

    Min = [i['Min_video_delay_recv'] for i in data]
    Avg = [i['Avg_video_delay_recv'] for i in data]
    Max = [i['Max_video_delay_recv'] for i in data]
    Dev_up = [(i['Avg_video_delay_recv'] + i['Dev_video_delay_recv'])
              for i in data]
    Dev_down = [(i['Avg_video_delay_recv'] - i['Dev_video_delay_recv'])
                for i in data]
    Dev = [i['Dev_video_delay_recv'] for i in data]
    Min_avg = sum(Min)/len(Min)
    Max_avg = sum(Max)/len(Max)
    Avg_avg = sum(Avg)/len(Avg)
    Dev_avg = sum(Dev)/len(Dev)
    ax3.set(xlabel='time (s)', ylabel='time between frames (ms)',
            title="Video @receiver")
    ax3.grid(True)
    ax3.plot(time, Max, label=f"max ({Max_avg:.2f})")
    ax3.plot(time, Avg, label=f"avg ({Avg_avg:.2f})")
    ax3.plot(time, Min, label=f"min ({Min_avg:.2f})")
    ax3.fill_between(time, Dev_up, Dev_down, alpha=0.2, label=f"dev ({Dev_avg:.2f})")
    ax3.legend()

    plt.savefig(name + ".png", bbox_inches='tight')
    plt.close()

def create_graph_csv(data, name):

    time = [i[0] for i in data] 
    dtime = [i[1] for i in data]

    fig, (ax1) = plt.subplots(1, constrained_layout=True)
    fig.suptitle(f'graphs for {name}')
    fig.set_figheight(cm_to_inch(10))
    fig.set_figwidth(cm_to_inch(21))

    ax1.set(xlabel='frame', ylabel='delta ms', title="ms from previous frames")
    ax1.set_ylim([0, max(dtime)])
    ax1.grid(True)
    ax1.plot(dtime)
    #ax1.legend()

    plt.savefig(name + ".png", bbox_inches='tight')
    plt.close()

def read_csv (r, c, f):
    format = ""

    for row in r:
        d = datetime.datetime.fromtimestamp(float(row['Timecode (ms)'])/10000000.0)
        d = d.strftime('%H:%M:%S.%f')
        # Detection in format changes
        new_format = "{}x{}, {}fps, {}, codec {}".format(row['X resolution'], row['Y resolution'], row['frame-rate'], row['frame type'], row['codec'])
        if format != new_format:
            f[d] = new_format
            format = new_format
        # Parsing useful data
        c.append([d, float(row['dTime (ms)'])])


def main():
    TEMPLATE_FILE = "templates/ndi-analysis.template".format()
    csv_data = []
    format_data = {}

    # Parse command line

    parser = argparse.ArgumentParser(description='Process line parameters.')
    parser.add_argument('--file', '-f', dest='file',
                        help='file with ndi analysis results')
    parser.add_argument('--csv', '-c', dest='csv_file', required=False,
                        help='file with ndi analysis results in csv format')
    args = parser.parse_args()

    if (args.file is None):
        print("No file indicated")
        exit(1)

    # Open file and template
    try:
        template = open(TEMPLATE_FILE)
        re_table = textfsm.TextFSM(template)
    except Exception as e:
        print(f"Problems opening template file {TEMPLATE_FILE}")
        print(e)
        exit(2)
    try:
        with open(args.file, 'r') as file:
            raw_data = file.read()
    except Exception as e:
        print(f"Problems opening file {args.file}")
        print(e)
        exit(3)

   # Open csv
    if args.csv_file:
        try:
            with open(args.csv_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',' )
                read_csv (reader, csv_data, format_data)

        except Exception as e:
            print(f"Problems opening csv file {args.csv_file}")
            print(e)
            exit(5)
    # Parse file
    try:
        data = re_table.ParseTextToDicts(raw_data)
    except Exception as e:
        print(f"Problems partsing file {args.file}")
        print(e)
        exit(4)
    # Check if empty (Stream was not running)
    if (len (data) == 0):
        print("No stream received. Sure it was really on?")
        exit(5)
    # Check if last record is OK
    if (data[len(data)-1]['Timestamp']) == "":
        del data[len(data)-1]
    # Process data from file, adding information

    convert_date_delta(data)
    convert_text_2_float(data)
    create_graph(data, args.file)
    if args.csv_file:
        create_graph_csv(csv_data, args.csv_file)
    


if __name__ == "__main__":
    main()

    exit(0)
