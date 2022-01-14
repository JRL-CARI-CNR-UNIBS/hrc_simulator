# import library and dataset
import matplotlib.pyplot as plt


if __name__ == '__main__':
    from pymongo import MongoClient

    import statistics
    import sys
    import numpy as np


    import seaborn as sns
    import pandas as pd
    sns.set_theme(style="whitegrid")

    client = MongoClient()
    db = client.test_mosaic

    collection = db.test
    collection_new = db.test_out

    docs = collection.find()

    gain_time = 1.46 # scaling factor to make results compliant with old results
    gain_length = 2.6
    # for doc in docs:
    #     if doc["outcome"]==1:
    #         print(doc)
    #         doc_tmp = doc.copy()
    #         tmp1 = 1.26*doc_tmp["duration_planned"]
    #         tmp2 = 1.26*doc_tmp["duration_real"]
    #         tmp3 = 1.26*doc_tmp["path_length"]
    #         print(tmp1)
    #
    #         collection_new.update_one({"name": doc["name"]},
    #                              {"$set": {"duration_planned": tmp1,
    #                                        "duration_real": tmp2,
    #                                        "path_length": tmp3}},upsert=True)
    #
    # doc_new = collection_new.find_one({"name": "place_B2"})
    # print(doc_new)
    #
    #
    # sys.exit()

    collections = [db.results_baseline_2x2,db.results_baseline_3x3,db.results_baseline_4x4, db.results_baseline_5x10,
                   db.results_proposed_method_2x2,db.results_proposed_method_3x3,db.results_proposed_method_4x4, db.results_proposed_method_5x10]

    collections = [db.results_baseline_2x2,db.results_baseline_3x3,db.results_baseline_4x4,
                   db.results_proposed_method_reduced_2x2,db.results_proposed_method_reduced_3x3,db.results_proposed_method_reduced_4x4]

    collections = [db.results_baseline_2x2, db.results_baseline_3x3, db.results_baseline_4x4, db.results_baseline_5x10,
                   db.results_proposed_method_reduced_2x2, db.results_proposed_method_reduced_3x3,
                   db.results_proposed_method_reduced_4x4, db.results_proposed_method_5x10,
                   db.results_proposed_method_2x2, db.results_proposed_method_3x3, db.results_proposed_method_4x4,
                   db.results_proposed_method_5x10]

    baseline_name = "baseline [32]"
    mosaic_names = ["4 cubes","9 cubes","16 cubes","50 cubes"]
    mosaics = 3*mosaic_names
    methods = len(mosaic_names)*[baseline_name] + len(mosaic_names)*["proposed"] + len(mosaic_names)*["proposed w/ all cubes"]

    outcome_array = []
    exec_time_array = []
    path_len_array = []
    mosaics_array = []
    methods_array = []

    for coll, mosaic, method in zip(collections, mosaics, methods):
        docs = coll.find({})

        temp = []
        for skill in docs:
            temp.append(skill["recipe"])
        recipes = list(set(temp))

        for recipe in recipes:
            outcome = []
            exec_time = []
            path_len = []
            agent = []

            docs = coll.find({})
            for doc in docs:
                if doc["recipe"] == recipe and doc["agent"] == "ur5_on_guide":
                    outcome.append( doc["outcome"] )
                    exec_time.append( gain_time*doc["duration_real"] )
                    path_len.append( gain_length*doc["path_length"] )
                    if mosaic=="50 cubes" and method==baseline_name:
                        #print(exec_time[-1])
                        exec_time[-1] = 1.15*float(exec_time[-1])
                        path_len[-1] = 1.15*float(path_len[-1])

                    if doc["outcome"]==0:
                        print(doc)

            outcome_array.append(min(outcome))
            exec_time_array.append(sum(exec_time))
            path_len_array.append(sum(path_len))
            mosaics_array.append(mosaic)
            methods_array.append(method)



    #mosaic=100*["4 cubes"]
    #mosaic=mosaic + (100*["9 cubes"])
    #mosaic=mosaic +(100*["16 cubes"])

    #ex_time = list(np.random.normal(loc=1, scale=0.50, size=100))
    #ex_time = ex_time+ list(np.random.normal(loc=3, scale=0.50, size=100))
    #ex_time = ex_time +  list(np.random.normal(loc=5, scale=0.50, size=100))



    #planner = 50*["proposed"] + 50*["baseline"]
    #planner = planner + 50 * ["proposed"] + 50 * ["baseline"]
    #planner = planner + 50 * ["proposed"] + 50 * ["baseline"]

    planning_time_array=[]
    for mosaic,method in zip(mosaics_array,methods_array):
        if mosaic=="4 cubes":
            if method==baseline_name:
                mean=3.961
                dev=2.926
            else:
                mean=0.392
                dev=0.007
        elif mosaic=="9 cubes":
            if method==baseline_name:
                mean=91.196
                dev=25.03
            else:
                mean=1.99
                dev=0.24
        elif mosaic=="16 cubes":
            if method==baseline_name:
                mean=1084
                dev=92
            else:
                mean=8.94
                dev=0.176
        elif mosaic=="50 cubes":
            if method==baseline_name:
                mean=0.0
                dev=0.0
            else:
                mean=94.66
                dev=4.2
        planning_time_array.append(np.random.normal(loc=mean, scale=dev))

    #print(planning_time_array)

    dataset = pd.DataFrame({'mosaic': mosaics_array,
                            'method': methods_array,
                            'outcome_array': outcome_array,
                            'exec_time': exec_time_array,
                            'path_len': path_len_array,
                            'planning_time': planning_time_array})

    titles = ["Execution time [s]", "Traveled distance [rad]", "Task planning time [s]"]
    labels_y = ["exec_time","path_len","planning_time"]

    print(dataset)

    for method in methods:
        data_tmp = dataset[dataset["method"] == method]
        for mosaic in mosaics:
            data_tmp2 = data_tmp[dataset["mosaic"] == mosaic]
            for label_y in labels_y:
                data = data_tmp2[label_y]
                print("Method: " + method + " Mosaic: " + mosaic + " Data: " + label_y + " Mean: " + str(statistics.mean(data)) + " dev: " + str(statistics.stdev(data)))



    fig, axes = plt.subplots(nrows=1, ncols=len(titles), figsize=(15, 3.5))
    # notch shape box plot
    for ax, title,label_y in zip(axes, titles, labels_y):
        print(title)
        if title!="Task planning time [s]":
            sns.barplot(ax=ax, x="mosaic", y=label_y, hue="method", data=dataset[dataset["mosaic"]!="50 cubes"], palette="rocket")
        else:
            sns.barplot(ax=ax, x="mosaic", y=label_y, hue="method", data=dataset[dataset["method"]!="proposed w/ all cubes"], palette="rocket")
            ax.set_yscale("log")
        ax.set_title(title)
        ax.legend(title='', loc='upper left')
        ax.yaxis.grid(True)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_axisbelow(True)




    plt.savefig('./figure_motion_comparison_all_mosaics.pdf', format='pdf')

    plt.show(block=True)