import tkinter as tk
from tkinter import filedialog, ttk, Menu, messagebox
from PIL import Image, ImageTk
from datetime import datetime
from ultralytics import YOLO
import cv2

# Default credentials
DEFAULT_USER = "aaa"
DEFAULT_PASS = "0000"

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("350x220")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill='both')
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, pady=5)
        self.user_entry = ttk.Entry(frame)
        self.user_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, pady=5)
        self.pw_entry = ttk.Entry(frame, show="*")
        self.pw_entry.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Login", command=self.check_login).grid(row=2, column=0, columnspan=2, pady=15)

    def check_login(self):
        if (self.user_entry.get().strip() == DEFAULT_USER and
            self.pw_entry.get().strip() == DEFAULT_PASS):
            self.destroy()
            DetectionApp().mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

class DetectionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Defect Detection System")
        self.geometry("1100x600")
        self.configure(bg="#f0f0f0")

        # Model init
        self.model = YOLO("/Users/jensen/Desktop/python_final/runs/detect/train3/weights/best.pt")
        self.filepath = None
        self.original_pil = None
        self.processed_images = []

        # Styles
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Arial",18,"bold"), background="#004080", foreground="white")
        style.configure("TButton", font=("Arial",11), padding=5)
        style.configure("Info.TLabel", font=("Arial",12), background="#f0f0f0", foreground="#004080")

        # Menu
        menubar = Menu(self)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

        # Header
        header = ttk.Label(self, text="Defect Detection System", style="Header.TLabel", anchor="center")
        header.pack(fill="x", pady=(0,5))

        # Main frame with 3 columns: image, gallery, sidebar
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=1)

        # Image display
        img_frame = ttk.Frame(main, borderwidth=2, relief="ridge")
        img_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        self.img_label = ttk.Label(img_frame)
        self.img_label.pack(expand=True)

        # Gallery panel (hidden initially)
        self.gallery_visible = False
        self.gallery_frame = ttk.Frame(main, borderwidth=2, relief="ridge")
        self.gallery_refs = []

        # Sidebar
        side = ttk.Frame(main)
        side.grid(row=0, column=2, sticky="nsew")

        # Toggle gallery button
        self.btn_toggle = ttk.Button(side, text="Show Gallery", command=self.toggle_gallery)
        self.btn_toggle.pack(fill="x", pady=4)

        # Action buttons
        for txt, cmd in [("Upload BMP", self.upload_and_display),
                         ("Detect", self.start_detection),
                         ("Reset", self.reset_detection),
                         ("Clear All", self.clear_all)]:
            ttk.Button(side, text=txt, command=cmd).pack(fill="x", pady=4)

        # Results tree
        ttk.Label(side, text="Detection Results", style="Info.TLabel").pack(pady=(10,0))
        cols=("Class","Conf","Level")
        self.tree=ttk.Treeview(side,columns=cols,show="headings",height=5)
        for c in cols:
            self.tree.heading(c,text=c)
            self.tree.column(c,width=80,anchor="center")
        self.tree.pack(fill="x",pady=5)

        # Info label: Time, Location, Temperature
        ttk.Separator(side,orient='horizontal').pack(fill='x',pady=5)
        self.time_var=tk.StringVar()
        self.loc_var=tk.StringVar()
        self.temp_var=tk.StringVar()
        ttk.Label(side,textvariable=self.time_var,style="Info.TLabel").pack(anchor='w',padx=5)
        ttk.Label(side,textvariable=self.loc_var,style="Info.TLabel").pack(anchor='w',padx=5)
        ttk.Label(side,textvariable=self.temp_var,style="Info.TLabel").pack(anchor='w',padx=5)
        self.update_time()

    def toggle_gallery(self):
        if not self.gallery_visible:
            self.gallery_frame.grid(row=0, column=1, sticky="nsew", padx=5)
            self.update_gallery()
            self.btn_toggle.config(text="Hide Gallery")
        else:
            self.gallery_frame.grid_forget()
            self.btn_toggle.config(text="Show Gallery")
        self.gallery_visible = not self.gallery_visible

    def update_gallery(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.gallery_refs.clear()
        for idx, img in enumerate(self.processed_images):
            thumb = img.resize((100,80))
            tp = ImageTk.PhotoImage(thumb)
            lbl = ttk.Label(self.gallery_frame, image=tp)
            lbl.image = tp
            lbl.pack(pady=5)
            self.gallery_refs.append(tp)

    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set("Time: " + now)
        self.loc_var.set("Location: 逢甲大學")
        self.temp_var.set("Temperature: 25°C")
        self.after(1000,self.update_time)

    def upload_and_display(self):
        fp=filedialog.askopenfilename(filetypes=[("BMP Files","*.bmp")])
        if not fp: return
        self.filepath=fp
        pil=Image.open(fp)
        self.original_pil=pil.copy()
        disp=pil.resize((500,400))
        self.photo=ImageTk.PhotoImage(disp)
        self.img_label.config(image=self.photo)

    def start_detection(self):
        if not self.filepath:
            messagebox.showwarning("Warning","Upload BMP first")
            return
        res=self.model(self.filepath)[0]
        img=res.orig_img.copy()
        self.tree.delete(*self.tree.get_children())
        # Gather boxes with area
        boxes=[]
        areas=[]
        classes=[]
        confs=[]
        for box,cls,conf in zip(res.boxes.xyxy,res.boxes.cls,res.boxes.conf):
            x1,y1,x2,y2=map(int,box.tolist())
            area=(x2-x1)*(y2-y1)
            boxes.append((x1,y1,x2,y2))
            areas.append(area)
            classes.append(int(cls))
            confs.append(float(conf))
        # Sort by area descending
        idxs=sorted(range(len(boxes)), key=lambda i: areas[i], reverse=True)
        selected=[]
        for i in idxs:
            x1,y1,x2,y2=boxes[i]
            keep=True
            for (sx1,sy1,sx2,sy2) in selected:
                xx1=max(x1,sx1); yy1=max(y1,sy1)
                xx2=min(x2,sx2); yy2=min(y2,sy2)
                w=max(0,xx2-xx1); h=max(0,yy2-yy1)
                inter=w*h
                if inter>0:
                    keep=False
                    break
            if keep:
                selected.append((x1,y1,x2,y2))
                name=res.names[classes[i]]
                level="Crit" if areas[i]>10000 else "Med" if areas[i]>3000 else "Min"
                self.tree.insert('', 'end', values=(name,f"{confs[i]:.2f}",level))
                col=(0,0,255) if level=="Crit" else (0,255,255) if level=="Med" else (0,255,0)
                cv2.rectangle(img,(x1,y1),(x2,y2),col,2)
        pil2=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        self.processed_images.append(pil2)
        disp=pil2.resize((500,400))
        self.photo=ImageTk.PhotoImage(disp)
        self.img_label.config(image=self.photo)
        if self.gallery_visible:
            self.update_gallery()

    def reset_detection(self):
        if not self.original_pil:
            messagebox.showwarning("Warning","No image to reset.")
            return
        img=self.original_pil.resize((500,400))
        self.photo=ImageTk.PhotoImage(img)
        self.img_label.config(image=self.photo)
        self.tree.delete(*self.tree.get_children())

    def clear_all(self,thumbnail_only=False):
        self.tree.delete(*self.tree.get_children())
        if not thumbnail_only:
            self.processed_images.clear()
            self.filepath=None
            self.original_pil=None
            self.img_label.config(image='')
            self.gallery_frame.grid_forget()
            self.gallery_visible=False
            self.btn_toggle.config(text="Show Gallery")

    # Stubs
    def export_csv(self): messagebox.showinfo("Info","Not implemented.")
    def export_report(self): messagebox.showinfo("Info","Not implemented.")
    def camera_settings(self): messagebox.showinfo("Info","Not implemented.")
    def calibration_wizard(self): messagebox.showinfo("Info","Not implemented.")
    def user_logout(self):
        self.destroy()
        LoginWindow().mainloop()

if __name__=='__main__':
    LoginWindow().mainloop()