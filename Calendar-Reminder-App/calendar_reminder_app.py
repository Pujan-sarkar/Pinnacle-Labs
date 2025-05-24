
import calendar
from tkinter import *
from tkinter import messagebox, ttk
import datetime
import json
import os
from tkcalendar import Calendar

REMINDER_FILE = "reminders.json"

def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as file:
            return json.load(file)
    return {}

def save_reminders():
    with open(REMINDER_FILE, "w") as file:
        json.dump(reminders, file, indent=4)

def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_valid_time(time_str):
    if not time_str:
        return True
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def on_date_select(event):
    date = cal.selection_get()
    date_str = date.strftime("%Y-%m-%d")
    date_entry.delete(0, END)
    date_entry.insert(0, date_str)
    show_reminder_for_date(date_str)
    if date_str in date_dropdown['values']:
        date_dropdown.set(date_str)

def on_dropdown_select(event):
    selected_date = date_dropdown.get()
    date_entry.delete(0, END)
    date_entry.insert(0, selected_date)
    cal.selection_set(datetime.datetime.strptime(selected_date, "%Y-%m-%d"))
    show_reminder_for_date(selected_date)

def show_reminder_for_date(date):
    if date in reminders:
        info = reminders[date]
        reminder_entry.delete("1.0", END)
        time_entry.delete(0, END)
        if isinstance(info, dict):
            reminder_entry.insert(INSERT, info.get("text", ""))
            time_entry.insert(0, info.get("time", ""))
            recurrence_var.set(info.get("recurrence", "None"))
        else:
            reminder_entry.insert(INSERT, str(info))
            recurrence_var.set("None")
    else:
        reminder_entry.delete("1.0", END)
        time_entry.delete(0, END)
        recurrence_var.set("None")

def set_reminder():
    date = date_entry.get()
    time = time_entry.get()
    reminder_text = reminder_entry.get("1.0", END).strip()
    recurrence = recurrence_var.get()

    if not date or not reminder_text:
        messagebox.showwarning("⚠️ Input Error", "Please enter a valid date and reminder.")
        return

    if not is_valid_date(date):
        messagebox.showwarning("⚠️ Input Error", "Invalid date format! Use YYYY-MM-DD.")
        return

    if not is_valid_time(time):
        messagebox.showwarning("⚠️ Input Error", "Invalid time format! Use HH:MM.")
        return

    reminders[date] = {
        "text": reminder_text,
        "time": time,
        "recurrence": recurrence
    }
    save_reminders()
    update_upcoming_reminders()
    update_dropdown_values()
    messagebox.showinfo("✅ Success", f"Reminder set for {date}")

def view_reminder():
    date = date_entry.get()
    if not date:
        messagebox.showwarning("⚠️ Input Error", "Please select or enter a date first.")
        return
    if not is_valid_date(date):
        messagebox.showwarning("⚠️ Input Error", "Invalid date format! Use YYYY-MM-DD.")
        return
    show_reminder_for_date(date)

def delete_reminder():
    date = date_entry.get()
    if not date:
        messagebox.showwarning("⚠️ Input Error", "Please select or enter a date first.")
        return
    if date in reminders:
        del reminders[date]
        save_reminders()
        update_upcoming_reminders()
        update_dropdown_values()
        reminder_entry.delete("1.0", END)
        time_entry.delete(0, END)
        recurrence_var.set("None")
        messagebox.showinfo("🗑 Deleted", f"Reminder for {date} deleted.")
    else:
        messagebox.showwarning("⚠️ Error", f"No reminder found for {date}.")

def clear_reminder():
    reminder_entry.delete("1.0", END)
    time_entry.delete(0, END)
    recurrence_var.set("None")
    date_entry.delete(0, END)

def update_upcoming_reminders():
    upcoming.delete(*upcoming.get_children())
    for date, info in sorted(reminders.items()):
        if isinstance(info, dict):
            time_val = info.get("time", "")
            recurrence_val = info.get("recurrence", "None")
            text_val = info.get("text", str(info))
        else:
            time_val = ""
            recurrence_val = "None"
            text_val = str(info)
        upcoming.insert("", "end", values=(date, time_val, recurrence_val, text_val[:40] + "..."))

def update_dropdown_values():
    values = sorted(reminders.keys())
    date_dropdown['values'] = values
    if not values:
        date_dropdown.set('')

def exit_app():
    root.quit()

style = ttk.Style()

LIGHT_THEME = {
    "bg": "#f0f4ff",
    "header_bg": "#3E64FF",
    "header_fg": "white",
    "frame_bg": "#f0f4ff",
    "cal_bg": "#3E64FF",
    "cal_fg": "white",
    "cal_select_bg": "#283593",
    "entry_bg": "white",
    "entry_fg": "black",
    "btn_bg": "#3E64FF",
    "btn_fg": "white",
    "tree_bg": "white",
    "tree_fg": "black",
    "select_bg": "#3E64FF",
    "select_fg": "white",
}

DARK_THEME = {
    "bg": "#2e2e2e",
    "header_bg": "#1a237e",
    "header_fg": "white",
    "frame_bg": "#2e2e2e",
    "cal_bg": "#3949ab",
    "cal_fg": "white",
    "cal_select_bg": "#283593",
    "entry_bg": "#4a4a4a",
    "entry_fg": "white",
    "btn_bg": "#3949ab",
    "btn_fg": "white",
    "tree_bg": "#3b3b3b",
    "tree_fg": "white",
    "select_bg": "#283593",
    "select_fg": "white",
}

current_theme = LIGHT_THEME

