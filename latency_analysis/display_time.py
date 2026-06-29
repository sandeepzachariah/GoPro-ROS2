import tkinter as tk
from datetime import datetime

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')
root.bind('<Escape>', lambda _: root.destroy())

label = tk.Label(
    root,
    text='',
    font=('DejaVu Sans Mono', 120, 'bold'),
    fg='white',
    bg='black'
)
label.pack(expand=True)

def update():
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S.') + f'{now.microsecond // 1000:03d}'
    label.config(text=time_str)
    root.after(10, update)  # reschedule every 10ms

update()
root.mainloop()
