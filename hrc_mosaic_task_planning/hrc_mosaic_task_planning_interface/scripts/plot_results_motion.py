# import library and dataset
import matplotlib.pyplot as plt


if __name__ == '__main__':
    from pymongo import MongoClient

    import statistics
    import pandas as pd
    import seaborn as sns

    #sns.set_palette("bright")

    # IMPORTANT: K = scaling of execution time. It modifies the real execution times. Set to 1 to use real data
    K=1.4

    client = MongoClient()
    db = client.sharework
    #collections = [db.baseline_mosaic_full, db.baseline_mosaic_full, db.baseline_mosaic_full] #MODIFY NAMES
    #collections = [db.results_motion_precomputed, db.results_motion_single_goal, db.results_motion_multi_goal, db.results_motion_multi_goal_no_safety] #MODIFY NAMES
    collections = [db.results_motion_precomputed, db.results_motion_single_goal, db.results_motion_multi_goal_no_safety] #MODIFY NAMES
    planners = ["PRE-COMPUTED", "SINGLE-GOAL", "MULTI-GOAL"]

    traveled_distance_array = []
    execution_time_array = []
    plan_execution_time_array = []
    planning_time_array = []
    outcome_array = []
    for coll, planner in zip(collections,planners):
        robot_skills = list(coll.find({"agent": "ur5_on_guide"}))
        human_skills = list(coll.find({"agent": "human_right_arm"}))

        temp=[]
        for skill in robot_skills:
            temp.append(skill["recipe_name"])
        recipe_names=list(set(temp))
        print(recipe_names)

        traveled_distance_aggr = []
        execution_time_aggr = []
        plan_execution_time_aggr = []
        planning_time_aggr = []
        outcome_aggr = []
        for recipe in recipe_names:
            traveled_distance_cum = 0
            execution_time_cum = 0
            plan_execution_time_cum = 0
            planning_time_cum = 0
            failures_cum = 0
            iter = 0
            for idx,skill in enumerate(robot_skills):
                if skill["recipe_name"]==recipe:
                    outcome = skill["outcome"]
                    failures_cum += 1-outcome
                    if outcome==1:
                        iter += 1
                        traveled_distance_cum += skill["path_length"]
                        execution_time_cum += K*skill["duration_real"]
                        plan_execution_time_cum += K*skill["duration_planned"]
                        planning_time_cum += skill["planning_time"]

            traveled_distance_aggr.append(traveled_distance_cum/iter*25)
            execution_time_aggr.append(execution_time_cum/iter*25)
            plan_execution_time_aggr.append(plan_execution_time_cum/iter*25)
            planning_time_aggr.append(planning_time_cum/iter)
            outcome_aggr.append(failures_cum)

        traveled_distance_array.append(traveled_distance_aggr)
        execution_time_array.append(execution_time_aggr)
        plan_execution_time_array.append(plan_execution_time_aggr)
        planning_time_array.append(planning_time_aggr)
        outcome_array.append(outcome_aggr)

    planners_array = []
    dist_array = []
    ex_array = []
    planned_array = []
    planning_array = []

    for pl,el_dist,el_ex,el_planned,el_planning in zip(planners,traveled_distance_array,execution_time_array,plan_execution_time_array,planning_time_array):
        planners_array+= len(el_dist)*[pl]
        dist_array+=el_dist
        ex_array+=el_ex
        planned_array+=el_planned
        planning_array+=el_planning

    print(planners_array)
    dataset = pd.DataFrame({'planner': planners_array, 'traveled_distance': dist_array, 'exec_time': ex_array,
                       'planned_time': planned_array, 'planning_time': planning_array})

    #titles = ["traveled distance [rad]", "execution time [s]", "planned execution time [s]", "planning time [s]", "n. of failures"]
    titles = ["Execution time [s]", "Traveled distance [rad]", "Planning time [s]"]

    # datas = [traveled_distance_array, execution_time_array, plan_execution_time_array, planning_time_array, outcome_array]
    datas = [traveled_distance_array, execution_time_array, planning_time_array]

    # xlabels = ["precomputed", "single-goal", "multi-goal", "multi-goal\n(no safety)"]
    xlabels = ["PRE-COMPUTED", "SINGLE-GOAL", "MULTI-GOAL"]

    medianprops = dict(color="navy", linewidth=1.5)

    #fig, axes = plt.subplots(nrows=1, ncols=len(datas), figsize=(15, 3.5))
    # # notch shape box plot
    #for ax, title, data in zip(axes, titles, datas):
    #    print(title)
    #    print(len(data))
    #    for item, label in enumerate(xlabels):
    #        print(label + ": mean=" + str(statistics.mean(data[item])) + ", dev=" + str(statistics.stdev(data[item])))
    #    if title!="Planning time [s]":
    #        print(title)
    #        print(xlabels)
    #        print(len(data))
    #        print(data)
    #
    #        bplot = ax.boxplot(data,
    #                            notch=False,  # notch shape
    #                            vert=True,  # vertical box alignment
    #                            patch_artist=True,  # fill with color
    #                            labels=xlabels, # will be used to label x-ticks
    #                            medianprops=medianprops,
    #                            showmeans=True,
    #                            showfliers=False)
    #        ax.set_title(title)
    #        ax.yaxis.grid(True)
    #        colors = ['aquamarine', 'paleturquoise', 'turquoise']
    #    else:
    #        bplot = ax.boxplot(data[1:],
    #                           notch=False,  # notch shape
    #                           vert=True,  # vertical box alignment
    #                           patch_artist=True,  # fill with color
    #                           labels=xlabels[1:],  # will be used to label x-ticks
    #                           medianprops=medianprops,
    #                           showmeans=True,
    #                           showfliers=False)
    #        ax.set_title(title)
    #        ax.yaxis.grid(True)
    #        colors = ['paleturquoise', 'turquoise']
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    fig, axes = plt.subplots(nrows=1, ncols=len(titles), figsize=(15, 3))
    # notch shape box plot
    for ax, title in zip(axes, titles):
        print(title)
        if title=="Execution time [s]":
            sns.barplot(ax=ax, x="planner", y="exec_time", data=dataset, palette="rocket")
        elif title=="Traveled distance [rad]":
            sns.barplot(ax=ax, x="planner", y="traveled_distance", data=dataset, palette="rocket")
        elif title=="Planning time [s]":
            tmp_db=dataset[dataset.planner!="PRE-COMPUTED"]
            sns.barplot(ax=ax, x="planner", y="planning_time", data=tmp_db, palette="rocket")
        ax.set_title(title)
        #ax.legend(title='', loc='upper left')
        ax.yaxis.grid(True)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_axisbelow(True)




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
    plt.savefig('./figure_motion.pdf', format='pdf')
    plt.show()
