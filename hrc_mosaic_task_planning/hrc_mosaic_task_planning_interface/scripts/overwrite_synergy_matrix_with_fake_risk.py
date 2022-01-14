
if __name__ == '__main__':
    print('Updating interaction matrix based on fake matrix...')

    from pymongo import MongoClient
    import math

    client = MongoClient()
    db = client.sharework
    coll_skills = db.hrc_task_properties
    coll_interaction = db.hrc_dynamic_risks

    agents=["ur5_on_guide", "human_right_arm"] # nome dei move_group
    other_agents=agents[::-1]

    blue_skills = []
    blue_boxes = ['A4', 'B2', 'B4', 'C2', 'D1', 'D2', 'D3', 'D4', 'D5', 'E4', 'E5', 'F1', 'F2', 'F3', 'G1', 'G4',
                  'G5', 'H1', 'H2', 'H3', 'I4', 'I5', 'J1', 'J2', 'J3', 'J4', 'J5']
    for item in blue_boxes:
        blue_skills.append('pickplace-' + item)

    cursor_dyn_risks = coll_interaction.find({})
    agent = agents[0]
    other_agent = other_agents[0]
    for task in cursor_dyn_risks:
        risk_fake = 0
        flag1 = int(task[agent + "_skill"] in blue_skills)
        flag2 = int(task[other_agent + "_skill"] in blue_skills)
        risk_fake = 20 * flag2 + 30 * flag1 * flag2
        coll_interaction.update_one({"_id": task["_id"]},
                                    {"$set": {"dynamic_risk": risk_fake}})

