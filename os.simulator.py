import tkinter as tk
from tkinter import ttk, scrolledtext


# ---------------- SAFE INPUT ----------------
def normalize_number_text(value):
    value = str(value).strip()

    arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    eastern_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

    value = value.translate(arabic_digits)
    value = value.translate(eastern_digits)

    value = value.replace("٫", ".")
    value = value.replace(",", ".")

    return value


def safe_float(value):
    try:
        return float(normalize_number_text(value))
    except Exception:
        return None


def safe_int(value):
    try:
        value = normalize_number_text(value)
        if "." in value:
            return None
        return int(value)
    except Exception:
        return None


def safe_float_list(value):
    try:
        parts = normalize_number_text(value).split()
        return [float(x) for x in parts]
    except Exception:
        return None


def safe_int_list(value):
    try:
        parts = normalize_number_text(value).split()
        nums = []
        for x in parts:
            if "." in x:
                return None
            nums.append(int(x))
        return nums
    except Exception:
        return None


def show_output_error(out, field_name, example="2 or 5.7"):
    out.delete("1.0", "end")
    out.insert(
        "end",
        f"Invalid Input\n\n"
        f"You entered a letter or invalid value in {field_name}.\n"
        f"Please try again using numbers only.\n\n"
        f"Example: {example}"
    )


def show_custom_error(out, message):
    out.delete("1.0", "end")
    out.insert("end", f"Invalid Input\n\n{message}")


def format_number(num):
    if isinstance(num, float) and num.is_integer():
        return int(num)
    if isinstance(num, float):
        return round(num, 4)
    return num


def with_unit(value, unit):
    return f"{format_number(value)} {unit}"


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


def gantt_chart(gantt, unit="ms"):
    if not gantt:
        return "No execution"

    line = ""
    time_line = ""

    for pid, s, e in gantt:
        block = f"| {pid} "
        line += block
        time_line += f"{format_number(s)} {unit}".ljust(len(block) + 3)

    time_line += f"{format_number(gantt[-1][2])} {unit}"
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
    EPS = 1e-9

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
            if arrival[p["pid"]] <= t + EPS and p["pid"] not in done
        ]

        if not available:
            t = min(p["arrival"] for p in procs if p["pid"] not in done)
            continue

        chosen = min(available, key=lambda x: (remaining[x], arrival[x], x))

        if current != chosen:
            if current is not None:
                gantt.append((current, start, t))
            current = chosen
            start = t

        future_arrivals = [
            p["arrival"]
            for p in procs
            if p["arrival"] > t + EPS and p["pid"] not in done
        ]

        next_arrival = min(future_arrivals) if future_arrivals else None

        if next_arrival is None:
            run_time = remaining[chosen]
        else:
            run_time = min(remaining[chosen], next_arrival - t)

        remaining[chosen] -= run_time
        t += run_time

        if remaining[chosen] <= EPS:
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
    EPS = 1e-9

    t = 0
    queue = []
    remaining = {p["pid"]: p["burst"] for p in procs}
    done = {}
    added = set()
    gantt = []

    while True:
        for p in sorted(procs, key=lambda x: (x["arrival"], x["pid"])):
            if p["arrival"] <= t + EPS and p["pid"] not in added and p["pid"] not in done:
                queue.append(p["pid"])
                added.add(p["pid"])

        if not queue:
            if len(done) == len(procs):
                break

            future_arrivals = [
                p["arrival"]
                for p in procs
                if p["pid"] not in done and p["pid"] not in added
            ]

            if future_arrivals:
                t = min(future_arrivals)
            else:
                break

            continue

        pid = queue.pop(0)

        run = min(q, remaining[pid])
        start = t
        t += run
        end = t

        remaining[pid] -= run
        gantt.append((pid, start, end))

        for p in sorted(procs, key=lambda x: (x["arrival"], x["pid"])):
            if start + EPS < p["arrival"] <= t + EPS and p["pid"] not in added and p["pid"] not in done:
                queue.append(p["pid"])
                added.add(p["pid"])

        if remaining[pid] > EPS:
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

    for i in range(len(processes)):
        for j in range(len(working)):
            if working[j] >= processes[i]:
                alloc[i] = j
                working[j] -= processes[i]
                break

    return alloc, working


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


