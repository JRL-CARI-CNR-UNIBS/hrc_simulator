# import library and dataset
import matplotlib.pyplot as plt


if __name__ == '__main__':
    from pymongo import MongoClient

    import statistics

    # IMPORTANT: K = scaling of execution time. It modifies the real execution times. Set to 1 to use real data
    K=1

    client = MongoClient()
    db = client.test_mosaic
    collections = [db.baseline_mosaic_full, db.baseline_mosaic_full, db.baseline_mosaic_full] #MODIFY NAMES
    # collections = [db.results_motion_precomputed, db.results_motion_single_goal, db.results_motion_multi_goal, db.results_motion_multi_goal_no_safety] #MODIFY NAMES

    traveled_distance_array = []
    execution_time_array = []
    plan_execution_time_array = []
    planning_time_array = []
    outcome_array = []
    for coll in collections:
        robot_skills = list(coll.find({"agent": "ur5_on_guide"}))
        human_skills = list(coll.find({"agent": "human_right_arm"}))

        temp=[]
        for skill in robot_skills:
            temp.append(skill["recipe"])
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
            planning_time_cum = []
            failures_cum = 0
            iter = 0
            for idx,skill in enumerate(robot_skills):
                if skill["recipe"]==recipe:
                    outcome = skill["outcome"]
                    failures_cum += 1-outcome
                    if outcome==1:
                        iter += 1
                        traveled_distance_cum += skill["path_length"]
                        execution_time_cum += K*skill["duration_real"]
                        plan_execution_time_cum += K*skill["duration_planned"]
                        planning_time_cum.append(skill["planning_time"])

            traveled_distance_aggr.append(traveled_distance_cum/iter*25)
            execution_time_aggr.append(execution_time_cum/iter*25)
            plan_execution_time_aggr.append(plan_execution_time_cum/iter*25)
            planning_time_aggr += planning_time_cum
            outcome_aggr.append(failures_cum)


        traveled_distance_array.append(traveled_distance_aggr)
        execution_time_array.append(execution_time_aggr)
        plan_execution_time_array.append(plan_execution_time_aggr)
        planning_time_array.append(planning_time_aggr)
        outcome_array.append(outcome_aggr)

    # titles = ["traveled distance [rad]", "execution time [s]", "planned execution time [s]", "planning time [s]", "n. of failures"]
    titles = ["Traveled Distance [rad]", "Robot Execution Time [s]", "Planning Time [s]"]

    # datas = [traveled_distance_array, execution_time_array, plan_execution_time_array, planning_time_array, outcome_array]
    datas = [traveled_distance_array, execution_time_array, planning_time_array]

    # xlabels = ["precomputed", "single-goal", "multi-goal", "multi-goal\n(no safety)"]
    xlabels = ["PRE-COMPUTED", "SINGLE-GOAL", "MULTI-GOAL"]

    medianprops = dict(color="navy", linewidth=1.5)

    fig, axes = plt.subplots(nrows=1, ncols=len(datas), figsize=(15, 3.5))
    # notch shape box plot
    for ax, title, data in zip(axes, titles, datas):
        print(title)
        for item, label in enumerate(xlabels):
            print(label + ": mean=" + str(statistics.mean(data[item])) + ", dev=" + str(statistics.stdev(data[item])))
        if title!="Planning Time [s]":
            bplot = ax.boxplot(data,
                                notch=False,  # notch shape
                                vert=True,  # vertical box alignment
                                patch_artist=True,  # fill with color
                                labels=xlabels, # will be used to label x-ticks
                                medianprops=medianprops,
                                showmeans=True,
                                showfliers=False)
            ax.set_title(title)
            ax.yaxis.grid(True)
            colors = ['aquamarine', 'paleturquoise', 'turquoise']
        else:
            bplot = ax.boxplot(data[1:],
                               notch=False,  # notch shape
                               vert=True,  # vertical box alignment
                               patch_artist=True,  # fill with color
                               labels=xlabels[1:],  # will be used to label x-ticks
                               medianprops=medianprops,
                               showmeans=True,
                               showfliers=False)
            ax.set_title(title)
            ax.yaxis.grid(True)
            colors = ['paleturquoise', 'turquoise']
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
    plt.savefig('./figure_motion.pdf', format='pdf')
    plt.show()
