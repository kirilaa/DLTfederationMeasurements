import matplotlib.pyplot as plt
import json
import time
import sys
import os
import numpy as np


# results_path= "../results/"
# results_path= "../eth_poa_10/results/"
# results_path= "../cosmos_results/results/" #WORKS
results_path= "../tender_results/results/" #WORKS
# results_path= "../eth_ath_all_verifiers_GOOD_results/results/" #WORKS
# results_path= "../eth_pow_all_miners_active/results/" #WORKS

#CHANGE THIS VARIABLE TO 
cosmos = True

def redefine_provider_domains(data):
    # max = len(data["20"][k])
    # max = len(data["30"][k]) if max < len(data["30"][k]) else max
    # total_data = []
    # total_data = data["20"]+data["30"]
    substitute_data1 = []
    substitute_data2 = []
    range_max = max(len(data["20"]), len(data["30"]))
    print("RANGE MAX =", range_max)
    for k in range(range_max):
        # max = len(data["20"][k])
        # max = len(data["30"][k]) if max < len(data["30"][k]) else max
        if len(data["20"][k]) > len(data["30"][k]):
            substitute_data1.append(data["20"][k])
            substitute_data2.append(data["30"][k])
        elif len(data["20"][k]) == len(data["30"][k]):
            print("ERROR SAME num of elements ", k)
        else:
            substitute_data1.append(data["30"][k])
            substitute_data2.append(data["20"][k])

    return substitute_data1, substitute_data2

def variance_data(data):
    print("RESULTS averaged: ", len(data["10"]))
    data = values_only(data)

    var_data = {}
    for n in ["10", "20", "30"]:
        var_data[str(n)] = []
        for j in range(len(data[str(n)][0])):
            max = float(0)
            min = float(0)
            variance = float(0)
            for i in range(len(data[str(n)])):
                if i == 0:
                    min = float(data[str(n)][i][j])
                    max = float(data[str(n)][i][j])
                if float(data[str(n)][i][j]) >= max:
                    max = float(data[str(n)][i][j])
                if float(data[str(n)][i][j]) <= min:
                    min = float(data[str(n)][i][j])
            var_data[str(n)].append(float(max-min))    
    print(var_data)    
    return var_data

def average_data(data):
    print("RESULTS averaged: ", len(data["10"]))
    data = values_only(data)
    sum_data = {}
    for n in ["10", "20", "30"]:
        print("n is:",n)
        sum_data[str(n)] = []
        for j in range(len(data[str(n)][0])):
            if((not(cosmos)) or n != "10" or (j != 3 and j!=8)):
                dummy = float(0)
                for i in range(len(data[str(n)])):
                    dummy += float(data[str(n)][i][j])
                sum_data[str(n)].append(float(dummy/len(data[str(n)])))    
    print(sum_data)    
    return sum_data

def values_only(data):
    new_data = {}

    for n in ["10", "20", "30"]:
        new_data[str(n)] = [None]*len(data[str(n)])
        for i in range(len(data[str(n)])):
            new_data[str(n)][i] = [v for i,v in data[str(n)][i]]
    
    return new_data

def sort_data(data):
    for i in range(len(data["10"])):
        data["10"][i] = sorted(data["10"][i].items(), key=lambda item: item[1])
        data["20"][i] = sorted(data["20"][i].items(), key=lambda item: item[1])
        data["30"][i] = sorted(data["30"][i].items(), key=lambda item: item[1])
    return data

def zero_start_data(data):
    for i in range(len(data["10"])):
        start = data["10"][i]["0_start"]
        data["10"][i].update({key: float(data["10"][i][key]-start) for key in data["10"][i].keys()})
        data["20"][i].update({key: float(data["20"][i][key]-start) for key in data["20"][i].keys()})
        data["30"][i].update({key: float(data["30"][i][key]-start) for key in data["30"][i].keys()})
    
    return data


