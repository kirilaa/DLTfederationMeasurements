import matplotlib.pyplot as plt
import json
import time
import sys
import os
import numpy as np
import csv
import collections
from numpy.core.defchararray import greater

from numpy.core.numeric import NaN

# results_path= "../cosmos_results/results/" #WORKS
# results_path= "../tender_results/results/" #WORKS
# results_path= "../eth_ath_all_verifiers_GOOD_results/results/" #WORKS
# results_path= "../eth_pow_all_miners_active/results/" #WORKS
# results_path= "../broken_results/cosmos_results/psutil/"

# results_path= "../cosmos_results/psutil/"
# results_path= "../tender_results/psutil/"
results_path= "../eth_ath_all_verifiers_GOOD_results/psutil/"
# results_path= "../eth_pow_all_miners_active/psutil/"

output_filename = 'eth_auth_'
# output_filename = 'eth_pow_'
# output_filename = 'cosmos_'
# output_filename = 'tender_'


nodes = ["10", "20", "30"]
measures = ["time", "cpu", "mem", "disk_busy", "disk_write","disk_read", "net_send", "net_rcv"]
notime_measures = [ "cpu", "mem", "disk_busy", "disk_write","disk_read", "net_send", "net_rcv"]

sample = 10


def open_csv(filename):
    
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            row = row[:-1]
            time_val = [float(str(value).split(",")[0]) for value in row]
            cpu_val = [float(str(value).split(",")[1]) for value in row]
            mem_val = [float(str(value).split(",")[2]) for value in row]
            disk_busy_val = [float(str(value).split(",")[3]) for value in row]
            disk_write_val = [float(str(value).split(",")[4]) for value in row]
            disk_read_val = [float(str(value).split(",")[5]) for value in row]
            net_send_val = [float(str(value).split(",")[6]) for value in row]
            net_rcv_val = [float(str(value).split(",")[7]) for value in row]
            
            new_list = {
                "time":time_val, 
                "cpu": cpu_val,
                "mem": mem_val,
                "disk_busy": disk_busy_val,
                "disk_write": disk_write_val,
                "disk_read": disk_read_val,
                "net_send": net_send_val,
                "net_rcv": net_rcv_val
                }
            
    return new_list

def zero_data(data):
    start = collections.defaultdict(dict)
    for node in nodes:
        for i in range(0,len(data[node])):
            start[node][i] = float(data[nodes[0]][i]["time"][0])

    for node in nodes:
        for i in range(0,len(data[node])):
            # start = float(data[nodes[0]][i]["time"][0])
            for j in range(0, len(data[node][i]["time"])):
                # data[node][i]["time"][:] = [float(value) - start for value in data[node][i]["time"]]
                data[node][i]["time"][j] = data[node][i]["time"][j] - start[node][i]
    return data

def increase_difference(data):
    data_diff = [ data[n] - data[n-1] for n in range(1, len(data))]
    return data_diff    

def modifyData(data, keys):
    for key in keys:
        for node in nodes:
            for i in range(1,len(data[node])):
                # print(node,key)
                data[node][i][key][1:] = increase_difference(data[node][i][key])
                data[node][i][key][0] = 0
    return data

def extractMax(data, keys, sample):
    data_max = collections.defaultdict(dict)
    for key in keys:
        for node in nodes:
            print(node,key)
            data_max[node][key] = max(data[node][sample][key])
    return data_max

def divideProviders(data, firstLoser, timegap):
    for node in nodes:
        for key in measures:
            for i in range(1,len(data[node])):
                if len(data[node][i][key]) < timegap and node is not firstLoser:
                    data_30 = []
                    data_30 = data[node][i][key]
                    data[node][i][key] = data[firstLoser][i][key]
                    data[firstLoser][i][key] = data_30
                # else:

    return data



def transposeTime(data):
    print("transpose data")
    for node in nodes:
        max_array = []
        max_array[:] = [data[node][i]["time"][-1] for i in range(len(data[node]))]
        node_average = np.average(max_array)
        for i in range(0,len(data[node])):
            data[node][i]["time"][:] = [float(node_average/max_array[i])*value for value in data[node][i]["time"]]
        
    return data



def maxLengthSamples(data):
    max_length = 0
    for node in nodes:
        if max_length < len(data[node][0]["time"]):
            max_length_node = node
            max_length = len(data[node][0]["time"])
    
    return max_length_node

def maxTimeNode(data):
    max_length = float(0)
    for node in nodes:
        if max_length < data[node][0]["time"][-1]:
            max_length_node = node
            max_length = data[node][0]["time"][-1]
    
    return max_length_node

