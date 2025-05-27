from datetime import datetime
import pandas as pd
import os

master_csv_file = "./data/task_logs.csv"

def collect_input():
    flags ={
        "completed_done": False,
        "pending_done": False,
        "notes_done": False
    }
    
    completed_tasks = []
    pending_tasks = []
    notes = []

    task_categories = ["completed", "pending", "notes"]

    task_lists = {
        "completed": completed_tasks,
        "pending": pending_tasks,
        "notes": notes
    }

    global today 
    today = datetime.today().strftime("%b %d, %Y")
    print(f"Let's create your task report for {today}\n\n(Enter \"quit\" to exit)")
    for category in task_categories:
        while flags[f"{category}_done"] != True:
            prompt = f"\nEnter {category} task: " if category != 'notes' else "\nEnter notes: "
            task_input = input(prompt).strip()
            if task_input.lower() == "quit":
                flags[f"{category}_done"] = True
            elif task_input != "":
                task_lists[category].append(task_input)
            else: 
                continue
    
        category_label = f"{category} tasks" if category != 'notes' else "notes"
        print(f"Your {category_label}: {', '.join(task_lists[category]) if task_lists[category] else 'None'}")
    return task_lists

def transform_input(input):
    task_items = {
                "date": [],
                "task_type": [],
                "task_description": []
            }
    for k, v in input.items():
        for task in v:
            task_items["date"].append(today)
            task_items["task_type"].append(k)
            task_items["task_description"].append(task)
    
    df = pd.DataFrame(task_items)
    return df

def check_existing_entry(filepath, date_str):
    if not os.path.exists(filepath):
        return False
    
    df = pd.read_csv(filepath)
    return date_str in df["date"].values

def prompt_user_choice(date_str):
    print(f"\nYou already have task entries for {date_str}.")
    print("[A] Append new tasks to existing entries")
    print("[O] Overwrite today's entries completely")
    print("[C] Cancel and exit")
    
    valid_choices = {"a", "o", "c"}
    while True:
        choice = input("Choose an option (A/O/C): ").strip().lower()
        if choice in valid_choices:
            return choice
        else:
            print("Invalid input. Please enter A, O, or C.")


def write_to_csv(df, filepath=master_csv_file, overwrite=False):
    folder = os.path.dirname(filepath)
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        if overwrite:
            filtered_df = existing_df[existing_df["date"] != df["date"].iloc[0]]
            combined_df = pd.concat([filtered_df, df], ignore_index=True)
            combined_df.to_csv(filepath, index=False)
            return "Today's entries were overwritten successfully."
        else:
            df.to_csv(filepath, mode="a", index=False, header=False)
            return "New tasks appended to today's existing entry."
    else:
        df.to_csv(filepath, mode="w", index=False)
        return "New log created."

def write_text_report(filepath, date_str):
    df = pd.read_csv(filepath)
    today_df = df[df["date"] == today]
    
    report_lines = [f"Daily Report - {today}"]

    def write_section(title, task_type):
        tasks = today_df[today_df['task_type'] == task_type]['task_description'].tolist()
        if tasks:
            section = [f"\n{title}:"]
            section += [f"- {task}" for task in tasks]
            return section
        return []
    
    report_lines += write_section("Completed Tasks", "completed")
    report_lines += write_section("Pending Tasks", "pending")
    report_lines += write_section("Notes", "notes")
    
    folder = "./reports"
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    report_filename = os.path.join(folder, f"Task_Report_{date_str.replace(',', '').replace(' ', '_')}.txt")

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

    return f"Text report saved to {report_filename}"

            
if __name__ == "__main__":
    user_input  = collect_input()
    task_items = transform_input(input=user_input)
    if check_existing_entry(master_csv_file, today):
        choice = prompt_user_choice(today)

        if choice == "c":
            print("Cancelled. No data was written.")
        elif choice == "o":
            result = write_to_csv(df=task_items, filepath=master_csv_file, overwrite=True)
            print(result)
            print(write_text_report(filepath=master_csv_file, date_str=today))
        elif choice == "a":
            result = write_to_csv(df=task_items, filepath=master_csv_file, overwrite=False)
            print(result)
            print(write_text_report(filepath=master_csv_file, date_str=today))
    else:
        result = write_to_csv(df=task_items, filepath=master_csv_file)
        print(result)
        print(write_text_report(filepath=master_csv_file, date_str=today))
    