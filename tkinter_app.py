from tkinter import *
from tkinter import filedialog
from watermark import watermark
from tkinter.ttk import Progressbar
import os

sentinel = object()

class App(Tk):

    def __init__(self):
        
        Tk.__init__(self)

        self.set_generals()

        self.set_btn_frame()

        self.set_list_frame()
        
        self.set_checkbox()

    #region Setting

    def set_generals(self):

        #---title--
        self.title('Watermark AIM')

        #---icon---
        self.iconbitmap(r'Logo_aim-drive.ico')

        #---geometry---
        self.width = int(self.winfo_screenwidth()/2)
        self.height = int(self.winfo_screenheight()/2)
        self.minsize(self.width, self.height)
        self.geometry(f'{self.width}x{self.height}')

    def set_btn_frame(self):

        #---button frame---
        self.btn_frame = Frame(self)
        self.btn_frame.pack(
            padx=10,
            pady=5,
            fill='x',
            side='bottom'
        )

        #---add file(s) button---
        self.add_btn = Button(
            self.btn_frame,
            text='Aggiungi uno o più file',
            command= self.select_pdf,
            font=('Helvetica', '15'),
            bg='green'
        )
        self.add_btn.pack(
            ipadx=10,
            ipady=10,
            fill='both',
            expand=True,
            side=RIGHT
        )

        #---watermark selected files button---
        self.modify_btn = Button(
            self.btn_frame,
            text='Applica Watermark',
            font=('Helvetica', '15'),
            command=self.modify
        )
        self.modify_btn.pack(
            ipadx=10,
            ipady=10,
            fill='both',
            expand=True,
            side=LEFT
        )

    def set_list_frame(self):

        self.files = {}

        #--- view frame ---
        self.view_frame = Frame(self)
        self.view_frame.pack(
            padx=10,
            pady=10,
            fill='both',
            expand=True,
            side='top'
        )

        #scroll bar
        self.sb = Scrollbar(
            self.view_frame,
            orient=VERTICAL
        )

        self.sb.pack(
            side=RIGHT,
            fill=Y
        )

        #listbox
        self.listbox = Listbox(
            self.view_frame,
            font=('Helvetica', '15'),
            selectmode=EXTENDED
        )

        self.listbox.pack(
            side=LEFT,
            fill='both',
            expand=True
        )

        #scrollbar config
        self.listbox.configure(yscrollcommand=self.sb.set)
        self.sb.config(command=self.listbox.yview)

        def context_menu(event, menu):
            widget = event.widget
            index = widget.nearest(event.y)
            _, yoffset, _, height = widget.bbox(index)
            if event.y > height + yoffset + 5:
                # Outside of widget.
                return
            item = widget.get(index)
            menu.post(event.x_root, event.y_root)


        aqua = self.tk.call('tk', 'windowingsystem') == 'aqua'

        self.menu = Menu(
            tearoff=0
        )

        self.menu.add_command(
            label=u'Elimina',
            command=self.delete_selected_items
        )

        self.listbox.bind('<2>' if aqua else '<3>', lambda e: context_menu(e, self.menu))

    def set_checkbox(self):

        self.overwrite = IntVar()

        self.check_frame = Frame(self)
        self.check_frame.pack(
            padx=5,
            fill='x',
            side='bottom'
        )
        #salva/sovrascrivi
        self.check = Checkbutton(
            self.check_frame,
            text='Sovrascrivi i file',
            variable=self.overwrite,
            onvalue=1,
            offvalue=0
        )
        self.check.pack(
            side=LEFT
        )

    def set_popup(self):

        self.popup = Toplevel()
        width = int(self.winfo_width()/3)
        height = int(self.winfo_height()/3)
        self.popup.geometry(f'{width}x{height}')

        Label(self.popup, text="Modifico il file").pack()

        n= len(self.files)
        self.pb_val = DoubleVar()
        self.pb_text = StringVar()

        self.file_label = Label(self.popup, textvariable=self.pb_text).pack()

        self.pb = Progressbar(
            self.popup,
            orient='horizontal',
            variable = self.pb_val,
            maximum = n
        )
        self.pb.pack(padx=10, pady=20)

        self.popup.pack_slaves()

    #endregion
    #----------
    #region Funzioni

    def refresh_list(self):

        self.listbox.delete(0, END)
        for item in self.files.values():
            self.listbox.insert(END, item)

    def select_pdf(self):
        new_files = filedialog.askopenfilenames(
            title='Seleziona i file da modificare...',
            filetypes=[('PDF', '*.pdf')],
        )
        new_files = {file: file.split('/')[-1] for file in new_files}
        self.files.update(new_files)
        self.refresh_list()

    def delete_selected_items(self):

        selected_items = self.listbox.curselection()
        for item in selected_items[::-1]:
            val = self.listbox.get(item)
            self.files = {key: value for key, value in self.files.items() if value != val}
            self.listbox.delete(item)

    def modify(self):

        over = self.overwrite.get()
        dir = None
        path = None

        if not over:
            dir = filedialog.askdirectory(
                title='Seleziona la cartella in cui salvare i file...'
            )

        if dir and not os.path.isdir(dir+'/Watermarked'):
            os.mkdir(dir+'/Watermarked')

        self.modify_btn.config(state = 'disabled')

        self.set_popup()
        files = list(self.files.keys())

        for file in files[::-1]:

            #aggiorno la progress bar
            self.update_pb(file)
            #metto il watermark
            watermark(file,over,dir)
            #elimino dalla list box e dalla lista
            self.delete(file)
            

        self.modify_btn.config(state = 'active')

    def update_pb(self,file):

        #aggiorno pb
        progress = self.pb_val.get()+1
        self.pb_val.set(progress)

        #aggiorno label
        text = file.split('/')[-1]
        self.pb_text.set(text)

        self.popup.update()

        
    
    def delete(self,file):

        self.listbox.delete(END)
        del self.files[file]

    #endregion
    



if __name__=='__main__':
    #main loop
    app = App()
    app.mainloop()

