def averageData(data):
    for node in nodes:
        avg_values = collections.defaultdict(dict)
        print("dataset length: ", len(data[node]))
        for key in notime_measures:
            avg_values[key] = []
            print("len_time:", len(data[node][0]["time"]),"len_key:", len(data[node][0][key]), "end_time:", data[node][0]["time"][-1])
            for j in range(0, int(data[node][0]["time"][-1])):
                temporary = []
                for i in range(len(data[node])):
                    temp = data[node][i]["time"]
                    index = []
                    index[:] = [idx for idx,element in enumerate(data["10"][i]["time"]) if element >= float(j) and element < float(j+1)]
                    # print("idx: ", index)
                    # print(j, i,"start",temp[0], "end", temp[-1], index, np.average(data[node][i][key][index[0]:index[-1]+1]))
                    if len(index) == 0:
                        value = float(0)
                    else:
                        value = np.average(data[node][i][key][index[0]:index[-1]+1])
                    temporary.append(value)
                if len(temporary) == 0:
                    temporary_value = float(0)
                else:
                    temporary_value = np.average(temporary)

                avg_values[key].append(temporary_value)
            # print("avg:", avg_values[key])
            data[node][0][key] = avg_values[key]
        data[node][0]["time"] = [float(value) for value in range(0, int(data[node][0]["time"][-1]))]
    return data

def zeroValueInMaxNode(data, node, keys, discard_time):
    variance_time = float(1.5)
    for key in keys:
        for i in range(len(data[node])):
            for j in range(len(data[node][i]["time"])):
                if(data[node][i]["time"][j] >=  discard_time[i]-variance_time):
                    data[node][i][key][j] = float(0)
    return data[node]

def appendTime(data):
    max_node = maxTimeNode(data)
    print("Max time node is: ", max_node)
    discard_time = []
    for node in nodes:
        for sample in range(0,len(data[node])):
            if node is not max_node:
                time_difference = data[max_node][sample]["time"][-1] - data[node][sample]["time"][-1]
                if node == '10':
                    discard_time.append(data[node][sample]["time"][-1])
                print(node,sample, "w. time_diff",time_difference, "from max node", max_node)
                last_time = data[node][sample]["time"][-1]
                for i in range(int(time_difference)):
                    data[node][sample]["time"].append(last_time+i)
                    for key in notime_measures:
                        data[node][sample][key].append(float(0))
    data[max_node] = zeroValueInMaxNode(data, max_node, ["disk_busy", "net_rcv", "net_send"], discard_time)
    return data