def apply_theme():
    theme = current_theme
    root.config(bg=theme["bg"])
    header.config(background=theme["header_bg"], foreground=theme["header_fg"])
    main_frame.config(bg=theme["frame_bg"])
    left_frame.config(bg=theme["frame_bg"])
    right_frame.config(bg=theme["frame_bg"])
    form_frame.config(bg=theme["frame_bg"])
    bottom_frame.config(bg=theme["frame_bg"])
    tree_frame.config(bg=theme["frame_bg"])
    btn_frame.config(bg=theme["frame_bg"])
    cal.config(background=theme["cal_bg"], foreground=theme["cal_fg"], selectbackground=theme["cal_select_bg"])
    date_entry.config(background=theme["entry_bg"], foreground=theme["entry_fg"], insertbackground=theme["entry_fg"])
    time_entry.config(background=theme["entry_bg"], foreground=theme["entry_fg"], insertbackground=theme["entry_fg"])
    reminder_entry.config(background=theme["entry_bg"], foreground=theme["entry_fg"], insertbackground=theme["entry_fg"])
    style.configure('TButton', background=theme["btn_bg"], foreground=theme["btn_fg"])
    style.map('TButton', background=[('active', theme["cal_select_bg"])])
    style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"], fieldbackground=theme["tree_bg"])
    style.map("Treeview", background=[('selected', theme["select_bg"])], foreground=[('selected', theme["select_fg"])])
    style.configure('TCombobox', fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"])

def toggle_theme():
    global current_theme
    if current_theme == LIGHT_THEME:
        current_theme = DARK_THEME
        theme_btn.config(text="☀️ Light Mode")
    else:
        current_theme = LIGHT_THEME
        theme_btn.config(text="🌙 Dark Mode")
    apply_theme()

root = Tk()
root.title("📅 Calendar Reminder App")
root.geometry("900x700")
root.config(bg="#f0f4ff")

reminders = load_reminders()
now = datetime.datetime.now()

header = Label(root, text="📆 Calendar Reminder App", font=("Segoe UI", 24, "bold"), bg="#3E64FF", fg="white", pady=15)
header.pack(fill=X)

main_frame = Frame(root, bg="#f0f4ff")
main_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

left_frame = Frame(main_frame, bg="#f0f4ff")
left_frame.pack(side=LEFT, padx=(0,10))

cal = Calendar(left_frame, selectmode='day', year=now.year, month=now.month, day=now.day, background='#3E64FF', foreground='white', selectbackground='#283593')
cal.pack()
cal.bind("<<CalendarSelected>>", on_date_select)

right_frame = Frame(main_frame, bg="#f0f4ff")
right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

form_frame = Frame(right_frame, bg="#f0f4ff")
form_frame.pack(pady=10, fill=X)

Label(form_frame, text="Selected Date (YYYY-MM-DD):", bg="#f0f4ff").grid(row=0, column=0, sticky=W)
date_entry = Entry(form_frame)
date_entry.grid(row=0, column=1, sticky=EW, pady=2, padx=2)

Label(form_frame, text="Time (HH:MM):", bg="#f0f4ff").grid(row=1, column=0, sticky=W)
time_entry = Entry(form_frame)
time_entry.grid(row=1, column=1, sticky=EW, pady=2, padx=2)

Label(form_frame, text="Reminder Text:", bg="#f0f4ff").grid(row=2, column=0, sticky=NW)
reminder_entry = Text(form_frame, width=40, height=5)
reminder_entry.grid(row=2, column=1, pady=2, padx=2)

Label(form_frame, text="Recurrence:", bg="#f0f4ff").grid(row=3, column=0, sticky=W, pady=2)
recurrence_var = StringVar(value="None")
recurrence_options = ["None", "Daily", "Weekly", "Monthly", "Yearly"]
recurrence_menu = ttk.Combobox(form_frame, textvariable=recurrence_var, values=recurrence_options, state="readonly")
recurrence_menu.grid(row=3, column=1, sticky=W, pady=2, padx=2)

form_frame.columnconfigure(1, weight=1)

date_dropdown_label = Label(right_frame, text="Select Existing Reminder Date:", bg="#f0f4ff")
date_dropdown_label.pack(anchor=W, pady=(10,0))

date_dropdown = ttk.Combobox(right_frame, values=sorted(reminders.keys()), state="readonly")
date_dropdown.pack(fill=X, pady=2)
date_dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)

btn_frame = Frame(right_frame, bg="#f0f4ff")
btn_frame.pack(pady=15, fill=X)

set_btn = ttk.Button(btn_frame, text="Set Reminder", command=set_reminder)
set_btn.pack(side=LEFT, padx=5, expand=True)

view_btn = ttk.Button(btn_frame, text="View Reminder", command=view_reminder)
view_btn.pack(side=LEFT, padx=5, expand=True)

delete_btn = ttk.Button(btn_frame, text="Delete Reminder", command=delete_reminder)
delete_btn.pack(side=LEFT, padx=5, expand=True)

clear_btn = ttk.Button(btn_frame, text="Clear Form", command=clear_reminder)
clear_btn.pack(side=LEFT, padx=5, expand=True)

theme_btn = ttk.Button(right_frame, text="🌙 Dark Mode", command=toggle_theme)
theme_btn.pack(pady=5)

bottom_frame = Frame(root, bg="#f0f4ff")
bottom_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

tree_frame = Frame(bottom_frame, bg="#f0f4ff")
tree_frame.pack(fill=BOTH, expand=True)

columns = ("Date", "Time", "Recurrence", "Reminder")
upcoming = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    upcoming.heading(col, text=col)
    upcoming.column(col, anchor=W)
upcoming.pack(fill=BOTH, expand=True)

apply_theme()
update_upcoming_reminders()
update_dropdown_values()

root.mainloop()
