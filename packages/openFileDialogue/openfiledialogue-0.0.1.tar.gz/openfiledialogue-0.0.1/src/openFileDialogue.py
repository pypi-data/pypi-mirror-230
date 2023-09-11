from tkinter import *
from tkinter import messagebox
import platform, os

def openfile(types = ["*"]):
    def update_files():
        try:
            all = os.listdir(path.get())
            files = [f for f in all if os.path.isfile(os.path.join(path.get(), f)) if f.split(".")[-1] in types or types == ["*"]]
            dirs = [d for d in all if os.path.isdir(os.path.join(path.get(), d))]
            files.sort()
            dirs.sort()
            files_box.delete(0, END)
            files_box.insert("end", "D: ..")
            for dir in dirs:
                files_box.insert("end", "D: " + dir)
            for file in files:
                files_box.insert("end", "F: " + file)
            return 0
        except:
            messagebox.showerror(title=None, message="Access Denied")
            return -1

    def double_select(*args):
        nonlocal double
        double = True
        current_selected = files_box.selection_get()
        if current_selected[:3] == "D: ":
            old_path = path.get()
            if current_selected[3:] == "..":
                path.set(sep.join(path.get().split(sep)[:-2]) + sep)
            else:
                path.set(path.get() + current_selected[3:] + sep)
            if update_files():
                path.set(old_path)

        elif current_selected[:3] == "F: ":
            selected.set(current_selected[3:])
            tk.destroy()
        double = False

    def single_select(*args):
        nonlocal double
        if not double:
            current_selected = files_box.selection_get()
            if current_selected[:3] == "F: ":
                selected.set(current_selected[3:])

    def button_select(*args):
        if selected.get() != "":
            tk.destroy()

    tk = Tk()
    title = "Select File ("
    for file_type in types:
        title += "." + file_type + ", "
    title = title[:-2] + ")"
    tk.title(title)
    tk.geometry("502x290")
    tk.resizable(0, 0)

    system = platform.system()
    selected = StringVar()
    path = StringVar()
    double = False

    if system == "Windows":
        path.set("C:\\Users\\" + os.getlogin() + "\\")
        sep = "\\"
    elif system == "Linux":
        path.set("/home/" + os.getlogin() + "/")
        sep = "/"
    else:
        print("Nope")
        return -1

    path_box = Label(tk, textvariable=path, borderwidth=2, relief="sunken", anchor="w")
    files_box = Listbox(tk, borderwidth=2)
    selected_box = Label(tk,textvariable=selected, borderwidth=2, relief="sunken", anchor="w")
    okay_button = Button(tk, text="Select", command=button_select)

    if system == "Linux":
        path_box.configure(width=62)
        files_box.configure(width=62, height=13)
        selected_box.configure(width=53)
        okay_button.configure(font=(None, 8))

    elif system == "Windows":
        path_box.configure(width=71)
        files_box.configure(width=83, height=15)
        selected_box.configure(width=65)
        okay_button.configure(font=(None, 7))

    path_box.grid(row=0, column=0, columnspan=2)
    files_box.bind("<Double-1>", double_select)
    files_box.bind("<<ListboxSelect>>", single_select)
    files_box.grid(row=1, column=0, columnspan=2)
    selected_box.grid(row=2, column=0)
    okay_button.grid(row=2, column=1)

    update_files()

    files_box.focus_force()
    tk.mainloop()
    if selected.get() != "":
        return os.path.join(path.get(), selected.get())

print(openfile(types=["jpeg", "txt"]))