if __name__ == '__main__':
    data = {}
    data["10"] = []
    data["20"] = []
    data["30"] = []

    count = 0
    for filename in os.listdir(results_path):
        name = filename.split("_")[1].split(".csv")[0]
        # print(name)
        if name == str(10):
            data["10"].append(open_csv(results_path+filename))
        elif name == str(20):
            data["20"].append(open_csv(results_path+filename))
        elif name == str(30):
            data["30"].append(open_csv(results_path+filename))
            count+=1
        else:
            print("No result")

    # print(data["10"][4]["time"][1])
    # print(len(data["20"][4]["time"]))
    # print(len(data["30"][4]["time"]))

    # print(data["10"][1]["cpu"])

    
    # print(data_max)
    data = divideProviders(data, "30", 300)

    data = zero_data(data)
    
    data = modifyData(data, ["disk_busy", "net_rcv", "net_send"])
    
    data = transposeTime(data)
    data = averageData(data)
    data_max = extractMax(data, ["disk_busy", "net_rcv", "net_send"], sample)
    print("max:",maxLengthSamples(data), maxTimeNode(data))
    data = appendTime(data)
    max_time = data[maxTimeNode(data)][sample]["time"][-1]
    print("max_time: ",max_time)
    # data = appendTime(data)
    # print(data["30"])
    # data["10"][1]["disk_busy"][1:] = increase_difference(data["10"][1]["disk_busy"])
    # data["10"][1]["disk_busy"][0] = 0

    # print("10",len(data["10"][sample]["time"]))
    # print("20",len(data["20"][sample]["time"]))
    # print("30",len(data["30"][sample]["time"]))


    fig, ax = plt.subplots(3,5, figsize=(8,5))
    # plt.sub
    # plt.eventplot([y,x,z], colors=['red', 'blue', 'black'], lineoffsets=[0, 2, 4], linelengths=[1.6], linewidths=[1, 1, 1], orientation='horizontal')
    # fig.rcParams["figure.figsize"] = (1280, 920)
    plt.subplots_adjust(wspace=0.75, hspace=0.3, left=0.165, bottom=0.1, right=0.99, top=0.95)
    # plt.rcParams["figure.figsize"] = (1280, 920)

    
    # ax[0, 0].yticks([0, 50, 100], labels, rotation="horizontal")
    # ax[0, 0].set(ylabel='CPU usage (%)', title='CPU usage for the experiment')
    # ax[0, 0].set(title='CPU usage', ylabel="(%)")
    ax[0, 0].set(title='CPU usage')
    ax[0, 0].plot(data["30"][sample]["time"], data["30"][sample]["cpu"])
    ax[0, 0].set_ylim([0, 120])
    ax[0, 0].set_xlim([0, max_time])

    # ax.grid()
    ax[0, 1].plot(data["30"][sample]["time"], data["30"][sample]["mem"])
    # ax[0, 1].set(xlabel='time (s)', ylabel='MEM usage (%)')
    ax[0, 1].set(title='MEM usage')
    ax[0, 1].set_ylim([0, 30])
    ax[0, 1].set_xlim([0, max_time])
    ax[0, 2].plot(data["30"][sample]["time"], data["30"][sample]["disk_busy"])
    # ax[0, 2].set(xlabel='time (s)', ylabel='Disk busy usage (%)')
    ax[0, 2].set(title='Disk usage')
    ax[0, 2].set_ylim([0, data_max["10"]["disk_busy"]+10])
    ax[0, 2].set_xlim([0, max_time])
    ax[0, 3].plot(data["30"][sample]["time"], data["30"][sample]["net_rcv"])
    # ax[0, 3].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[0, 3].set(title='NET receive')
    ax[0, 3].set_ylim([0, data_max["10"]["net_rcv"]+10])
    ax[0, 3].set_xlim([0, max_time])
    ax[0, 4].plot(data["30"][sample]["time"], data["30"][sample]["net_send"])
    # ax[0, 4].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[0, 4].set(title='NET send')
    ax[0, 4].set_ylim([0, data_max["10"]["net_send"]])
    ax[0, 4].set_xlim([0, max_time])
    

    ax[1, 0].plot(data["10"][0]["time"], data["10"][0]["cpu"])
    # ax[1, 0].set(ylabel='CPU usage (%)')
    ax[1, 0].set_ylim([0, 120])
    ax[1, 0].set_xlim([0, max_time])
    # ax.grid()
    ax[1, 1].plot(data["10"][sample]["time"], data["10"][sample]["mem"])
    # ax[1, 1].set(xlabel='time (s)', ylabel='MEM usage (%)')
    ax[1, 1].set_ylim([0, 30])
    ax[1, 1].set_xlim([0, max_time])
    ax[1, 2].plot(data["10"][sample]["time"], data["10"][sample]["disk_busy"])
    # ax[1, 2].set(xlabel='time (s)', ylabel='Disk busy usage (%)')
    ax[1, 2].set_ylim([0, data_max["10"]["disk_busy"]+10])
    ax[1, 2].set_xlim([0, max_time])
    ax[1, 3].plot(data["10"][sample]["time"], data["10"][sample]["net_rcv"])
    # ax[1, 3].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[1, 3].set_ylim([0, data_max["10"]["net_rcv"]+10])
    ax[1, 3].set_xlim([0, max_time])
    ax[1, 4].plot(data["10"][sample]["time"], data["10"][sample]["net_send"])
    # ax[1, 4].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[1, 4].set_ylim([0, data_max["10"]["net_send"]+10])
    ax[1, 4].set_xlim([0, max_time])

    ax[2, 0].plot(data["20"][0]["time"], data["20"][0]["cpu"])
    ax[2, 0].set_xlim([0, max_time])
    # ax[2, 0].set(ylabel='CPU usage (%)')
    ax[2, 0].set(xlabel='time (s)')
    ax[2, 0].set_ylim([0, 120])
    
    # ax.grid()
    ax[2, 1].plot(data["20"][sample]["time"], data["20"][sample]["mem"])
    ax[2, 1].set(xlabel='time (s)')
    # ax[2, 1].set(xlabel='time (s)', ylabel='MEM usage (%)')
    ax[2, 1].set_ylim([0, 30])
    ax[2, 1].set_xlim([0, max_time])
    ax[2, 2].plot(data["20"][sample]["time"], data["20"][sample]["disk_busy"])
    # ax[2, 2].set(xlabel='time (s)', ylabel='Disk busy usage (%)')
    ax[2, 2].set(xlabel='time (s)')
    ax[2, 2].set_ylim([0, data_max["20"]["disk_busy"]+10])
    ax[2, 2].set_xlim([0, max_time])
    ax[2, 3].plot(data["20"][sample]["time"], data["20"][sample]["net_rcv"])
    # ax[2, 3].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[2, 3].set(xlabel='time (s)')
    ax[2, 3].set_ylim([0, data_max["20"]["net_rcv"]+10])
    ax[2, 3].set_xlim([0, max_time])
    ax[2, 4].plot(data["20"][sample]["time"], data["20"][sample]["net_send"])
    # ax[2, 4].set(xlabel='time (s)', ylabel='NET usage (%)')
    ax[2, 4].set(xlabel='time (s)')
    ax[2, 4].set_ylim([0, data_max["10"]["net_send"]+10])
    ax[2, 4].set_xlim([0, max_time])
    
    
    # for a in ax.flat:
    #     a.set(xlabel='time (s)')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    # for a in ax.flat:
    #     a.label_outer()
    plt.sca(ax[0,0])
    labels = ["0", "Provider#1     50","100"]
    plt.yticks([0, 50, 100], labels, rotation="horizontal")
    
    plt.sca(ax[1,0])
    labels = ["0", "Consumer     50","100"]
    plt.yticks([0, 50, 100], labels, rotation="horizontal")
   
    plt.sca(ax[2,0])
    labels = ["0", "Provider#2     50","100"]
    plt.yticks([0, 50, 100], labels, rotation="horizontal")
    # labels = ["0", "Provider#2 50","Consumer", "Provider#1"]
    
    fig.savefig(output_filename+"profiling.png")
    fig.savefig(output_filename+"profiling.pdf")
