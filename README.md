# OS.Simulator

This project is a GUI-based simulator for key Operating System algorithms, including CPU Scheduling, Contiguous Memory Allocation, and Page Replacement.
-------------------------------------------------------
Features
CPU Scheduling Algorithms
First Come First Serve (FCFS)
Shortest Job First (SJF) – Non-preemptive
Shortest Job First (SJF) – Preemptive
Round Robin (RR)

The simulator calculates:
Waiting Time (ms)
Turnaround Time (ms)
Average Waiting Time (ms)
Average Turnaround Time (ms)
Gantt Chart
-------------------------------------------------------
Contiguous Memory Allocation
First Fit
Best Fit
Worst Fit

The simulator shows:
Allocated memory blocks (KB)
Remaining memory (KB)
-------------------------------------------------------
Page Replacement Algorithms
FIFO
Optimal
LRU

The simulator calculates:
Number of Page Faults
Number of Hits
Hit Ratio
Miss Ratio
Final Frame State
-------------------------------------------------------
Requirements
Python 3.x
tkinter (usually included with Python)
-------------------------------------------------------
How to Run
Download the project files
Open terminal in the project folder
Run:
python os_simulator.py
-------------------------------------------------------
Sample Inputs
CPU Scheduling example:
Number of Processes = 4
Arrival Time (ms):
0 1 2 3
Burst Time (ms):
5 3 8 6
Quantum = 2
-------------------------------------------------------
Page Replacement example:
Number of Frames = 3
Reference String:
7 0 1 2 0 3 0 4
-------------------------------------------------------
Output
The program displays results in table format and visual Gantt charts.
