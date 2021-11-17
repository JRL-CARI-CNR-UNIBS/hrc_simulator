# Author: Marco Faroni
# Email: marco.faroni@stiima.cnr.it
# Affiliation: CNR-STIIMA

# Input: a mongoDB database with the possible skills performed by the human and the robot
#        a mongoDB database with results of the execution of such skills
# Output: a mongoDB database that stores success rate and cost of the pairs of tasks
#         average values of the tasks durations

if __name__ == '__main__':
    print('Updating task durations and interaction matrix based on past results...')

    from pymongo import MongoClient
    import math

    client = MongoClient()
    db = client.test_mosaic
    coll_skills = db.tasks_properties
    coll_results = db.tasks_results
    coll_interaction = db.dynamic_risks
    coll_durations = db.tasks_durations

    coll_durations.delete_many({})
    coll_interaction.delete_many({})
    agents=["ur5_on_guide", "human_right_arm"] # nome dei move_group
    other_agents=agents[::-1]
    for agent, other_agent in zip(agents,other_agents):
        cursor_skills=coll_skills.find({},{"name": 1, "_id": 0})
        for skill in cursor_skills:
            duration_cum = 0.0
            outcome_cum = 0
            duration_mean = 0.0
            success_rate_mean = 0.0
            varianceM2 = 0.0
            cursor_results=coll_results.find({"agent": agent, "name": skill["name"]})
            if cursor_results.count()==0:
                duration_avg=-999.0
                success_rate=-999.0
                std_dev=-999.0
            else:
                iter=0
                successes = 0
                for res in cursor_results:
                    # sum all durations and outcomes to get average
                    iter+=1
                    outcome_cum=outcome_cum+int(res["outcome"])
                    success_rate_mean = success_rate_mean + (float(res["outcome"]) - success_rate_mean)/iter
                    if int(res["outcome"])==1:
                        successes+=1
                        duration_cum += float(res["duration_real"])
                        delta = float(res["duration_real"]) - duration_mean
                        duration_mean += delta/successes
                        delta2 = float(res["duration_real"]) - duration_mean
                        varianceM2 += delta*delta2

                    # analyze interaction with concurrent tasks
                    for task in res["concurrent_tasks"]:
                        print(res["name"] + ": " + task)
                        pair_outcome = int(res["outcome"])
                        if pair_outcome==1 and res["duration_planned"]<0.01:
                            pair_outcome=0
                        if pair_outcome==1:
                            pair_dynamic_risk = float(res["duration_real"])/float(res["duration_planned"])
                        else:
                            pair_dynamic_risk=0.0
                        pair = coll_interaction.find_one({agent + "_skill": skill["name"], other_agent + "_skill": task})
                        if pair:
                            counter_old = float(pair["counter"])
                            succ_rate_old = float(pair["success_rate"])
                            risk_old = float(pair["dynamic_risk"])
                            counter_success=counter_old*succ_rate_old
                            coll_interaction.update_one({agent + "_skill": skill["name"], other_agent + "_skill": task},
                                                        {"$set": {"success_rate": (succ_rate_old * counter_old + pair_outcome) / (counter_old + 1),
                                                         "dynamic_risk": (risk_old * counter_success + pair_dynamic_risk) / (counter_success + pair_outcome),
                                                         "counter": counter_old+1}})
                        elif pair_outcome:
                            coll_interaction.insert_one({agent + "_skill": skill["name"], other_agent + "_skill": task,
                                                         "success_rate": pair_outcome,
                                                         "dynamic_risk": pair_dynamic_risk,
                                                         "counter": 1})

                success_rate = outcome_cum/(cursor_results.count())
                if successes > 0:
                    duration_avg = duration_cum / successes
                if successes > 1:
                    std_dev=math.sqrt( varianceM2/(successes-1) )

                print("avg 1: ", duration_avg)
                print("avg 2: ", duration_mean)
                print(std_dev, successes)
                print("\n")

                #update duration and outcome in coll_skills
                coll_durations.update_one({"name": skill["name"]},
                                          {"$set": {agent+"_success_rate": success_rate,
                                                    agent+"_expected_duration": duration_avg,
                                                    agent+"_duration_stddev": std_dev,
                                                    agent+"_counter": cursor_results.count()}},
                                          upsert=True)

            #print([skill["name"], duration_avg, success_rate])

