import matplotlib.pyplot as plt
import pandas as pd
import glob
import seaborn as sns

def main():

    result= pd.DataFrame(columns=["name", "time","read_data_time","process_data_time"], index=range(3))
    count= 0
    all_files = glob.glob("*.out")
    # read all out files
    for file in all_files:
        with open(file) as fp:
            result.iloc[count, 0] = "case "+str(count+1)+": "+str(file).split(".")[0]
            for line in fp:
                if "Wall-clock" in line.split():
                    result.iloc[count, 1] = line.split()[3]
                if " ".join(line.split()[:4]) == "Time to read data:":
                    result.iloc[count, 2] = line.split()[4]
                if " ".join(line.split()[:4]) == "Time to process data:":
                    result.iloc[count, 3] = line.split()[4]
        count+=1


    result["time"] = pd.to_timedelta(result["time"])
    result["total_sec"]=result["time"].dt.seconds
    result["process_data_time"] =result["process_data_time"].astype(float)
    result["read_data_time"] =result["read_data_time"].astype(float)
    df = pd.melt(result[["name","total_sec","process_data_time","read_data_time"]],
                 id_vars=["name","total_sec"], var_name="component")
    df["component"] =df["component"].astype("category")

    df["value"] = [round(ele, 3) for ele in df["value"].values]

    # plot bar chart
    plt.figure()
    ax = sns.barplot(x="name", y="value", hue="component",  data=df)
    # add value to each bar
    for ct in ax.containers:
        ax.bar_label(ct)

    plt.xlabel("")
    plt.ylabel("Wall-clock time (seconds)")
    plt.title("Speed performance comparison")
    plt.savefig("speed_performance.pdf")

if __name__ == "__main__":
    main()
