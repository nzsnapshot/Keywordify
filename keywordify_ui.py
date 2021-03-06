import tkinter as tk
import tkinter.font as font
from keyboard_listener import KeyboardListener, KeyWord
from replace_functions import replace, eval_replace, exec_replace
import json
import os
import threading
from pynput.keyboard import Key, Controller
import copy

### Threading ###

stop_event = threading.Event()
keyboard = Controller()

### Functions ###

def start_thread(target):
    stop_event.clear()
    thread = threading.Thread(target=target)
    thread.start()
    return thread
    
def get_font(family='Helvetica', size=14, weight='normal'):
    return font.Font(family=family, size=size, weight=weight)

def create_keywords_json():
    filename = 'keywords.json'
    with open(filename, 'a') as file:
        if os.path.getsize(filename) == 0:
            json.dump({}, file)

def update_keyword_json(new_keyword_text, new_value_text):
    filename = 'keywords.json'
    with open(filename) as file:
        keywords = json.load(file)

    keywords[new_keyword_text] = new_value_text
    with open(filename, 'w') as file:
        json.dump(keywords, file)

def convert_keywords_to_KeyWord_Objects():
    with open('keywords.json', 'r') as file:
        keywords = json.load(file)
    keyword_objects = {}
    for keyword, value in keywords.items():
        # Instead of executing the replacement as soon as the input is entered, it is executed after the input + enter is pressed
        if value[1] == "text":
            keyword_objects[keyword] = KeyWord(keyword + 'enter', replace, keyword + '\n', value[0])
        elif value[1] == "function":
            keyword_objects[keyword] = KeyWord(keyword + 'enter', exec_replace, keyword + '\n', value[0])
    return keyword_objects

def add_keyword_and_value():
    global keywords
    global keyboard_listener
    new_keyword_text = new_keyword.get()
    new_value_text = new_value.get("1.0", tk.END)
    new_value_type = value_type_variable.get()
    # Remove newline that the text box randomly adds to the end of the string
    new_value_text = new_value_text[:-1]
    if not new_keyword_text:
        add_confirmation_label.config(text='Please Enter Keyword', fg='red')
        return
    if not new_value_text:
        add_confirmation_label.config(text='Please Enter Value', fg='red')
        return
    new_value_text = [new_value_text, new_value_type]
    keyboard_listener.recent_input = []
    update_keyword_json(new_keyword_text, new_value_text)
    add_confirmation_label.config(text='Keyword Added', fg='green')
    keywords = convert_keywords_to_KeyWord_Objects()
    keyboard_listener.keywords = keywords
    update_current_keywords_frame()
    return keyboard_listener

def start_keyboard_listener():
    keyboard_listener = KeyboardListener(keywords=keywords)
    keyboard_listener_thread = start_thread(target=keyboard_listener.run)
    return keyboard_listener

def toggle_frame(frame, **kwargs):
    if frame.visible == True:
        frame.grid_forget()
        frame.visible = False
        toggle_frame_btn.config(text='Show Frame')
    elif frame.visible == False:
        frame.grid(kwargs)
        frame.visible = True
        toggle_frame_btn.config(text='Hide Frame')

def text_radio_command():
    new_value.config(bg='white', fg='black', insertbackground='black')
    print(value_type_variable.get())

def function_radio_command():
    new_value.config(bg='#202020', fg='white', insertbackground='white')
    print(value_type_variable.get())

def update_current_keywords_frame():
    # Clears the frame
    current_keywords_frame.delete(0,tk.END)
    # Updates frame
    with open('keywords.json') as file:
        current_keywords = json.load(file)
    for current_keyword, value in current_keywords.items():
        if value[1] == "function":
            current_keywords_frame.insert(tk.END, current_keyword)
        elif value[1] == "text":
            current_keywords_frame.insert(tk.END, current_keyword)

def edit_keyword():
    try:
        keyword = current_keywords_frame.get(current_keywords_frame.curselection())
    except:
        add_confirmation_label.config(text='Please select keyword to edit', fg='red')
        return
    with open('keywords.json') as file:
        current_keywords = json.load(file)
    value = current_keywords[keyword][0]
    value_type = current_keywords[keyword][1]
    new_keyword.delete(0,tk.END)
    new_keyword.insert(0,keyword)
    new_value.delete("1.0",tk.END)
    new_value.insert("1.0",value)
    if value_type == 'text':
        text_radio_command()
        value_type_text_radio.select()
    elif value_type == 'function':
        function_radio_command()
        value_type_function_radio.select()

