import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:5000/api/items"

# --- MIDNIGHT & GOLD THEME ---
BG_SIDEBAR = "#130f40"    # Deep Midnight Blue
BG_MAIN = "#f5f6fa"       # Very Light Grey
TEXT_SIDEBAR = "#dff9fb"  # Ice White
TEXT_MAIN = "#2d3436"     # Dark Grey
ACCENT_COLOR = "#f0932b"  # Vibrant Orange/Gold
ACCENT_HOVER = "#ffbe76"  # Lighter Orange
DANGER_COLOR = "#eb4d4b"  # Soft Red

class PageTurnApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MyLibrary | Media Manager")
        self.geometry("1050x650")
        self.configure(bg=BG_MAIN)
        
        # --- STYLES ---
        style = ttk.Style()
        style.theme_use("clam")
        
        # Frames
        style.configure("Sidebar.TFrame", background=BG_SIDEBAR)
        style.configure("Main.TFrame", background=BG_MAIN)
        
        # Labels
        style.configure("Sidebar.TLabel", background=BG_SIDEBAR, foreground=TEXT_SIDEBAR, font=("Helvetica", 10))
        style.configure("Title.TLabel", background=BG_SIDEBAR, foreground=ACCENT_COLOR, font=("Helvetica", 26, "bold"))
        style.configure("Header.TLabel", background=BG_SIDEBAR, foreground="#95afc0", font=("Helvetica", 11, "bold"))
        
        # Buttons (Gold Theme)
        style.configure("Gold.TButton", background=ACCENT_COLOR, foreground="#130f40", font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("Gold.TButton", background=[("active", ACCENT_HOVER)])
        
        style.configure("Search.TButton", background="#95afc0", foreground="#130f40", borderwidth=0)
        style.map("Search.TButton", background=[("active", "#c7ecee")])

        style.configure("Danger.TButton", background=DANGER_COLOR, foreground="white", font=("Helvetica", 9, "bold"), borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#ff7979")])

        # Treeview (Table) l
        style.configure("Treeview", 
                        background="white", 
                        fieldbackground="white", 
                        foreground=TEXT_MAIN, 
                        rowheight=35, 
                        font=("Helvetica", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background="#dcdde1", 
                        foreground="#2f3640", 
                        font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", "#130f40")], foreground=[("selected", ACCENT_COLOR)])

        self.create_layout()
        self.load_data()

    def create_layout(self):
        # --- LEFT SIDEBAR (Inputs) ---
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=320)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Branding
        ttk.Label(sidebar, text="Legendary01", style="Title.TLabel").pack(pady=(40, 5), padx=25, anchor="w")
        ttk.Label(sidebar, text="Bookstore Inventory System", style="Sidebar.TLabel").pack(pady=(0, 40), padx=25, anchor="w")

        # Form
        ttk.Label(sidebar, text="NEW ENTRY", style="Header.TLabel").pack(padx=25, pady=(0, 15), anchor="w")

        self.create_input(sidebar, "Title")
        self.entry_title = tk.Entry(sidebar, bg="#30336b", fg="white", insertbackground="white", relief="flat", font=("Helvetica", 11))
        self.entry_title.pack(fill="x", padx=25, pady=(0, 15), ipady=8)

        self.create_input(sidebar, "Creator (Author/Director)")
        self.entry_creator = tk.Entry(sidebar, bg="#30336b", fg="white", insertbackground="white", relief="flat", font=("Helvetica", 11))
        self.entry_creator.pack(fill="x", padx=25, pady=(0, 15), ipady=8)

        self.create_input(sidebar, "Category")
        self.combo_cat = ttk.Combobox(sidebar, values=["Book", "Film", "Magazine"], state="readonly", font=("Helvetica", 10))
        self.combo_cat.current(0)
        self.combo_cat.pack(fill="x", padx=25, pady=(0, 15), ipady=4)

        self.create_input(sidebar, "Year")
        self.entry_year = tk.Entry(sidebar, bg="#30336b", fg="white", insertbackground="white", relief="flat", font=("Helvetica", 11))
        self.entry_year.pack(fill="x", padx=25, pady=(0, 30), ipady=8)

        # Main Action Button
        ttk.Button(sidebar, text="ADD TO LIBRARY", style="Gold.TButton", command=self.add_item).pack(fill="x", padx=25, ipady=10)

        # --- RIGHT MAIN AREA (List) ---
        main_area = ttk.Frame(self, style="Main.TFrame")
        main_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        # Top Control Bar
        top_bar = ttk.Frame(main_area, style="Main.TFrame")
        top_bar.pack(fill="x", pady=(0, 20))

        self.entry_search = tk.Entry(top_bar, bg="white", fg=TEXT_MAIN, relief="flat", font=("Helvetica", 11), highlightthickness=1, highlightbackground="#dcdde1")
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry_search.insert(0, "Search by title...")
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.delete(0, "end"))

        ttk.Button(top_bar, text="SEARCH", style="Search.TButton", width=10, command=self.search).pack(side="left", padx=(0, 5))
        ttk.Button(top_bar, text="REFRESH", style="Search.TButton", width=10, command=self.load_data).pack(side="left")
        
        # Delete Button (Right aligned)
        ttk.Button(top_bar, text="DELETE SELECTED", style="Danger.TButton", command=self.delete_item).pack(side="right")

        # The Table
        cols = ("ID", "Title", "Creator", "Category", "Year")
        self.tree = ttk.Treeview(main_area, columns=cols, show="headings", selectmode="browse")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("ID", text="#")
        self.tree.column("Title", width=300, anchor="w")
        self.tree.heading("Title", text="TITLE")
        self.tree.column("Creator", width=200, anchor="w")
        self.tree.heading("Creator", text="CREATOR")
        self.tree.column("Category", width=100, anchor="center")
        self.tree.heading("Category", text="CATEGORY")
        self.tree.column("Year", width=80, anchor="center")
        self.tree.heading("Year", text="YEAR")

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_area, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def create_input(self, parent, text):
        ttk.Label(parent, text=text.upper(), style="Sidebar.TLabel", font=("Helvetica", 8, "bold"), foreground="#95afc0").pack(anchor="w", padx=25, pady=(0, 5))

    # --- LOGIC ---
    def load_data(self):
        try:
            self.populate(requests.get(API_URL).json())
        except:
            messagebox.showerror("Error", "Is backend.py running?")

    def populate(self, items):
        self.tree.delete(*self.tree.get_children())
        for idx, i in enumerate(items, 1):
            self.tree.insert("", "end", iid=i['id'], values=(idx, i['title'], i['creator'], i['category'], i.get('year', '')))

    def add_item(self):
        title = self.entry_title.get()
        if not title: return messagebox.showwarning("Required", "Title is missing!")
        
        data = {
            "title": title,
            "creator": self.entry_creator.get(),
            "category": self.combo_cat.get(),
            "year": self.entry_year.get()
        }
        requests.post(API_URL, json=data)
        self.load_data()
        
        # Clear inputs
        self.entry_title.delete(0, 'end')
        self.entry_creator.delete(0, 'end')
        self.entry_year.delete(0, 'end')

    def search(self):
        q = self.entry_search.get()
        if q and q != "Search by title...":
            self.populate(requests.get(API_URL, params={"q": q}).json())

    def delete_item(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete this item permanently?"):
            requests.delete(f"{API_URL}/{sel[0]}")
            self.load_data()

if __name__ == "__main__":
    app = PageTurnApp()
    app.mainloop()