def memory_result_table(blocks, processes, alloc, remaining, unit):
    headers = ["Process", f"Process Size ({unit})", "Allocated Block", "Status"]
    rows = []

    for i, size in enumerate(processes):
        if alloc[i] == -1:
            rows.append([f"P{i+1}", with_unit(size, unit), "-", "Not Allocated"])
        else:
            rows.append([f"P{i+1}", with_unit(size, unit), f"Block {alloc[i]+1}", "Allocated"])

    footer = f"Remaining Block Sizes ({unit}): " + ", ".join(
        f"Block {i+1} = {with_unit(remaining[i], unit)}"
        for i in range(len(remaining))
    )

    return format_table(headers, rows) + "\n\n" + footer


# ---------------- PAGE REPLACEMENT ----------------
def page_stats(faults, total_refs):
    hits = total_refs - faults
    hit_ratio = hits / total_refs if total_refs else 0
    miss_ratio = faults / total_refs if total_refs else 0
    return hits, hit_ratio, miss_ratio


def format_page_steps_table(steps, frame_count):
    headers = ["Step", "Page Reference", *[f"Frame {i+1}" for i in range(frame_count)], "Result"]
    rows = []

    for step in steps:
        frame_values = step["frames"] + ["-"] * (frame_count - len(step["frames"]))

        rows.append([
            step["step"],
            format_number(step["reference"]),
            *[format_number(x) for x in frame_values],
            step["result"],
        ])

    return format_table(headers, rows)


def fifo(refs, frame_count):
    frames = []
    faults = 0
    idx = 0
    steps = []

    for step_no, r in enumerate(refs, start=1):
        if r in frames:
            result = "Hit"
        else:
            result = "Page Fault"
            faults += 1

            if len(frames) < frame_count:
                frames.append(r)
            else:
                frames[idx] = r
                idx = (idx + 1) % frame_count

        steps.append({
            "step": step_no,
            "reference": r,
            "frames": frames.copy(),
            "result": result,
        })

    return {"faults": faults, "final_frames": frames.copy(), "steps": steps}


def optimal(refs, frame_count):
    frames = []
    faults = 0
    steps = []

    for i, r in enumerate(refs):
        if r in frames:
            result = "Hit"
        else:
            result = "Page Fault"
            faults += 1

            if len(frames) < frame_count:
                frames.append(r)
            else:
                future = refs[i + 1:]

                idx = max(
                    range(len(frames)),
                    key=lambda j: future.index(frames[j]) if frames[j] in future else 999999,
                )

                frames[idx] = r

        steps.append({
            "step": i + 1,
            "reference": r,
            "frames": frames.copy(),
            "result": result,
        })

    return {"faults": faults, "final_frames": frames.copy(), "steps": steps}