if __name__ == '__main__':
    data = {}
    data["10"] = []
    data["20"] = []
    data["30"] = []
    count = 0
    for filename in os.listdir(results_path):
        name = filename.split("_")[1].split(".json")[0]
        # print(name)
        if name == str(10):
            # print(filename)
            with open(results_path+filename) as loaded_file:
                data["10"].append(json.load(loaded_file))
        elif name == str(20):
            with open(results_path+filename) as loaded_file:
                data["20"].append(json.load(loaded_file))
        elif name == str(30):
            with open(results_path+filename) as loaded_file:
                data["30"].append(json.load(loaded_file))
            count+=1
        else:
            print("No result")

    

    
    data = zero_start_data(data)
    data = sort_data(data)

    print(data["10"][0])
    print(data["20"][0])
    print(data["30"][0])
    
    
    data["20"], data["30"] = redefine_provider_domains(data)
    
    for k in range(len(data["30"])):
        print([v for i,v in data["30"][k]])
    
    for l in range(0, len(data["30"])):
        print(len(data["30"][l]))
    for l in range(0, len(data["20"])):
        print(len(data["20"][l]))
    for l in range(0, len(data["10"])):
        print(len(data["10"][l]))
    
    # print(data["20"][0])
    #DATA transformed into data[node_id][#measurement][#item (0 for first item)][0-label / 1- value]

    # print("Consumer:\n",data["10"][0])
    # print("Provider:\n",data["30"][0])
    # print(data["30"][0])
    # print(values_only(data))

    # print("DATA SAMPLE: ",average_data(data))
    
    var_data = variance_data(data)
    data = average_data(data)

    # x = [v for i,v in data["10"][1]]
    # y = [v for i,v in data["20"][1]]
    # z = [v for i,v in data["30"][1]]
    print(data)
    print(var_data)
    x = data['10']
    y = data['20']
    z = data['30']

    x_var = var_data['10']
    y_var = var_data['20']
    z_var = var_data['30']
    print("MAX VARIANCE:")
    print(np.max(x_var[:-1]))
    print(np.max(y_var))
    print(np.max(z_var))
    print("MIN VARIANCE:")
    print(np.min(x_var))
    print(np.min(y_var))
    print(np.min(z_var))
    # # x = x[1:]
    y = y[1:]
    z = z[1:]
    x_var = [5.3*element for element in var_data['10']]
    y_var = [5.3*element for element in var_data['20']]
    z_var = [5.3*element for element in var_data['30']]
    # print(z)
    # time = np.linspace(0,50,50)
    # time_width = [float(5.4)]*len(time)
    # print(time)
    fig, ax = plt.subplots()
    plt.eventplot([y,x,z], colors=['red', 'blue', 'black'], lineoffsets=[0, 2, 4], linelengths=[0.8], linewidths=[x_var, y_var, z_var], orientation='horizontal', alpha=0.1)
    plt.eventplot([y,x,z], colors=['red', 'blue', 'black'], lineoffsets=[0, 2, 4], linelengths=[1.6], linewidths=[1, 1, 1], orientation='horizontal')
    # plt.eventplot([time,y,z], colors=['blue', 'red', 'black'], lineoffsets=[0, 1, 2], linelengths=[2.0], linewidths=[time_width, 0.5, 0.5], orientation='horizontal')
    plt.ylabel("Domains")
    plt.xlabel("time (s)")
    # fig.canvas.draw()
    # labels = [item.get_text() for item in ax.get_yticklabels()]
    # labels[2] = 'Consumer'
    # labels[4] = 'Provider #1'
    # labels[6] = 'Provider #1'
    # ax.set_yticklabels(labels)
    plt.grid(color='grey', linestyle='dashdot', linewidth='0.5', axis="x")
    labels = ["Provider#2","Consumer", "Provider#1"]
    # plt.xticks(time)
    plt.yticks([0, 2, 4], labels, rotation="horizontal")


    plt.subplots_adjust(left=0.18 )
    plt.savefig("test.png")
    plt.savefig("events_mean_variance.png")
    plt.savefig("events_mean_variance.pdf")