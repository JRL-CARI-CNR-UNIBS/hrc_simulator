# import library and dataset
import matplotlib.pyplot as plt

if __name__ == '__main__':

    from pymongo import MongoClient
    import statistics
    import pandas as pd
    import seaborn as sns

    client = MongoClient()
    db = client.sharework
    collections = [db.results_tamp_baseline, db.results_tamp_multi_obj] #MODIFY NAMES

    planners = ["FEASIBLE", "OPTIMIZED"]

    stopping_times_all = [ [33.5, 47.8, 43.9, 49.5, 49.6, 37.3, 92, 46.6, 32.4, 88.5, 61.6, 34.8, 106, 61, 59.8, 28.9, 64.7, 50.3, 47.7, 58.2],
                           [100,  68.7, 73.2, 76.6, 75.5, 106, 102, 92.9, 71.6, 81.1, 65.9, 75.3, 87.7, 97, 76.8, 101, 79.3, 88.4, 87.6, 88.6] ]

    stopping_times_labeled_all = []
    for idx1 in stopping_times_all:
        stopping_times_recipes = []
        for idx2 in range(len(idx1)):
            stopping_times_recipes.append("recipe_" + str(idx2))
        stopping_times_labeled_all.append(sorted(zip(stopping_times_recipes,idx1)))

    temp_list = stopping_times_labeled_all.copy()
    for idx, temp in enumerate(temp_list):
        stopping_times_labeled_all[idx] = [(x, y) for x, y in temp if x != "recipe_17" ]

    print(stopping_times_labeled_all)

    robot_execution_time_array = []
    robot_outcome_array = []
    human_execution_time_array = []
    human_outcome_array = []
    cycle_times_array = []
    idle_times_array = []
    concurrent_work_array = []

    for coll,stopping_time_vec in zip(collections,stopping_times_labeled_all):
        robot_skills = list(coll.find({"agent": "ur5_on_guide"}))
        human_skills = list(coll.find({"agent": "human_right_arm"}))

        temp=[]
        for skill in robot_skills:
            temp.append(skill["recipe_name"])
        recipe_names=list(set(temp))
        recipe_names=sorted(recipe_names)

        try:
            recipe_names.remove("recipe_17")
        except:
            pass
        #stopping_time_vec.pop(17)

        print(recipe_names)

        robot_execution_time_aggr = []
        robot_outcome_aggr = []
        human_execution_time_aggr = []
        human_outcome_aggr = []
        cycle_times_aggr=[]
        idle_times_aggr=[]
        concurrent_work_aggr = []
        for i_rec,recipe in enumerate(recipe_names):
            robot_execution_time_cum = 0
            robot_failures_cum = 0
            for idx,skill in enumerate(robot_skills):
                if skill["recipe_name"]==recipe:
                    outcome = skill["outcome"]
                    robot_failures_cum += 1-outcome
                    if outcome==1:
                        robot_execution_time_cum += skill["duration_real"]
            robot_execution_time_aggr.append(robot_execution_time_cum)
            robot_outcome_aggr.append(robot_failures_cum)

            human_execution_time_cum = 0
            human_failures_cum = 0
            for idx,skill in enumerate(human_skills):
                if skill["recipe_name"]==recipe:
                    outcome = skill["outcome"]
                    human_failures_cum += 1-outcome
                    if outcome==1:
                        human_execution_time_cum += skill["duration_real"]
            human_execution_time_aggr.append(human_execution_time_cum)
            human_outcome_aggr.append(human_failures_cum)

            for time in stopping_time_vec:
                if time[0]==recipe:
                    stopping_time=time[1]
            #print(stopping_time)

            cycle_time = max(robot_execution_time_cum,human_execution_time_cum)
            idle_time = abs(robot_execution_time_cum-human_execution_time_cum)
            cycle_times_aggr.append(cycle_time)
            idle_times_aggr.append(idle_time/cycle_time*100 )
            concurrent_work_aggr.append((cycle_time-idle_time-stopping_time)/cycle_time*100)

        robot_execution_time_array.append(robot_execution_time_aggr)
        robot_outcome_array.append(robot_outcome_aggr)
        human_execution_time_array.append(human_execution_time_aggr)
        human_outcome_array.append(human_outcome_aggr)
        cycle_times_array.append(cycle_times_aggr)
        idle_times_array.append(idle_times_aggr)
        concurrent_work_array.append(concurrent_work_aggr)

    planners_array = []
    ex_array = []
    idle_array = []
    concurrent_array = []

    for pl, el_ex, el_idle, el_conc in zip(planners, cycle_times_array, idle_times_array, concurrent_work_array):
        planners_array += len(el_ex) * [pl]
        ex_array += el_ex
        idle_array += el_idle
        concurrent_array += el_conc

    print(planners_array)
    dataset = pd.DataFrame({'planner': planners_array, 'exec_time': ex_array, 'idle_time': idle_array, 'concurrent_time': concurrent_array})

    titles = ["Execution time [s]", "Idle time [% of Execution Time]", "Concurrent work [% of Execution time]"]
    datas = [cycle_times_array, idle_times_array, concurrent_work_array]
    xlabels = planners
    medianprops = dict(color="navy", linewidth=1.5)

    fig, axes = plt.subplots(nrows=1, ncols=len(datas), figsize=(15, 3))
    # notch shape box plot
    for ax, title, data in zip(axes, titles, datas):
        print(title)
        for item,label in enumerate(xlabels):
            print(label + ": mean=" + str(statistics.mean(data[item])) + ", dev=" + str(statistics.stdev(data[item])))
        bplot = ax.boxplot(data,
                            notch=False,  # notch shape
                            vert=True,  # vertical box alignment
                            patch_artist=True,  # fill with color
                            labels=xlabels, # will be used to label x-ticks
                            medianprops=medianprops,
                            showmeans=False,
                            showfliers=False)
        ax.set_title(title)
        ax.yaxis.grid(True)
        colors = ['aquamarine', 'paleturquoise', 'turquoise']
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)


    # bplot2 = axes[1].boxplot(planning_time_aggr,
    #                         notch=False,  # notch shape
    #                         vert=True,  # vertical box alignment
    #                         patch_artist=True,  # fill with color
    #                         labels=xlabels, # will be used to label x-ticks
    #                         medianprops=medianprops,
    #                         showfliers=False)
    # axes[1].set_title('Notched box plot 2')
    #
    # colors = ['lightblue', 'lightgreen','red']
    # for bplot in (bplot1, bplot2):
    #     for patch, color in zip(bplot['boxes'], colors):
    #         patch.set_facecolor(color)
    # for ax in axes:
    #     ax.yaxis.grid(True)

    fig, axes = plt.subplots(nrows=1, ncols=len(titles), figsize=(15, 3))
    # notch shape box plot
    for ax, title in zip(axes, titles):
        print(title)
        if title=="Execution time [s]":
            sns.barplot(ax=ax, x="planner", y="exec_time", data=dataset, palette="rocket")
        elif title=="Idle time [% of Execution Time]":
            sns.barplot(ax=ax, x="planner", y="idle_time", data=dataset, palette="rocket")
        elif title=="Concurrent work [% of Execution time]":
            tmp_db=dataset[dataset.planner!="PRE-COMPUTED"]
            sns.barplot(ax=ax, x="planner", y="concurrent_time", data=dataset, palette="rocket")
        ax.set_title(title)
        #ax.legend(title='', loc='upper left')
        ax.yaxis.grid(True)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_axisbelow(True)

    plt.savefig('./figure_tamp.pdf', format='pdf')

    plt.show()
