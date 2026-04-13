import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


# ---------------- SAFE INPUT ----------------
def safe_int(val, name="Input"):
    try:
        return int(val)
    except Exception:
        messagebox.showerror("Invalid Input", f"{name} must be a number.")
        return None


# ---------------- TABLE + GANTT ----------------
def format_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep = "-+-".join("-" * w for w in col_widths)
    rows_str = []
    for row in rows:
        rows_str.append(
            " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        )
    return "\n".join([line, sep] + rows_str)


def gantt_chart(gantt):
    if not gantt:
        return "No execution"

    line = ""
    time_line = ""
    for pid, s, e in gantt:
        block = f"| {pid} "
        line += block
        time_line += f"{s}".ljust(len(block))
    time_line += str(gantt[-1][2])
    line += "|"
    return line + "\n" + time_line


def averages_from_results(results):
    avg_wait = sum(row[3] for row in results) / len(results) if results else 0
    avg_tat = sum(row[4] for row in results) / len(results) if results else 0
    return avg_wait, avg_tat


# ---------------- CPU ALGORITHMS ----------------
def fcfs(procs):
    procs = sorted(procs, key=lambda x: (x["arrival"], x["pid"]))
    t = 0
    res = []
    gantt = []

    for p in procs:
        if t < p["arrival"]:
            t = p["arrival"]
        start = t
        t += p["burst"]
        end = t
        wt = start - p["arrival"]
        tat = end - p["arrival"]
        res.append([p["pid"], p["arrival"], p["burst"], wt, tat])
        gantt.append((p["pid"], start, end))

    return res, gantt



def sjf_non_preemptive(procs):
    procs = sorted(procs, key=lambda x: (x["arrival"], x["pid"]))
    t = 0
    done = []
    ready = []
    i = 0
    gantt = []

    while len(done) < len(procs):
        while i < len(procs) and procs[i]["arrival"] <= t:
            ready.append(procs[i])
            i += 1

        if not ready:
            if i < len(procs):
                t = procs[i]["arrival"]
            continue

        ready.sort(key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        p = ready.pop(0)
        start = t
        t += p["burst"]
        end = t
        wt = start - p["arrival"]
        tat = end - p["arrival"]
        done.append([p["pid"], p["arrival"], p["burst"], wt, tat])
        gantt.append((p["pid"], start, end))

    return done, gantt



def sjf_preemptive(procs):
    t = 0
    remaining = {p["pid"]: p["burst"] for p in procs}
    arrival = {p["pid"]: p["arrival"] for p in procs}
    burst = {p["pid"]: p["burst"] for p in procs}
    done = set()
    gantt = []
    current = None
    start = 0

    while len(done) < len(procs):
        available = [
            p["pid"]
            for p in procs
            if arrival[p["pid"]] <= t and p["pid"] not in done
        ]

        if not available:
            t += 1
            continue

        chosen = min(available, key=lambda x: (remaining[x], arrival[x], x))

        if current != chosen:
            if current is not None:
                gantt.append((current, start, t))
            current = chosen
            start = t

        remaining[chosen] -= 1
        t += 1

        if remaining[chosen] == 0:
            gantt.append((current, start, t))
            done.add(chosen)
            current = None

    res = []
    for p in procs:
        end = max(e for pid, s, e in gantt if pid == p["pid"])
        tat = end - p["arrival"]
        wt = tat - burst[p["pid"]]
        res.append([p["pid"], p["arrival"], p["burst"], wt, tat])

    return res, gantt



def round_robin(procs, q):
    t = 0
    queue = []
    remaining = {p["pid"]: p["burst"] for p in procs}
    arrival = {p["pid"]: p["arrival"] for p in procs}
    done = {}
    added = set()
    gantt = []

    while True:
        for p in sorted(procs, key=lambda x: (x["arrival"], x["pid"])):
            if p["arrival"] <= t and p["pid"] not in added and p["pid"] not in done:
                queue.append(p["pid"])
                added.add(p["pid"])

        if not queue:
            if len(done) == len(procs):
                break
            t += 1
            continue

        pid = queue.pop(0)
        run = min(q, remaining[pid])
        start = t
        t += run
        end = t
        remaining[pid] -= run
        gantt.append((pid, start, end))

        for p in sorted(procs, key=lambda x: (x["arrival"], x["pid"])):
            if start < p["arrival"] <= t and p["pid"] not in added and p["pid"] not in done:
                queue.append(p["pid"])
                added.add(p["pid"])

        if remaining[pid] > 0:
            queue.append(pid)
        else:
            done[pid] = t

    res = []
    for p in procs:
        tat = done[p["pid"]] - p["arrival"]
        wt = tat - p["burst"]
        res.append([p["pid"], p["arrival"], p["burst"], wt, tat])

    return res, gantt


# ---------------- MEMORY ----------------
def first_fit(blocks, processes):
    working = blocks.copy()
    alloc = [-1] * len(processes)
    remaining = working.copy()
    for i in range(len(processes)):
        for j in range(len(working)):
            if working[j] >= processes[i]:
                alloc[i] = j
                working[j] -= processes[i]
                break
    remaining = working
    return alloc, remaining



def best_fit(blocks, processes):
    working = blocks.copy()
    alloc = [-1] * len(processes)
    for i in range(len(processes)):
        best = -1
        for j in range(len(working)):
            if working[j] >= processes[i]:
                if best == -1 or working[j] < working[best]:
                    best = j
        if best != -1:
            alloc[i] = best
            working[best] -= processes[i]
    return alloc, working



def worst_fit(blocks, processes):
    working = blocks.copy()
    alloc = [-1] * len(processes)
    for i in range(len(processes)):
        worst = -1
        for j in range(len(working)):
            if working[j] >= processes[i]:
                if worst == -1 or working[j] > working[worst]:
                    worst = j
        if worst != -1:
            alloc[i] = worst
            working[worst] -= processes[i]
    return alloc, working



def memory_result_table(blocks, processes, alloc, remaining):
    headers = ["Process", "Process Size (KB)", "Allocated Block", "Status"]
    rows = []
    for i, size in enumerate(processes):
        if alloc[i] == -1:
            rows.append([f"P{i+1}", f"{size} KB", "-", "Not Allocated"])
        else:
            rows.append([f"P{i+1}", f"{size} KB", f"Block {alloc[i]+1}", "Allocated"])

    footer = "Remaining Block Sizes: " + ", ".join(
        f"Block {i+1} = {remaining[i]} KB" for i in range(len(remaining))
    )
    return format_table(headers, rows) + "\n\n" + footer


# ---------------- PAGE REPLACEMENT ----------------
def page_stats(faults, total_refs):
    hits = total_refs - faults
    hit_ratio = hits / total_refs if total_refs else 0
    miss_ratio = faults / total_refs if total_refs else 0
    return hits, hit_ratio, miss_ratio



def fifo(refs, frame_count):
    frames = []
    faults = 0
    idx = 0

    for r in refs:
        if r not in frames:
            faults += 1
            if len(frames) < frame_count:
                frames.append(r)
            else:
                frames[idx] = r
                idx = (idx + 1) % frame_count

    return {
        "faults": faults,
        "final_frames": frames.copy(),
    }



def optimal(refs, frame_count):
    frames = []
    faults = 0

    for i, r in enumerate(refs):
        if r not in frames:
            faults += 1
            if len(frames) < frame_count:
                frames.append(r)
            else:
                future = refs[i + 1 :]
                idx = max(
                    range(len(frames)),
                    key=lambda j: future.index(frames[j]) if frames[j] in future else 999999,
                )
                frames[idx] = r

    return {
        "faults": faults,
        "final_frames": frames.copy(),
    }



def lru(refs, frame_count):
    frames = []
    recent = {}
    faults = 0

    for i, r in enumerate(refs):
        if r not in frames:
            faults += 1
            if len(frames) < frame_count:
                frames.append(r)
            else:
                lru_page = min(frames, key=lambda x: recent.get(x, -1))
                frames[frames.index(lru_page)] = r
        recent[r] = i

    return {
        "faults": faults,
        "final_frames": frames.copy(),
    }


# ---------------- GUI ----------------
root = tk.Tk()
root.title("OS Simulator")
root.geometry("1050x780")


def clear():
    for w in root.winfo_children():
        w.destroy()


# ---------------- CPU PAGE ----------------
def cpu_page():
    clear()
    tk.Label(root, text="CPU Scheduling", font=("Arial", 22)).pack(pady=10)

    top_frame = tk.Frame(root)
    top_frame.pack(pady=5)

    tk.Label(top_frame, text="Number of Processes:").grid(row=0, column=0, padx=5, pady=5)
    num_entry = ttk.Entry(top_frame, width=10)
    num_entry.insert(0, "3")
    num_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(top_frame, text="Time Quantum (ms):").grid(row=0, column=2, padx=5, pady=5)
    q_entry = ttk.Entry(top_frame, width=10)
    q_entry.insert(0, "2")
    q_entry.grid(row=0, column=3, padx=5, pady=5)

    entries_frame = tk.Frame(root)
    entries_frame.pack(pady=10)

    entries = []

    def build_process_inputs():
        for widget in entries_frame.winfo_children():
            widget.destroy()
        entries.clear()

        count = safe_int(num_entry.get(), "Number of Processes")
        if count is None:
            return
        if count <= 0:
            messagebox.showerror("Invalid Input", "Number of Processes must be greater than 0.")
            return

        headers = ["PID", "Arrival Time (ms)", "Burst Time (ms)"]
        for c, h in enumerate(headers):
            tk.Label(entries_frame, text=h, font=("Arial", 10, "bold")).grid(
                row=0, column=c, padx=10, pady=5
            )

        for i in range(count):
            pid = ttk.Entry(entries_frame, width=12)
            pid.insert(0, f"P{i+1}")
            pid.grid(row=i + 1, column=0, padx=10, pady=4)

            arr = ttk.Entry(entries_frame, width=12)
            arr.insert(0, "0")
            arr.grid(row=i + 1, column=1, padx=10, pady=4)

            burst = ttk.Entry(entries_frame, width=12)
            burst.insert(0, "1")
            burst.grid(row=i + 1, column=2, padx=10, pady=4)

            entries.append((pid, arr, burst))

    ttk.Button(top_frame, text="Set Processes", command=build_process_inputs).grid(
        row=0, column=4, padx=8, pady=5
    )

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def run():
        procs = []
        if not entries:
            build_process_inputs()
            if not entries:
                return

        for pid, a, b in entries:
            pid_val = pid.get().strip() or f"P{len(procs)+1}"
            arr = safe_int(a.get(), "Arrival")
            burst = safe_int(b.get(), "Burst")
            if arr is None or burst is None:
                return
            if arr < 0 or burst <= 0:
                messagebox.showerror(
                    "Invalid Input",
                    "Arrival time must be 0 or more, and burst time must be greater than 0.",
                )
                return
            procs.append({"pid": pid_val, "arrival": arr, "burst": burst})

        q = safe_int(q_entry.get(), "Quantum")
        if q is None:
            return
        if q <= 0:
            messagebox.showerror("Invalid Input", "Quantum must be greater than 0.")
            return

        algos = [
            ("FCFS", fcfs),
            ("SJF Non-Preemptive", sjf_non_preemptive),
            ("SJF Preemptive", sjf_preemptive),
            ("Round Robin", lambda x: round_robin(x, q)),
        ]

        out.delete("1.0", "end")
        for name, func in algos:
            res, gantt = func([dict(p) for p in procs])
            avg_wait, avg_tat = averages_from_results(res)
            out.insert("end", f"\n--- {name} ---\n")
            out.insert(
                "end",
                format_table(
                    ["PID", "Arrival (ms)", "Burst (ms)", "Waiting Time (ms)", "Turnaround Time (ms)"],
                    res,
                )
                + "\n",
            )
            out.insert("end", f"\nAverage Waiting Time: {avg_wait:.2f}\n")
            out.insert("end", f"Average Turnaround Time: {avg_tat:.2f}\n")
            out.insert("end", "\nGantt Chart:\n")
            out.insert("end", gantt_chart(gantt) + "\n")

    build_process_inputs()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    ttk.Button(button_frame, text="Run", command=run).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Back", command=main_menu).pack(side="left", padx=6)


# ---------------- MEMORY PAGE ----------------
def memory_page():
    clear()
    tk.Label(root, text="Contiguous Memory Allocation", font=("Arial", 22)).pack(pady=10)

    tk.Label(root, text="Memory Block Sizes (KB, space-separated):").pack()
    block_entry = ttk.Entry(root, width=60)
    block_entry.insert(0, "100 500 200")
    block_entry.pack(pady=4)

    tk.Label(root, text="Process Memory Requests (KB, space-separated):").pack()
    proc_entry = ttk.Entry(root, width=60)
    proc_entry.insert(0, "212 417 112")
    proc_entry.pack(pady=4)

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def run():
        try:
            blocks = list(map(int, block_entry.get().split()))
            procs = list(map(int, proc_entry.get().split()))
        except Exception:
            messagebox.showerror("Error", "Please enter numbers only.")
            return

        if not blocks or not procs:
            messagebox.showerror("Error", "Please enter at least one block and one process.")
            return
        if any(b <= 0 for b in blocks) or any(p <= 0 for p in procs):
            messagebox.showerror("Error", "All block and process sizes must be greater than 0.")
            return

        ff_alloc, ff_remaining = first_fit(blocks, procs)
        bf_alloc, bf_remaining = best_fit(blocks, procs)
        wf_alloc, wf_remaining = worst_fit(blocks, procs)

        out.delete("1.0", "end")
        out.insert("end", "--- First Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, ff_alloc, ff_remaining) + "\n\n")

        out.insert("end", "--- Best Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, bf_alloc, bf_remaining) + "\n\n")

        out.insert("end", "--- Worst Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, wf_alloc, wf_remaining) + "\n")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    ttk.Button(button_frame, text="Run", command=run).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Back", command=main_menu).pack(side="left", padx=6)


# ---------------- PAGE REPLACEMENT ----------------
def page_page():
    clear()
    tk.Label(root, text="Page Replacement", font=("Arial", 22)).pack(pady=10)

    tk.Label(root, text="Number of Frames:").pack()
    f_entry = ttk.Entry(root, width=20)
    f_entry.insert(0, "3")
    f_entry.pack(pady=4)

    tk.Label(root, text="Reference String (space-separated):").pack()
    ref_entry = ttk.Entry(root, width=60)
    ref_entry.insert(0, "7 0 1 2 0 3")
    ref_entry.pack(pady=4)

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def run():
        f = safe_int(f_entry.get(), "Number of Frames")
        if f is None:
            return
        if f <= 0:
            messagebox.showerror("Error", "Number of Frames must be greater than 0.")
            return

        try:
            refs = list(map(int, ref_entry.get().split()))
        except Exception:
            messagebox.showerror("Error", "Invalid reference string")
            return

        if not refs:
            messagebox.showerror("Error", "Reference string cannot be empty.")
            return

        results = {
            "FIFO": fifo(refs, f),
            "Optimal": optimal(refs, f),
            "LRU": lru(refs, f),
        }

        out.delete("1.0", "end")
        out.insert("end", f"Frames: {f}\n")
        out.insert("end", f"Reference String: {' '.join(map(str, refs))}\n\n")

        for algo_name, result in results.items():
            faults = result["faults"]
            hits, hit_ratio, miss_ratio = page_stats(faults, len(refs))
            final_frames = result["final_frames"]

            out.insert("end", f"--- {algo_name} ---\n")
            out.insert("end", f"Page Faults: {faults}\n")
            out.insert("end", f"Hits: {hits}\n")
            out.insert("end", f"Hit Ratio: {hit_ratio:.2f}\n")
            out.insert("end", f"Miss Ratio: {miss_ratio:.2f}\n")
            out.insert(
                "end",
                "Final Frame State: "
                + (" ".join(map(str, final_frames)) if final_frames else "None")
                + "\n\n",
            )

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    ttk.Button(button_frame, text="Run", command=run).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Back", command=main_menu).pack(side="left", padx=6)


# ---------------- MAIN ----------------
def main_menu():
    clear()
    tk.Label(root, text="OS Simulator", font=("Arial", 26)).pack(pady=20)
    ttk.Button(root, text="CPU Scheduling", command=cpu_page).pack(pady=10)
    ttk.Button(root, text="Contiguous Memory Allocation", command=memory_page).pack(pady=10)
    ttk.Button(root, text="Page Replacement", command=page_page).pack(pady=10)
    ttk.Button(root, text="Exit", command=root.destroy).pack(pady=20)


main_menu()
root.mainloop()