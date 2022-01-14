# Author: Marco Faroni
# Email: marco.faroni@stiima.cnr.it
# Affiliation: CNR-STIIMA

# Input: a mongoDB database with the pickplace skills for the paper on Transactions on Cybernetics
# Output: a MongoDB collection containing the durations of tasks decomposed as pick-cube-1 and place-in-slot-A1


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
    white = ["E1","E2","E3","F4","F5","G2","G3","H4","H5","I1","I2","I3"]

    prefix_in="pickplace-"
    prefix_out_pick="pick-"
    prefix_out_place="place-"

    client = MongoClient()
    db = client.sharework
    coll_skills = db.hrc_task_properties
    coll_durations_source = db.hrc_task_durations
    coll_durations_out = db.hrc_task_durations_decomposed

    coll_durations_out.delete_many({})
    docs = coll_durations_source.find({})

    counter_orange=0
    counter_white = 0
    counter_blue = 0

    added_tasks=[]

    for doc in docs:
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