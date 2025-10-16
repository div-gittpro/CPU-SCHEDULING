import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CPU Scheduling Simulator", layout="wide")

# ----------------------------
# CPU Scheduling Algorithms
# ----------------------------

def fcfs(processes):
    processes = sorted(processes, key=lambda x: x["arrival"])
    time = 0
    gantt, waiting, turnaround = [], {}, {}

    for p in processes:
        if time < p["arrival"]:
            time = p["arrival"]
        start = time
        finish = start + p["burst"]
        gantt.append((p["id"], start, finish))
        waiting[p["id"]] = start - p["arrival"]
        turnaround[p["id"]] = finish - p["arrival"]
        time = finish
    return gantt, waiting, turnaround


def sjf(processes):
    processes = sorted(processes, key=lambda x: x["arrival"])
    ready, gantt, waiting, turnaround = [], [], {}, {}
    time, i = 0, 0
    while i < len(processes) or ready:
        while i < len(processes) and processes[i]["arrival"] <= time:
            ready.append(processes[i])
            i += 1
        if ready:
            ready.sort(key=lambda x: x["burst"])
            p = ready.pop(0)
            start, finish = time, time + p["burst"]
            gantt.append((p["id"], start, finish))
            waiting[p["id"]] = start - p["arrival"]
            turnaround[p["id"]] = finish - p["arrival"]
            time = finish
        else:
            time += 1
    return gantt, waiting, turnaround


def priority_scheduling(processes):
    processes = sorted(processes, key=lambda x: x["arrival"])
    ready, gantt, waiting, turnaround = [], [], {}, {}
    time, i = 0, 0
    while i < len(processes) or ready:
        while i < len(processes) and processes[i]["arrival"] <= time:
            ready.append(processes[i])
            i += 1
        if ready:
            ready.sort(key=lambda x: x["priority"])
            p = ready.pop(0)
            start, finish = time, time + p["burst"]
            gantt.append((p["id"], start, finish))
            waiting[p["id"]] = start - p["arrival"]
            turnaround[p["id"]] = finish - p["arrival"]
            time = finish
        else:
            time += 1
    return gantt, waiting, turnaround


def round_robin(processes, quantum=2):
    queue, gantt, waiting, turnaround = [], [], {}, {}
    processes = sorted(processes, key=lambda x: x["arrival"])
    time, i = 0, 0
    remaining = {p["id"]: p["burst"] for p in processes}
    finish_time = {}

    while i < len(processes) or queue:
        while i < len(processes) and processes[i]["arrival"] <= time:
            queue.append(processes[i])
            i += 1
        if queue:
            p = queue.pop(0)
            exec_time = min(quantum, remaining[p["id"]])
            start, finish = time, time + exec_time
            gantt.append((p["id"], start, finish))
            remaining[p["id"]] -= exec_time
            time = finish
            if remaining[p["id"]] > 0:
                while i < len(processes) and processes[i]["arrival"] <= time:
                    queue.append(processes[i])
                    i += 1
                queue.append(p)
            else:
                finish_time[p["id"]] = time
        else:
            time += 1

    for p in processes:
        turnaround[p["id"]] = finish_time[p["id"]] - p["arrival"]
        waiting[p["id"]] = turnaround[p["id"]] - p["burst"]
    return gantt, waiting, turnaround


# ----------------------------
# Helpers
# ----------------------------

def plot_gantt(gantt):
    fig, ax = plt.subplots(figsize=(8, 2))
    for (pid, start, finish) in gantt:
        ax.barh(0, finish - start, left=start, edgecolor="black")
        ax.text((start + finish) / 2, 0, pid, ha="center", va="center", color="white")
    ax.set_yticks([])
    ax.set_xlabel("Time")
    st.pyplot(fig)


def show_results(gantt, waiting, turnaround):
    st.subheader("Gantt Chart")
    plot_gantt(gantt)
    df = pd.DataFrame({
        "Process": list(waiting.keys()),
        "Waiting Time": list(waiting.values()),
        "Turnaround Time": list(turnaround.values())
    })
    st.subheader("Results Table")
    st.dataframe(df)
    st.success(f"Average Waiting Time: {sum(waiting.values())/len(waiting):.2f}")
    st.success(f"Average Turnaround Time: {sum(turnaround.values())/len(turnaround):.2f}")


# ----------------------------
# Streamlit UI
# ----------------------------

st.title("⚙️ CPU Scheduling Simulator")

# Default processes
if "processes" not in st.session_state:
    st.session_state["processes"] = [
        {"id": "P1", "burst": 5, "arrival": 0, "priority": 1},
        {"id": "P2", "burst": 3, "arrival": 1, "priority": 2},
        {"id": "P3", "burst": 8, "arrival": 2, "priority": 3},
    ]

# Two columns layout
col1, col2 = st.columns(2)

with col1:
    st.header("Process Configuration")
    for p in st.session_state["processes"]:
        cols = st.columns(4)
        cols[0].text(p["id"])
        p["burst"] = cols[1].number_input("Burst", value=p["burst"], key=f"{p['id']}_burst")
        p["arrival"] = cols[2].number_input("Arrival", value=p["arrival"], key=f"{p['id']}_arrival")
        p["priority"] = cols[3].number_input("Priority", value=p["priority"], key=f"{p['id']}_priority")
    if st.button("➕ Add Process"):
        new_id = f"P{len(st.session_state['processes'])+1}"
        st.session_state["processes"].append({"id": new_id, "burst": 1, "arrival": 0, "priority": 1})

with col2:
    st.header("Scheduling Algorithms")
    algo = st.radio("Select Algorithm", ["FCFS", "SJF", "Priority", "Round Robin", "Compare All"])
    if algo != "Compare All":
        if algo == "FCFS":
            gantt, waiting, turnaround = fcfs(st.session_state["processes"])
        elif algo == "SJF":
            gantt, waiting, turnaround = sjf(st.session_state["processes"])
        elif algo == "Priority":
            gantt, waiting, turnaround = priority_scheduling(st.session_state["processes"])
        elif algo == "Round Robin":
            quantum = st.slider("Quantum", 1, 5, 2)
            gantt, waiting, turnaround = round_robin(st.session_state["processes"], quantum)
        show_results(gantt, waiting, turnaround)
    else:
        for name, func in [("FCFS", fcfs), ("SJF", sjf), ("Priority", priority_scheduling), ("Round Robin (q=2)", lambda p: round_robin(p,2))]:
            st.markdown(f"### {name}")
            gantt, waiting, turnaround = func(st.session_state["processes"])
            show_results(gantt, waiting, turnaround)
