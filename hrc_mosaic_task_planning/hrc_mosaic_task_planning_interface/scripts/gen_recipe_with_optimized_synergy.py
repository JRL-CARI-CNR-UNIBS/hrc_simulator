import yaml
import random
import numpy as np

def convert2vector(skill_names,skill_durations):
    skill_durations_int = list(map(round, skill_durations))
    window_array = []
    for name,duration in zip(skill_names,skill_durations_int):
        window_array += duration * [name]
    return window_array

def computeRisk(r_window_array,h_window_array,r_prefix,h_prefix,mongo_collection):
    risk = 0
    for idx in range( min(len(r_window_array),len(h_window_array)) ):
        risk += mongo_collection.find_one({r_prefix+"_skill" : r_window_array[idx], h_prefix+"_skill" : h_window_array[idx]})["dynamic_risk"]
    return risk

def printSkillToYaml(filename,prefix,skill,concurrent_skill,id_command,sync_flag):
    with open(filename, 'r') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile)  # Note the safe_load
        try:
            new_robot_skill = {'cmd_id': str(id_command), 'cmd_name': skill,
                             'cfg_start': 'Null', 'cfg_goal': 'Null', 'risk_level': 0,
                             'expected_time': 0, 'human_tasks': concurrent_skill}
            cur_yaml[prefix + '_plan'].append(new_robot_skill)
            if sync_flag:
                sync_skill = {'cmd_id': str(id_command) + '_sync', 'cmd_name': "syncronization",
                                  'cfg_start': 'Null', 'cfg_goal': 'Null', 'risk_level': 0,
                                  'expected_time': 0, 'human_tasks': []}
                cur_yaml[prefix + '_plan'].append(sync_skill)

        except:
            new_skill = {prefix + '_plan': [{'cmd_id': str(id_command), 'cmd_name': skill,
                                                     'cfg_start': 'Null', 'cfg_goal': 'Null',
                                                     'risk_level': 0,
                                                     'expected_time': 0,
                                                     'human_tasks': concurrent_skill}]}
            cur_yaml.update(new_skill)
            if sync_flag:
                sync_skill = {'cmd_id': str(id_command + 1) + '_sync', 'cmd_name': "syncronization",
                                  'cfg_start': 'Null', 'cfg_goal': 'Null', 'risk_level': 0,
                                  'expected_time': 0, 'human_tasks': []}
                cur_yaml[prefix + '_plan'].append(sync_skill)
        # print(cur_yaml)
    if cur_yaml:
        with open(filename, 'w') as yamlfile:
            yaml.safe_dump(cur_yaml, yamlfile)  # Note the safe_dump

if __name__ == '__main__':

    from pymongo import MongoClient
    from datetime import datetime

    client = MongoClient()
    db = client.sharework
    collection_duration = db.hrc_task_durations
    collection_risk = db.hrc_dynamic_risks

    # get recipe
    recipe_name = "plan1"
    folder_name = "/home/hypatia/catkin_ws/src/sharework-dbs/plans/multi-obj/v4/"
    with open(folder_name + recipe_name + ".yaml", 'r') as stream:
        out = yaml.safe_load(stream)
        r_skill_names = out['robot_plan']
        h_skill_names = out['human_plan']

    robot_prefix = "ur5_on_guide"
    human_prefix = "human_right_arm"

    # r_skill_names = ['pickplace-B1', 'pickplace-B2', 'pickplace-B3']
    # h_skill_names = ['pickplace-G1', 'pickplace-G2', 'pickplace-G3']

    r_durations = []
    for name in r_skill_names:
        r_durations.append(collection_duration.find_one({"name" : name})[robot_prefix+"_expected_duration"])
    h_durations = []
    for name in h_skill_names:
        h_durations.append(collection_duration.find_one({"name": name})[human_prefix + "_expected_duration"])

    r_window_array = convert2vector(r_skill_names,r_durations)
    h_window_array = convert2vector(h_skill_names, h_durations)
    best_risk = computeRisk(r_window_array, h_window_array, robot_prefix, human_prefix, collection_risk)
    best_plan = [r_skill_names,h_skill_names]

    print("Initial recipe")
    print("robot plan: ", best_plan[0])
    print("human plan: ", best_plan[1])
    print("Initial risk: ", best_risk)

    for idx in range(100):
        temp_r = list(zip(r_skill_names, r_durations))
        random.shuffle(temp_r)
        r_skill_names, r_durations = zip(*temp_r)

        temp_h = list(zip(h_skill_names, h_durations))
        random.shuffle(temp_h)
        h_skill_names, h_durations = zip(*temp_h)

        r_window_array = convert2vector(r_skill_names, r_durations)
        h_window_array = convert2vector(h_skill_names, h_durations)
        risk = computeRisk(r_window_array, h_window_array, robot_prefix, human_prefix, collection_risk)

        if risk <= best_risk:
            best_risk = risk
            best_plan = [r_skill_names,h_skill_names]

    robot_plan = best_plan[0]
    human_plan = best_plan[1]

    # create yaml recipe
    now = datetime.now()
    folder_name_out = '/home/hypatia/catkin_ws/src/task-planner-interface/task_planner_interface/plans/multi-obj/v4_fake/'
    filename = folder_name_out + 'optimized_' + recipe_name + '.yaml'
    file_obj = open(filename, 'w')
    file_obj.truncate(0)  # delete all content
    file_obj.write('recipe autogenerated: ' + now.strftime('%m/%d/%Y, %H:%M:%S'))
    file_obj.close()

    with_sync = 0
    for idx in range(len(robot_plan)):
        if idx<len(human_plan):
            concurrent_skill=[human_plan[idx]]
        else:
            concurrent_skill=[]
        printSkillToYaml(filename, "robot", robot_plan[idx], concurrent_skill, idx, with_sync)
    printSkillToYaml(filename, "robot", "end", [], idx+1, 0)

    for idx in range(len(human_plan)):
        if idx<len(robot_plan):
            concurrent_skill=[robot_plan[idx]]
        else:
            concurrent_skill=[]
        printSkillToYaml(filename, "human", human_plan[idx], concurrent_skill, idx+1000, with_sync)
    printSkillToYaml(filename, "human", "end", [], idx+1001, 0)

    print("Final recipe")
    print("robot plan: ", robot_plan)
    print("human plan: ", human_plan)
    print("Final risk: ", best_risk)



