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

    fig, (ax1, ax2, ax3) = plt.subplots(3, constrained_layout=True)
    fig.suptitle(f'graphs for {name}. 5 secs/sample')
    fig.set_figheight(cm_to_inch(29.7))
    fig.set_figwidth(cm_to_inch(21))
    # fig.tight_layout()
    ax1.set(xlabel='time (s)', ylabel='bitrate (Mbps)', title="Video data rate")
    ax1.grid(True)
    ax1.plot(time, bitrate, label='bitrate')
    ax1.legend()

    Min = [i['Min_video_delay_send'] for i in data]
    Avg = [i['Avg_video_delay_send'] for i in data]
    Max = [i['Max_video_delay_send'] for i in data]
    Dev_up = [(i['Avg_video_delay_send'] + i['Dev_video_delay_send'])
              for i in data]
    Dev_down = [(i['Avg_video_delay_send'] - i['Dev_video_delay_send'])
                for i in data]
    Min_avg = sum(Min)/len(Min)
    Max_avg = sum(Max)/len(Max)
    Avg_avg = sum(Avg)/len(Avg)
    Dev_avg = sum(Dev_up)/len(Dev_up) - Avg_avg
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
    Min_avg = sum(Min)/len(Min)
    Max_avg = sum(Max)/len(Max)
    Avg_avg = sum(Avg)/len(Avg)
    Dev_avg = sum(Dev_up)/len(Dev_up) - Avg_avg
    ax3.set(xlabel='time (s)', ylabel='time between frames (ms)',
            title="Video @receiver")
    ax3.grid(True)
    ax3.plot(time, Max, label=f"max ({Max_avg:.2f})")
    ax3.plot(time, Avg, label=f"avg ({Avg_avg:.2f})")
    ax3.plot(time, Min, label=f"min ({Min_avg:.2f})")
    ax3.fill_between(time, Dev_up, Dev_down, alpha=0.2, label=f"dev ({Dev_avg:.2f})")
    ax3.legend()


#    Min = [i['Min_video_delay_recv'] - i['Min_video_delay_send'] for i in data]
#    Avg = [i['Avg_video_delay_recv'] - i['Avg_video_delay_send'] for i in data]
#    Max = [i['Max_video_delay_recv'] - i['Max_video_delay_send'] for i in data]
#    ax4.set(xlabel='time (s)', ylabel='time between frames (ms)',
#            title="Video @receiver - @ sender")
#    ax4.grid(True)
#    ax4.plot(time, Max, label='max')
#    ax4.plot(time, Avg, label='avg')
#    ax4.plot(time, Min, label='min')
#    ax4.legend()

    plt.savefig(name + ".png", bbox_inches='tight')
    plt.close()


def main():
    TEMPLATE_FILE = "templates/ndi-analysis.template"

    # Parse command line

    parser = argparse.ArgumentParser(description='Process line parameters.')
    parser.add_argument('--file', '-f', dest='file',
                        help='file with ndi analysis results')
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


if __name__ == "__main__":
    main()

    exit(0)
