import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:5000/api/items"

# ===== WEB STYLE THEME (MATCHES YOUR index.html) =====
BG_SIDEBAR = "#0f172a"
BG_MAIN    = "#020617"
CARD_BG    = "#0b1220"

TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED   = "#94a3b8"

ACCENT       = "#f59e0b"
ACCENT_HOVER = "#fbbf24"
DANGER       = "#ef4444"

ENTRY_BG     = "#020617"
ENTRY_BORDER = "#1e293b"


class PageTurnApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LegendaryOneApex - MyLibrary")
        self.geometry("1100x680")
        self.configure(bg=BG_MAIN)

        style = ttk.Style()
        style.theme_use("clam")

        # ===== FRAME STYLES =====
        style.configure("Sidebar.TFrame", background=BG_SIDEBAR)
        style.configure("Main.TFrame", background=BG_MAIN)
        style.configure("Card.TFrame", background=CARD_BG)

        # ===== TEXT STYLES =====
        style.configure("Sidebar.TLabel",
            background=BG_SIDEBAR, foreground=TEXT_PRIMARY, font=("Inter", 10)
        )
        style.configure("Title.TLabel",
            background=BG_SIDEBAR, foreground=ACCENT, font=("Inter", 24, "bold")
        )
        style.configure("Header.TLabel",
            background=BG_SIDEBAR, foreground=TEXT_MUTED, font=("Inter", 10, "bold")
        )

        # ===== BUTTONS =====
        style.configure("Gold.TButton",
            background=ACCENT, foreground="#000000", font=("Inter", 10, "bold"), borderwidth=0
        )
        style.map("Gold.TButton", background=[("active", ACCENT_HOVER)])

        style.configure("Gray.TButton",
            background="#1e293b", foreground=TEXT_PRIMARY, borderwidth=0
        )
        style.map("Gray.TButton", background=[("active", "#334155")])

        style.configure("Danger.TButton",
            background=DANGER, foreground="white", font=("Inter", 10, "bold"), borderwidth=0
        )
        style.map("Danger.TButton", background=[("active", "#f87171")])

        # ===== TABLE =====
        style.configure("Treeview",
            background=CARD_BG, fieldbackground=CARD_BG, foreground=TEXT_PRIMARY,
            rowheight=32, borderwidth=0, font=("Inter", 10)
        )
        style.configure("Treeview.Heading",
            background="#020617", foreground=ACCENT, font=("Inter", 10, "bold")
        )
        style.map("Treeview",
            background=[("selected", "#1e293b")],
            foreground=[("selected", ACCENT)]
        )

        self.create_layout()
        self.load_data()


    def create_layout(self):
        # ===== SIDEBAR =====
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=320)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="LegendaryOneApex", style="Title.TLabel").pack(pady=(35, 4), padx=25, anchor="w")
        ttk.Label(sidebar, text="Bookstore & Media Manager", style="Sidebar.TLabel").pack(pady=(0, 30), padx=25, anchor="w")

        ttk.Label(sidebar, text="ADD NEW ITEM", style="Header.TLabel").pack(padx=25, pady=(0, 15), anchor="w")

        # INPUTS
        self.create_input(sidebar, "Title")
        self.entry_title = self.modern_entry(sidebar)

        self.create_input(sidebar, "Creator")
        self.entry_creator = self.modern_entry(sidebar)

        self.create_input(sidebar, "Category")
        self.combo_cat = ttk.Combobox(
            sidebar, values=["Book", "Film", "Magazine"], state="readonly", font=("Inter", 10)
        )
        self.combo_cat.current(0)
        self.combo_cat.pack(fill="x", padx=25, pady=(0, 15), ipady=5)

        self.create_input(sidebar, "Year")
        self.entry_year = self.modern_entry(sidebar)

        ttk.Button(sidebar, text="ADD TO LIBRARY", style="Gold.TButton",
                   command=self.add_item).pack(fill="x", padx=25, ipady=12)


        # ===== MAIN AREA =====
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        card = ttk.Frame(main, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        # SEARCH BAR
        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", padx=20, pady=20)

        self.entry_search = tk.Entry(
            top, bg=ENTRY_BG, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", font=("Inter", 11), highlightthickness=1,
            highlightbackground=ENTRY_BORDER
        )
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry_search.insert(0, "Search title...")

        ttk.Button(top, text="SEARCH", style="Gray.TButton",
                   command=self.search).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="REFRESH", style="Gray.TButton",
                   command=self.load_data).pack(side="left")
        ttk.Button(top, text="DELETE", style="Danger.TButton",
                   command=self.delete_item).pack(side="right")

        # TABLE
        table_frame = ttk.Frame(card, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols = ("ID", "Title", "Creator", "Category", "Year")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, anchor="center")

        self.tree.column("ID", width=50)
        self.tree.column("Title", width=280, anchor="w")
        self.tree.column("Creator", width=200, anchor="w")
        self.tree.column("Category", width=100)
        self.tree.column("Year", width=80)

        sc = ttk.Scrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")


    # ===== HELPERS =====
    def modern_entry(self, parent):
        e = tk.Entry(
            parent, bg=ENTRY_BG, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", font=("Inter", 11), highlightthickness=1,
            highlightbackground=ENTRY_BORDER
        )
        e.pack(fill="x", padx=25, pady=(0, 15), ipady=8)
        return e

    def create_input(self, parent, text):
        ttk.Label(parent, text=text.upper(), style="Sidebar.TLabel").pack(
            anchor="w", padx=25, pady=(0, 5)
        )

    # ===== LOGIC (UNCHANGED) =====
    def load_data(self):
        try:
            self.populate(requests.get(API_URL).json())
        except:
            messagebox.showerror("Error", "Is backend.py running?")

    def populate(self, items):
        self.tree.delete(*self.tree.get_children())
        for idx, i in enumerate(items, 1):
            self.tree.insert("", "end", iid=i['id'],
                             values=(idx, i['title'], i['creator'], i['category'], i.get('year', '')))

    def add_item(self):
        if not self.entry_title.get():
            return messagebox.showwarning("Required", "Title is missing!")

        data = {
            "title": self.entry_title.get(),
            "creator": self.entry_creator.get(),
            "category": self.combo_cat.get(),
            "year": self.entry_year.get()
        }
        requests.post(API_URL, json=data)
        self.load_data()

        self.entry_title.delete(0, 'end')
        self.entry_creator.delete(0, 'end')
        self.entry_year.delete(0, 'end')

    def search(self):
        q = self.entry_search.get()
        if q and q.lower() != "search title...":
            self.populate(requests.get(API_URL, params={"q": q}).json())

    def delete_item(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete this item?"):
            requests.delete(f"{API_URL}/{sel[0]}")
            self.load_data()


if __name__ == "__main__":
    PageTurnApp().mainloop()
