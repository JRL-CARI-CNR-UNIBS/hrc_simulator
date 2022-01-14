# Author: Marco Faroni
# Email: marco.faroni@stiima.cnr.it
# Affiliation: CNR-STIIMA

# Input: a mongoDB database with the pickplace skills for the paper on Transactions on Cybernetics
# Output: a MongoDB collection containing the durations of tasks decomposed as pick-cube-1 and place-in-slot-A1
import sys
import numpy as np


def insert_doc(collection, doc, color, counter):
    slot=doc["name"][-2:]
    agents = ["ur5_on_guide","human_right_arm"]
    for agent in agents:
        try:
            success_rate = doc[agent + "_success_rate"]
            duration_avg = doc[agent + "_expected_duration"]
            std_dev = doc[agent + "_duration_stddev"]
            cnt = doc[agent + "_counter"]

            collection.update_one({"name": prefix_out_pick + color + "-cube-" + str(counter)},
                                  {"$set": {agent + "_success_rate": success_rate,
                                            agent + "_expected_duration": 0.6 * duration_avg,
                                            agent + "_duration_stddev": math.sqrt(std_dev),
                                            agent + "_counter": cnt}},
                                  upsert=True)

            collection.update_one({"name": prefix_out_place + slot},
                                  {"$set": {agent + "_success_rate": success_rate,
                                            agent + "_expected_duration": 0.4 * duration_avg,
                                            agent + "_duration_stddev": math.sqrt(std_dev),
                                            agent + "_counter": cnt}},
                                  upsert=True)
        except:
            try:
                success_rate = doc[agent + "_success_rate"]
                print("something wrong")
            except:
                pass



if __name__ == '__main__':

    print('Generating tasks duration and upload them to mongo...')

    from pymongo import MongoClient
    import math

    orange = ["A1","A2","A3","A5","B1","B3","B5","C1","C3","C4","C5"]
    white =  ["E1","E2","E3","F4","F5","G2","G3","H4","H5","I1","I2","I3"]

    blue=[]
    for ir in range(1,6):
        for ic in ["A","B","C","D","E","F","G","H","I","J"]:
            blue.append(ic+str(ir))
    blue_copy=blue.copy()
    for idx,cube in enumerate(blue_copy):
        for cube_or in orange:
            if cube==cube_or:
                blue.remove(cube)
        for cube_wh in white:
            if cube==cube_wh:
                blue.remove(cube)


    prefix_in="pickplace-"
    prefix_out_pick="pick-"
    prefix_out_place="place-"

    client = MongoClient()
    db_out = client.sharework_pellegrinelli
    coll_skills = db_out.hrc_task_properties

    counter_orange=0
    counter_white = 0
    counter_blue = 0

    added_tasks=[]

    coll_skills.delete_many({})

    for idx, slot in enumerate(orange):
        for idx2 in range(0,len(orange)):
            task_name = "move-from-slot-"+slot+"-to-cube-orange-"+str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot"]})
            task_name = "move-from-cube-orange-"+str(idx2)+"-to-slot-"+slot
            coll_skills.insert_one({"name": task_name,
                                    "type": "place",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot"]})
            counter_orange += 1
        for idx2 in range(0, len(blue)):
            task_name = "move-from-slot-"+slot+"-to-cube-blue-"+str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot"]})
            counter_blue += 1

    for idx, slot in enumerate(blue):
        for idx2 in range(0, len(orange)):
            task_name = "move-from-slot-" + slot + "-to-cube-orange-" + str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot"]})
            counter_orange += 1
        for idx2 in range(0, len(blue)):
            task_name = "move-from-slot-" + slot + "-to-cube-blue-" + str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot","human"]})
            task_name = "move-from-cube-blue-"+str(idx2)+"-to-slot-"+slot
            coll_skills.insert_one({"name": task_name,
                                    "type": "place",
                                    "description": "",
                                    "goal": "cube-blue-" + str(idx2),
                                    "agent": ["robot","human"]})
            counter_blue += 1
        for idx2 in range(0, len(white)):
            task_name = "move-from-slot-" + slot + "-to-cube-white-" + str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["human"]})
            counter_white += 1
    for idx, slot in enumerate(white):
        for idx2 in range(0, len(blue)):
            task_name = "move-from-slot-" + slot + "-to-cube-blue-" + str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["robot","human"]})
            counter_blue += 1
        for idx2 in range(0, len(white)):
            task_name = "move-from-slot-" + slot + "-to-cube-white-" + str(idx2)
            coll_skills.insert_one({"name": task_name,
                                    "type": "pick",
                                    "description": "",
                                    "goal": "cube-orange-" + str(idx2),
                                    "agent": ["human"]})
            task_name = "move-from-cube-white-"+str(idx2)+"-to-slot-"+slot
            coll_skills.insert_one({"name": task_name,
                                    "type": "place",
                                    "description": "",
                                    "goal": "cube-blue-" + str(idx2),
                                    "agent": ["human"]})
            counter_white += 1

    docs_tasks = coll_skills.find({})
    coll_results = db_out.hrc_task_durations
    coll_results.delete_many({})

    for doc in docs_tasks:
        for agent in doc["agent"]:
            success_rate = 0.95 + 0.05*np.random.uniform()
            duration_avg = 8.0 + 4*np.random.uniform()
            std_dev = 3.0 + 2*np.random.uniform()
            cnt = 5

            coll_results.update_one({"name": doc["name"]},
                                    {"$set": {agent + "_success_rate": success_rate,
                                              agent + "_expected_duration": duration_avg,
                                              agent + "_duration_stddev": std_dev,
                                              agent + "_counter": cnt}},
                                    upsert=True)

    sys.exit()

    if 0:
        is_blue = True
        for slot in orange:
            if doc["name"]==prefix_in+slot:
                insert_doc(coll_durations_out, doc, "orange", counter_orange)
                counter_orange=counter_orange+1
                is_blue = False
                added_tasks.append(slot)
        for slot in white:
            if doc["name"]==prefix_in+slot:
                insert_doc(coll_durations_out, doc, "white", counter_white)
                counter_white=counter_white+1
                is_blue = False
                added_tasks.append(slot)
        if is_blue==True:
            insert_doc(coll_durations_out, doc, "blue", counter_blue)
            counter_blue = counter_blue + 1
            added_tasks.append("blue")

    print(sorted(added_tasks))
    print("Added tasks: ", len(added_tasks))