def delete_keyword():
    try:
        keyword = current_keywords_frame.get(current_keywords_frame.curselection())
    except:
        add_confirmation_label.config(text='Please select keyword to delete', fg='red')
        return
    filename = 'keywords.json'
    with open(filename) as file:
        keywords = json.load(file)

    del keywords[keyword]

    with open(filename, 'w') as file:
        json.dump(keywords, file)

    update_current_keywords_frame()
    add_confirmation_label.config(text='Keyword successfully deleted', fg='green')

### Setup ###

root = tk.Tk()

root.title("Keywordify")
# root.wm_attributes("-topmost", 1)

# Create keywords.json if it doesn't already exist
create_keywords_json()

keywords = convert_keywords_to_KeyWord_Objects()

print(keywords)

### Variables ###

value_type_variable = tk.StringVar()

### Styles ###

header_font = get_font('Arial', 16, 'bold')
text_font = get_font('Arial', 18)
button_font = get_font('Arial', 16)
alert_font = get_font('Arial', 11, 'bold')

### Frames ###

left_frame = tk.Frame(root, height=200, width=200)

right_frame = tk.Frame(root, height=200, width=300)

current_keywords_container_frame = tk.Frame(root, height=200, width=200)
current_keywords_container_frame.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

current_keywords_label = tk.Label(current_keywords_container_frame, text='Current Keywords', font=header_font)
current_keywords_label.grid(row=0,column=0)

current_keywords_frame = tk.Listbox(current_keywords_container_frame, font=text_font, selectmode=tk.SINGLE, height=15)
current_keywords_frame.grid(row=1,column=0, pady=10)

recent_keywords_scrollbar = tk.Scrollbar(current_keywords_container_frame, orient="vertical")
recent_keywords_scrollbar.config(command = current_keywords_frame.yview)
recent_keywords_scrollbar.grid(row=1,column=1, sticky='nsew')

current_keywords_frame.config(yscrollcommand = recent_keywords_scrollbar.set)

current_keywords_config_frame = tk.Frame(current_keywords_container_frame)
current_keywords_config_frame.grid(row=2,column=0)

edit_current_keywords_btn = tk.Button(current_keywords_config_frame, text='Edit', font=text_font, command=edit_keyword)
edit_current_keywords_btn.pack(side='left', padx=5)

delete_current_keywords_btn = tk.Button(current_keywords_config_frame, text='Delete', font=text_font, command=delete_keyword, bg='red', fg='white')
delete_current_keywords_btn.pack(side='right', padx=5)


### Labels ###

new_keyword_label = tk.Label(left_frame, text='New Keyword', font=header_font)
new_value_label = tk.Label(right_frame, text='New Keyword Value', font=header_font)
add_confirmation_label = tk.Label(left_frame, text='', font=alert_font, fg='green')
value_type_label = tk.Label(left_frame, text='Choose Value Type', font=header_font)

### Inputs ###

new_keyword = tk.Entry(left_frame, font=text_font)
new_value = tk.Text(right_frame, font=text_font, width=30, height=17)

### Buttons ###

create_keyword_btn = tk.Button(left_frame, text='Create', font=button_font, command=add_keyword_and_value, bg='green', fg='white')
toggle_frame_btn = tk.Button(left_frame, text='Hide Right Frame', font=button_font, command= lambda: toggle_frame(right_frame, row=0, column=1, padx=5, pady=5))

value_type_text_radio = tk.Radiobutton(left_frame, text='Text', variable=value_type_variable, value='text', font=text_font, indicatoron=0, command=text_radio_command)
value_type_function_radio = tk.Radiobutton(left_frame, text='Function', variable=value_type_variable, value='function', font=text_font, indicatoron=0, command=function_radio_command)


### Layout ###

left_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

new_keyword_label.grid(row=1, column=0)
new_keyword.grid(row=2, column=0, pady=(10,0))

value_type_label.grid(row=3, column=0, pady=(10,0), sticky='nsew')
value_type_text_radio.grid(row=4, column=0, pady=(10,0), sticky='nsew')
value_type_text_radio.select()
value_type_function_radio.grid(row=5, column=0, sticky='nsew')
value_type_function_radio.deselect()

create_keyword_btn.grid(row=6,column=0, pady=(10,0), sticky='nsew')

add_confirmation_label.grid(row=7, column=0, pady=(20,0))


right_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

new_value_label.grid(row=0, column=0, sticky='n')
new_value.grid(row=1, column=0, pady=(10,0), sticky='n')

update_current_keywords_frame()

### Run Loop ###

keyboard_listener = start_keyboard_listener()

root.mainloop()