def lru(refs, frame_count):
    frames = []
    recent = {}
    faults = 0
    steps = []

    for i, r in enumerate(refs):
        if r in frames:
            result = "Hit"
        else:
            result = "Page Fault"
            faults += 1

            if len(frames) < frame_count:
                frames.append(r)
            else:
                lru_page = min(frames, key=lambda x: recent.get(x, -1))
                frames[frames.index(lru_page)] = r

        recent[r] = i

        steps.append({
            "step": i + 1,
            "reference": r,
            "frames": frames.copy(),
            "result": result,
        })

    return {"faults": faults, "final_frames": frames.copy(), "steps": steps}


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

    tk.Label(
        root,
        text="Time unit used in this page: milliseconds (ms)",
        font=("Arial", 10, "italic")
    ).pack()

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

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def build_process_inputs():
        for widget in entries_frame.winfo_children():
            widget.destroy()

        entries.clear()

        count = safe_int(num_entry.get())

        if count is None:
            show_custom_error(
                out,
                "Number of Processes must be a whole number only.\nExample: 3"
            )
            return

        if count <= 0:
            show_custom_error(out, "Number of Processes must be greater than 0.")
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

        out.delete("1.0", "end")

    ttk.Button(top_frame, text="Set Processes", command=build_process_inputs).grid(
        row=0, column=4, padx=8, pady=5
    )

    def run():
        procs = []

        if not entries:
            build_process_inputs()
            if not entries:
                return

        for pid, a, b in entries:
            pid_val = pid.get().strip() or f"P{len(procs)+1}"

            arr = safe_float(a.get())
            burst = safe_float(b.get())

            if arr is None:
                show_output_error(out, "Arrival Time (ms)", "0 or 2.5")
                return

            if burst is None:
                show_output_error(out, "Burst Time (ms)", "1 or 5.7")
                return

            if arr < 0 or burst <= 0:
                show_custom_error(
                    out,
                    "Arrival Time must be 0 ms or more, and Burst Time must be greater than 0 ms."
                )
                return

            procs.append({"pid": pid_val, "arrival": arr, "burst": burst})

        q = safe_float(q_entry.get())

        if q is None:
            show_output_error(out, "Time Quantum (ms)", "2 or 4.5")
            return

        if q <= 0:
            show_custom_error(out, "Time Quantum must be greater than 0 ms.")
            return

        algos = [
            ("FCFS", fcfs),
            ("SJF Non-Preemptive", sjf_non_preemptive),
            ("SJF Preemptive", sjf_preemptive),
            ("Round Robin", lambda x: round_robin(x, q)),
        ]

        out.delete("1.0", "end")
        out.insert("end", "CPU Scheduling Results\n")
        out.insert("end", "Time Unit: milliseconds (ms)\n")
        out.insert("end", f"Time Quantum: {with_unit(q, 'ms')}\n\n")

        for name, func in algos:
            res, gantt = func([dict(p) for p in procs])
            avg_wait, avg_tat = averages_from_results(res)

            out.insert("end", f"\n--- {name} ---\n")

            formatted_rows = []
            for row in res:
                formatted_rows.append([
                    row[0],
                    with_unit(row[1], "ms"),
                    with_unit(row[2], "ms"),
                    with_unit(row[3], "ms"),
                    with_unit(row[4], "ms"),
                ])

            out.insert(
                "end",
                format_table(
                    [
                        "PID",
                        "Arrival Time",
                        "Burst Time",
                        "Waiting Time",
                        "Turnaround Time"
                    ],
                    formatted_rows,
                )
                + "\n",
            )

            out.insert("end", f"\nAverage Waiting Time: {avg_wait:.2f} ms\n")
            out.insert("end", f"Average Turnaround Time: {avg_tat:.2f} ms\n")
            out.insert("end", "\nGantt Chart Time Unit: ms\n")
            out.insert("end", gantt_chart(gantt, "ms") + "\n")

    build_process_inputs()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    ttk.Button(button_frame, text="Run", command=run).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Back", command=main_menu).pack(side="left", padx=6)


