# import library and dataset
import matplotlib.pyplot as plt
from pymongo import MongoClient
import statistics
import pandas as pd
import seaborn as sns


def main():

    client = MongoClient()
    db = client.sharework
    collections = [db.results_tamp_baseline, db.results_tamp_multi_obj] #MODIFY NAMES





if __name__ == '__main__':
    main()
