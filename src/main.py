from Utility import *
import mmap
import time
import json
import re
import sys
sys.path.append("mpi4py")
sys.path.append("pandas")
from mpi4py import MPI
import math
import psutil
import pandas as pd

CELL_NAME = [j+str(i) for j in ["A","B","C","D"] for i in range(1,5)]
ID_TO_CELL = {"24":"D4", "23":"C4", "22":"B4", "21":"A4",
              "20":"D3", "19":"C3", "18":"B3", "17":"A3",
              "16":"D2", "15":"C2", "14":"B2", "13":"A2",
              "12":"D1", "11":"C1", "10":"B1", "9":"A1"}

# read grid file
def get_grid(file_name):
    result = {}
    with open(file_name, "r") as fp:
        data = json.load(fp)
        for dd in data["features"]:
            curr_id = str(dd["properties"]["id"])
            name = ID_TO_CELL[curr_id]
            polyg = dd["geometry"]["coordinates"][0]
            poly = Cell([list(i) for i in polyg], name)

            result[name] = poly
    return result

# for a given coordinates and language, update the grid
def update_grid_count(grid, pt, lang):
    for name, cell in grid.items():
        cell.update_count(pt=pt, lang=lang)

# get the formatted result summary
def get_result(grid):
    final = pd.DataFrame(columns=["cell","total_tweets","num_langs","top_10"])

    for name, cell in grid.items():
        cell.get_summary()
        cell_df = pd.DataFrame([cell.summary.values()], columns=["cell","total_tweets","num_langs","top_10"])
        final = pd.concat([final, cell_df], sort=False, axis=0)
    final = final.sort_values(["cell"])
    final.columns = ["Cell", "#Total Tweets",
                      "#Number of Languages Used", "#Top 10 Languages & #Tweets"]
    return final

def read_coords(lst, grid):
    # [[x_coord, y_coord, lang], [x_coord, y_coord, lang]]
    if lst:
        for rec in lst:
            pt = Point(rec[0], rec[1])
            update_grid_count(grid=grid, pt=pt, lang=rec[2])


# use mmap function to read file with smaller memory,
# divide whole file into parts for different MPI processors,
# and compile the steps and functions to get results needed.
def reading_compiling_part(map, process_size, file_bytes, current_rank, comm):

    # according to rank number, compute the end position of processors
    end_position = process_size * (current_rank + 1)

    count = 0
    # get the current position in file
    current_position = map.tell()
    records = []

    while current_position < file_bytes and current_position <= end_position:

        # ijson.items(map, 'rows.item')
        item = map.readline().decode("utf-8")

        # if arriving the end of file, jump out of the while loop
        if not item:
            break

        # extract last three terms ",\r\n" to satisfy dict format
        if item[:6] == '{"id":' and item[-3:] == ",\r\n":
            json_item = json.loads(item[:-3])

        # the last record has a different ending with others ("]}\r\n" for small/tinyTwitter,
        # "\r\n" for bigTwitter), so it needs to be extracted last four terms
        elif item[:6] == '{"id":':
            json_item = json.loads(item[:-2])
        else:
            continue

        # update current position
        current_position = map.tell()

        # compile functions to get languages and #tweets (Add Melody's part)
        language = json_item["doc"]["lang"]
        coordinates = json_item["doc"]["coordinates"]

        # determine whether the tweet is useful
        if (language is None) or (coordinates is None) or (language == "und"):
            count += 1
            continue

        coord = coordinates["coordinates"]
        records.append(coord+[language])

    # if the rank is 0, it will gather all results from others like [rank0, rank1, ...].
    # if the rank is not 0, their results are None.
    useful_records = comm.gather(records, root=0)

    # finally, return gathering results from all ranks
    return useful_records


# the MPI process to compute different parts of files parallely
def mpi_process(comm, current_rank, current_size, map, file_size):

    # calculate the byte size each processor will take
    process_size = math.ceil(file_size / current_size)

    # for each MPI processor, move to corresponding position in map
    # for example, rank0-0k, rank1-1k, rank2-2k where k is block size
    map.seek(process_size*current_rank)

    print(current_rank)

    if current_rank == 0:
        str_total_rows = map.readline().decode("utf-8")
        total_rows = int(re.findall(r'\"total_rows\":(.*?),', str_total_rows)[0])

    # other ranks except 0, drop the last record belonging to previous rank
    else:
        map.readline()

    useful_records = reading_compiling_part(map, process_size, file_size, current_rank, comm)

    # MPI.Finalize()
    if current_rank == 0:

        # combine records from all processors into one list
        combined_records = [i for j in useful_records for i in j]
        # print(combined_records)

        return combined_records

def main():
    # count memory and time usage
    pid = psutil.Process(os.getpid())
    memory_start = pid.memory_full_info().uss / 1024
    start_time = time.time()

    grid = get_grid("sydGrid.json")
    with open('bigTwitter.json', 'r', encoding='utf-8') as f:

        # get coordinates and languages
        outer_map = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
        # count the total bytes in the file and calculate
        # the bytes each MPI processor to compile
        file_bytes = outer_map.size()

        comm = MPI.COMM_WORLD
        current_rank = comm.Get_rank()
        current_size = comm.Get_size()

        processed_data = mpi_process(comm, current_rank, current_size, outer_map, file_bytes)
        outer_map.close()

    # update cell count
    if current_rank == 0:
        time1 = time.time()
        print("Time to read data:", time1 - start_time, " seconds")
        read_coords(processed_data, grid)
        result = get_result(grid)
        result.to_csv("bigTwitter_result.csv", index=False)
        time2 = time.time()
        print("Time to process data:", time2 - time1, " seconds")

    end_time = time.time()
    total_time = end_time-start_time
    print("Total Time Usage: "+str(total_time)+"s")

    memory_end = pid.memory_full_info().uss/1024
    total_memory = memory_end - memory_start
    print("Total Memory Usage: "+str(total_memory)+"KB")

if __name__ == "__main__":
    main()
