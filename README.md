# OS Simulator

## Overview
This project is a **GUI-based simulator** for key **Operating System algorithms**, including:

- CPU Scheduling
- Contiguous Memory Allocation
- Page Replacement

---

## Features

### CPU Scheduling Algorithms
- **First Come First Serve (FCFS)**
- **Shortest Job First (SJF) – Non-preemptive**
- **Shortest Job First (SJF) – Preemptive**
- **Round Robin (RR)**

#### The simulator calculates:
- Waiting Time (ms)
- Turnaround Time (ms)
- Average Waiting Time (ms)
- Average Turnaround Time (ms)
- Gantt Chart

---

### Contiguous Memory Allocation
- **First Fit**
- **Best Fit**
- **Worst Fit**

#### The simulator shows:
- Allocated memory blocks (KB)
- Remaining memory (KB)

---

### Page Replacement Algorithms
- **FIFO**
- **Optimal**
- **LRU**

#### The simulator calculates:
- Number of Page Faults
- Number of Hits
- Hit Ratio
- Miss Ratio
- Final Frame State

---

## Requirements
- Python 3.x
- tkinter (usually included with Python)

---

## How to Run

1. Download the project files
2. Open terminal in the project folder
3. Run:

```bash
python3 os_simulator.py