# ---------------- MEMORY PAGE ----------------
def memory_page():
    clear()

    tk.Label(root, text="Contiguous Memory Allocation", font=("Arial", 22)).pack(pady=10)

    unit_frame = tk.Frame(root)
    unit_frame.pack(pady=5)

    tk.Label(unit_frame, text="Memory Size Unit:").pack(side="left", padx=5)

    unit_var = tk.StringVar(value="KB")
    unit_box = ttk.Combobox(
        unit_frame,
        textvariable=unit_var,
        values=["Bytes", "KB", "MB", "GB"],
        width=8,
        state="readonly"
    )
    unit_box.pack(side="left", padx=5)

    tk.Label(root, text="Memory Block Sizes (space-separated, using selected unit):").pack()

    block_entry = ttk.Entry(root, width=60)
    block_entry.insert(0, "100 500 200.5")
    block_entry.pack(pady=4)

    tk.Label(root, text="Process Memory Requests (space-separated, using selected unit):").pack()

    proc_entry = ttk.Entry(root, width=60)
    proc_entry.insert(0, "212 417.5 112")
    proc_entry.pack(pady=4)

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def run():
        unit = unit_var.get()

        blocks = safe_float_list(block_entry.get())
        procs = safe_float_list(proc_entry.get())

        if blocks is None:
            show_output_error(out, f"Memory Block Sizes ({unit})", f"100 500 200.5 {unit}")
            return

        if procs is None:
            show_output_error(out, f"Process Memory Requests ({unit})", f"212 417.5 112 {unit}")
            return

        if not blocks or not procs:
            show_custom_error(out, "Please enter at least one memory block and one process memory request.")
            return

        if any(b <= 0 for b in blocks) or any(p <= 0 for p in procs):
            show_custom_error(out, f"All block sizes and process memory requests must be greater than 0 {unit}.")
            return

        ff_alloc, ff_remaining = first_fit(blocks, procs)
        bf_alloc, bf_remaining = best_fit(blocks, procs)
        wf_alloc, wf_remaining = worst_fit(blocks, procs)

        out.delete("1.0", "end")

        out.insert("end", "Contiguous Memory Allocation Results\n")
        out.insert("end", f"Memory Unit: {unit}\n")
        out.insert("end", f"Memory Blocks: {', '.join(with_unit(x, unit) for x in blocks)}\n")
        out.insert("end", f"Process Requests: {', '.join(with_unit(x, unit) for x in procs)}\n\n")

        out.insert("end", "--- First Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, ff_alloc, ff_remaining, unit) + "\n\n")

        out.insert("end", "--- Best Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, bf_alloc, bf_remaining, unit) + "\n\n")

        out.insert("end", "--- Worst Fit ---\n")
        out.insert("end", memory_result_table(blocks, procs, wf_alloc, wf_remaining, unit) + "\n")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    ttk.Button(button_frame, text="Run", command=run).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Back", command=main_menu).pack(side="left", padx=6)


# ---------------- PAGE REPLACEMENT ----------------
def page_page():
    clear()

    tk.Label(root, text="Page Replacement", font=("Arial", 22)).pack(pady=10)

    tk.Label(
        root,
        text="Reference string values are page numbers. Frames are counted as frame slots, not time or memory units.",
        font=("Arial", 10, "italic")
    ).pack()

    tk.Label(root, text="Number of Frames (frame slots):").pack()

    f_entry = ttk.Entry(root, width=20)
    f_entry.insert(0, "3")
    f_entry.pack(pady=4)

    tk.Label(root, text="Reference String (page numbers, space-separated):").pack()

    ref_entry = ttk.Entry(root, width=60)
    ref_entry.insert(0, "7 0 1 2 0 3")
    ref_entry.pack(pady=4)

    out = scrolledtext.ScrolledText(root, height=24, width=120)
    out.pack(padx=10, pady=10, fill="both", expand=True)

    def run():
        f = safe_int(f_entry.get())

        if f is None:
            show_custom_error(
                out,
                "Number of Frames must be a whole number only.\nExample: 3 frames"
            )
            return

        if f <= 0:
            show_custom_error(out, "Number of Frames must be greater than 0 frames.")
            return

        refs = safe_int_list(ref_entry.get())

        if refs is None:
            show_output_error(out, "Reference String (page numbers)", "7 0 1 2 0 3")
            return

        if not refs:
            show_custom_error(out, "Reference string cannot be empty.")
            return

        if any(r < 0 for r in refs):
            show_custom_error(out, "Page numbers in the reference string must be 0 or greater.")
            return

        results = {
            "FIFO": fifo(refs, f),
            "Optimal": optimal(refs, f),
            "LRU": lru(refs, f),
        }

        out.delete("1.0", "end")
        out.insert("end", "Page Replacement Results\n")
        out.insert("end", "Unit Note: references are page numbers; frames are frame slots.\n")
        out.insert("end", f"Number of Frames: {f} frame(s)\n")
        out.insert("end", f"Reference String: {' '.join(str(format_number(x)) for x in refs)} page references\n\n")

        for algo_name, result in results.items():
            faults = result["faults"]
            hits, hit_ratio, miss_ratio = page_stats(faults, len(refs))
            final_frames = result["final_frames"]

            out.insert("end", f"--- {algo_name} ---\n")
            out.insert("end", "Step-by-Step Table:\n")
            out.insert("end", format_page_steps_table(result["steps"], f) + "\n\n")

            out.insert("end", f"Total Page References: {len(refs)} reference(s)\n")
            out.insert("end", f"Page Faults: {faults} fault(s)\n")
            out.insert("end", f"Hits: {hits} hit(s)\n")
            out.insert("end", f"Hit Ratio: {hit_ratio:.2f}\n")
            out.insert("end", f"Miss Ratio: {miss_ratio:.2f}\n")
            out.insert(
                "end",
                "Final Frame State: "
                + (" ".join(str(format_number(x)) for x in final_frames) if final_frames else "None")
                + " page number(s)\n\n",
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