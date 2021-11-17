# Author: Marco Faroni
# Email: marco.faroni@stiima.cnr.it
# Affiliation: CNR-STIIMA

# Input: a list of pick&place tasks for the human and the robot
# Output: a yaml file with the recipe. If baseline=True -> tasks are decomposed in pick_color_cube_n + place_A1

import yaml

def printSkillsToYaml(filename,prefix,skill,skill_other,id_command,sync_flag):
    with open(filename, 'r') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile)  # Note the safe_load
        try:
            print(id_command)
            new_skill = {'cmd_id': str(id_command), 'cmd_name': skill, 'human_tasks': [skill_other]}
            cur_yaml[prefix + '_plan'].append(new_skill)
            if sync_flag:
                sync_skill = {'cmd_id': str(id_command) + '_sync', 'cmd_name': "syncronization"}
                cur_yaml[prefix + '_plan'].append(sync_skill)

        except:
            new_skill = {prefix + '_plan': [{'cmd_id': str(id_command), 'cmd_name': skill, 'human_tasks': [skill_other]}]}
            cur_yaml.update(new_skill)
            if sync_flag:
                sync_skill = {'cmd_id': str(id_command + 1) + '_sync', 'cmd_name': "syncronization"}
                cur_yaml[prefix + '_plan'].append(sync_skill)
        # print(cur_yaml)
    if cur_yaml:
        with open(filename, 'w') as yamlfile:
            yaml.safe_dump(cur_yaml, yamlfile)  # Note the safe_dump


if __name__ == '__main__':
    print('Generating recipe from given list...')

    from pymongo import MongoClient
    from datetime import datetime

    foldername='/home/hypatia/ros/cnr/cells_ws/src/hrc-cell/hrc_mosaic_task_planning/hrc_mosaic_task_planning_interface/plans/comparison_for_review_tcybernetics/'
    filename = foldername + 'recipe_proposed_method' + '.yaml'
    now = datetime.now()
    file_obj = open(filename, 'w')
    file_obj.truncate(0)  # delete all content
    file_obj.write('recipe autogenerated: ' + now.strftime('%m/%d/%Y, %H:%M:%S'))
    file_obj.close()

    baseline = False
    with_sync = False

    tasks = [ ["A1",   "orange"],   ["A2",   "orange"], ["A3",   "orange"], ["A4",   "blue"],   ["A5",   "orange"],
              ["B1",   "orange"],   ["B2",   "blue"],   ["B3",   "orange"], ["B4",   "blue"],   ["B5",   "orange"],
              ["C1",   "orange"],   ["C2",   "blue"],   ["C3",   "orange"], ["C4",   "orange"], ["C5",   "orange"],
              ["D1",   "blue"],     ["D2",   "blue"],   ["D3",   "blue"],   ["D4",   "blue"],   ["D5",   "blue"],
              ["E1",   "white"],    ["E2",   "white"],  ["E3",   "white"],  ["E4",   "blue"],   ["E5",   "blue"],
              ["F1",   "blue"],     ["F2",   "blue"],   ["F3",   "blue"],   ["F4",   "white"],  ["F5",   "white"],
              ["G1",   "blue"],     ["G2",   "white"],  ["G3",   "white"],  ["G4",   "blue"],   ["G5",   "blue"],
              ["H1",   "blue"],     ["H2",   "blue"],   ["H3",   "blue"],   ["H4",   "white"],  ["H5",   "white"],
              ["I1",   "white"],    ["I2",   "white"],  ["I3",   "white"],  ["I4",   "blue"],   ["I5",   "blue"],
              ["J1",   "blue"],     ["J2",   "blue"],   ["J3",   "blue"],   ["J4",   "blue"],   ["J5",   "blue"] ]

    robot_skills = ["B2","G1","G5","A4","F2","J4","C1","E5","B5","B3","C4","A5","C5","A1",
                    "A2","A3","B4","J1","B1","C3","D1","D5","J5"]

    human_skills = ["H1","G4","J3","I5","D4","F4","E1","H5","H4","F1","C2","E2","F5","E3",
                    "I1","I3","I2","G3","D3","G2","D2","H3","I4","F3","H2","E4","J2"]

    if  len(human_skills)>=len(robot_skills):
        longer_list=human_skills
        robot_skills_eq=robot_skills.copy()
        human_skills_eq=human_skills[:len(robot_skills)-1]
        human_skills_remainder=human_skills[len(robot_skills):]
        prefix_longer_list="human"
    else:
        longer_list = robot_skills
        human_skills_eq=human_skills.copy()
        robot_skills_eq=robot_skills[:len(robot_skills)-1]
        robot_skills_remainder=robot_skills[len(robot_skills):]
        prefix_longer_list="robot"

    print(robot_skills)
    print(human_skills)

    orange_cnt=-1
    blue_cnt=-1
    white_cnt=-1
    id_command=0
    for idx in range(0,len(longer_list)):

        if idx>=len(robot_skills):
            task_robot_str=""
        else:
            task_robot_str = robot_skills[idx]

        if idx>=len(human_skills):
            task_human_str=""
        else:
            task_human_str = human_skills[idx]

        if baseline:
            if task_robot_str!="":
                for idx, task in enumerate(tasks):
                    if task[0]==task_robot_str:
                        color=task[1]
                if color=="orange":
                    orange_cnt=orange_cnt+1
                    cnt=orange_cnt
                elif color=="white":
                    white_cnt=white_cnt+1
                    cnt = white_cnt
                elif color=="blue":
                    blue_cnt=blue_cnt+1
                    cnt = blue_cnt
                task_robot="pick_"+color+"_box_"+str(cnt)
                printSkillsToYaml(filename, "robot", task_robot, "", id_command, with_sync)

            if task_human_str != "":
                for idx, task in enumerate(tasks):
                    if task[0]==task_human_str:
                        color=task[1]
                if color=="orange":
                    orange_cnt=orange_cnt+1
                    cnt=orange_cnt
                elif color=="white":
                    white_cnt=white_cnt+1
                    cnt = white_cnt
                elif color=="blue":
                    blue_cnt=blue_cnt+1
                    cnt = blue_cnt
                task_human="pick_"+color+"_box_"+str(cnt)
                printSkillsToYaml(filename, "human", task_human, "", id_command+1000, with_sync)

            id_command = id_command + 1

            if task_robot_str != "":
                task_robot = "place_" + task_robot_str
                printSkillsToYaml(filename, "robot", task_robot, "", id_command, with_sync)
            if task_human_str != "":
                task_human = "place_" + task_human_str
                printSkillsToYaml(filename, "human", task_human, "", id_command+1000, with_sync)
            id_command = id_command + 1

        else:
            if task_robot_str != "":
                task_robot="pickplace_"+task_robot_str
                if task_human_str != "":
                    task_human="pickplace_"+task_human_str
                else:
                    task_human=""
                printSkillsToYaml(filename, "robot", task_robot, task_human, id_command, with_sync)
            if task_human_str != "":
                task_human="pickplace_"+task_human_str
                if task_robot_str != "":
                    task_robot="pickplace_"+task_robot_str
                else:
                    task_robot=""
                printSkillsToYaml(filename, "human", task_human, task_robot, id_command+1000, with_sync)
            id_command=id_command+1

    printSkillsToYaml(filename, "robot", "end", "", id_command, False)
    printSkillsToYaml(filename, "human", "end", "", id_command+1000, False)
