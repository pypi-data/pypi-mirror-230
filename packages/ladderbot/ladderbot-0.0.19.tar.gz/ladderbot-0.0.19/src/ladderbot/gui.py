import pkgutil
import importlib.resources
import json
from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar
from ladderbot.html_creator import make_game_html

def show_gui():
    logo_icon = pkgutil.get_data('ladderbot', 'Logo.ico')
    root = Tk()
    root.geometry("230x200")
    root.title("LadderBot")
    root.iconbitmap(logo_icon)
    uname_label = Label(root, text="Username:")
    uname_label.pack()
    uname_entry = Entry(root)
    uname_entry.pack()
    uid_label = Label(root, text="UID:")
    uid_label.pack()
    uid_entry = Entry(root)
    uid_entry.pack()
    hash_label = Label(root, text="Hash:")
    hash_label.pack()
    hash_entry = Entry(root, show="*")
    hash_entry.pack()
    remember_var = IntVar()
    remember_checkbox = Checkbutton(root, text="Remember", variable=remember_var)
    remember_checkbox.pack()
    load_values(uname_entry, uid_entry, hash_entry, remember_checkbox)
    submit_button = Button(root, text="Submit", command=lambda: submit_creds(uname_entry, uid_entry, hash_entry, remember_var, root))
    submit_button.pack()
    root.mainloop()
#-----------------------------------------------
def submit_creds(uname_entry, uid_entry, hash_entry, remember_var, root):
    username = uname_entry.get()
    uid = uid_entry.get()
    hash = hash_entry.get()
    if remember_var.get():
        save_values(username, uid, hash)
    make_game_html(username, uid, hash)
    root.destroy()
#-----------------------------------------------
def save_values(uname, uid, hash):
    data = {
        'uname': uname,
        'uid': uid,
        'hash': hash
    }
    with open(str(importlib.resources.files("ladderbot")) + "\\creds.json", "w") as file:
        json.dump(data, file)
#-----------------------------------------------
def load_values(uname_entry, uid_entry, hash_entry, remember_checkbox):
    with open(str(importlib.resources.files("ladderbot")) + "\\creds.json") as file:
        data = json.load(file)
    try:
        uname_entry.delete(0, 'end')
        uname_entry.insert('end', data['uname'])
        uid_entry.delete(0, 'end')
        uid_entry.insert('end', data['uid'])
        hash_entry.delete(0, 'end')
        hash_entry.insert('end', data['hash'])
        remember_checkbox.select()
    except FileNotFoundError:
        print("No saved values found")
        #-----------------------------------------------