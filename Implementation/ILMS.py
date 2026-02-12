
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import hashlib

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1200x750")
        self.root.minsize(900, 650)
        
        # --- MODERN THEME COLORS ---
        self.bg_main = '#0f1419'           # Deep dark navy
        self.bg_secondary = '#1a1f2e'      # Slightly lighter navy
        self.bg_tertiary = '#252d3d'       # Card background
        self.fg_text = '#e8eaed'           # Light gray text
        self.fg_muted = '#9ca3af'          # Muted gray
        self.accent_primary = '#00d9ff'    # Cyan blue
        self.accent_secondary = '#6366f1'  # Indigo
        self.accent_tertiary = '#10b981'   # Emerald
        self.accent_danger = '#ef4444'     # Red for logout
        
        self.root.configure(bg=self.bg_main)
        self.apply_styles()
        
        self.db_name = 'library.db'
        self.conn = None
        self.cursor = None
        self.logged_in_user = None
        
        self.init_database()
        self.show_login_screen()
        
    def apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Backgrounds
        style.configure("TFrame", background=self.bg_main)
        style.configure("TLabel", background=self.bg_main, foreground=self.fg_text, font=("Segoe UI", 10))
        
        # Secondary Frames
        style.configure("TLabelframe", background=self.bg_tertiary, foreground=self.fg_text, relief="flat", borderwidth=2)
        style.configure("TLabelframe.Label", background=self.bg_tertiary, foreground=self.accent_primary, 
                       font=("Segoe UI", 11, "bold"))
        
        # Primary Buttons (Accent color)
        style.configure("Accent.TButton", padding=12, relief="flat", background=self.accent_primary, 
                       foreground=self.bg_main, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[('active', self.accent_secondary), ('pressed', self.accent_secondary)])
        
        # Secondary Buttons (Subtle style)
        style.configure("Secondary.TButton", padding=10, relief="flat", background=self.bg_tertiary, 
                       foreground=self.fg_text, font=("Segoe UI", 10))
        style.map("Secondary.TButton", background=[('active', self.bg_secondary)])
        
        # Danger Button (for logout)
        style.configure("Danger.TButton", padding=8, relief="flat", background=self.accent_danger, 
                       foreground=self.fg_text, font=("Segoe UI", 9, "bold"))
        style.map("Danger.TButton", background=[('active', '#dc2626')])
        
        # Card-style Button
        style.configure("Card.TButton", padding=20, relief="flat", background=self.bg_tertiary, 
                       foreground=self.fg_text, font=("Segoe UI", 11, "bold"))
        style.map("Card.TButton", background=[('active', self.bg_secondary)])
        
        # Tables
        style.configure("Treeview", background=self.bg_tertiary, foreground=self.fg_text, 
                       fieldbackground=self.bg_tertiary, bordercolor=self.bg_secondary, rowheight=30)
        style.configure("Treeview.Heading", background=self.bg_secondary, foreground=self.accent_primary, 
                       font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', self.accent_secondary)])
        
        # Entry
        style.configure("TEntry", fieldbackground=self.bg_tertiary, foreground=self.fg_text, 
                       font=("Segoe UI", 10), borderwidth=1, relief="solid")

    def init_database(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS librarians (librarian_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL, email TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS books (book_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, isbn TEXT UNIQUE NOT NULL, publisher TEXT, publication_year INTEGER, total_copies INTEGER DEFAULT 1, available_copies INTEGER DEFAULT 1, category TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS members (member_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT, phone TEXT, address TEXT, membership_date TEXT NOT NULL, status TEXT DEFAULT "active")')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER NOT NULL, book_id INTEGER NOT NULL, borrow_date TEXT NOT NULL, due_date TEXT NOT NULL, return_date TEXT, fine_amount REAL DEFAULT 0, status TEXT DEFAULT "borrowed", FOREIGN KEY(member_id) REFERENCES members(member_id), FOREIGN KEY(book_id) REFERENCES books(book_id))')
        self.conn.commit()
    
    def format_id(self, id_number, prefix="", digits=4):
        """Format ID with leading zeros (e.g., 0001, 0067)"""
        return f"{prefix}{str(id_number).zfill(digits)}"
    
    def format_member_id(self, member_id):
        """Format member ID with 'mem' prefix (e.g., mem001, mem042)"""
        return f"mem{str(member_id).zfill(3)}"

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_sub_window(self, title, size="900x650"):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(size)
        win.configure(bg=self.bg_main)
        main = ttk.Frame(win, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        return win, main

    # --- NAVIGATION SCREENS ---
    def show_login_screen(self):
        self.clear_screen()
        frame = ttk.Frame(self.root, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(frame, text="ILMS", font=("Segoe UI", 36, "bold"), foreground=self.accent_primary).pack(pady=10)
        ttk.Label(frame, text="Integrated Library Management System", font=("Segoe UI", 11), foreground=self.fg_muted).pack(pady=(0, 30))
        
        ttk.Label(frame, text="Username", font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 2))
        u_entry = ttk.Entry(frame, width=40)
        u_entry.pack(pady=(0, 15))
        
        ttk.Label(frame, text="Password", font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 2))
        p_entry = ttk.Entry(frame, width=40, show="*")
        p_entry.pack(pady=(0, 25))
        
        def login():
            self.cursor.execute('SELECT librarian_id, username FROM librarians WHERE username=? AND password_hash=?', 
                               (u_entry.get(), self.hash_password(p_entry.get())))
            result = self.cursor.fetchone()
            if result:
                self.logged_in_user = result[1]
                self.show_main_menu()
            else:
                messagebox.showerror("Access Denied", "Invalid Credentials")

        ttk.Button(frame, text="LOGIN", command=login, style="Accent.TButton").pack(pady=10, fill=tk.X, ipady=8)
        ttk.Button(frame, text="CREATE ACCOUNT", command=self.show_register_screen, style="Secondary.TButton").pack(fill=tk.X, ipady=6)

    def show_register_screen(self):
        self.clear_screen()
        frame = ttk.Frame(self.root, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(frame, text="Create New Account", font=("Segoe UI", 24, "bold"), foreground=self.accent_primary).pack(pady=20)
        
        fields = ["Username", "Password", "Full Name"]
        ents = {}
        for f in fields:
            ttk.Label(frame, text=f, font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 2))
            e = ttk.Entry(frame, width=40, show="*" if f == "Password" else "")
            e.pack(pady=(0, 15))
            ents[f] = e

        def reg():
            try:
                self.cursor.execute('INSERT INTO librarians (username, password_hash, name) VALUES (?,?,?)',
                                   (ents["Username"].get(), self.hash_password(ents["Password"].get()), ents["Full Name"].get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                self.show_login_screen()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")

        ttk.Button(frame, text="CREATE ACCOUNT", command=reg, style="Accent.TButton").pack(pady=15, fill=tk.X, ipady=8)
        ttk.Button(frame, text="BACK", command=self.show_login_screen, style="Secondary.TButton").pack(fill=tk.X, ipady=6)

    def show_main_menu(self):
        self.clear_screen()
        
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Top bar with header and logout
        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        # Header section (left)
        header_frame = ttk.Frame(top_bar)
        header_frame.pack(side=tk.LEFT)
        
        ttk.Label(header_frame, text="Library Management", font=("Segoe UI", 28, "bold"), 
                 foreground=self.accent_primary).pack(anchor="w")
        welcome_text = f"Welcome, {self.logged_in_user}" if self.logged_in_user else "Dashboard"
        ttk.Label(header_frame, text=welcome_text, font=("Segoe UI", 11), 
                 foreground=self.fg_muted).pack(anchor="w")
        
        # Logout button (right corner)
        logout_frame = ttk.Frame(top_bar)
        logout_frame.pack(side=tk.RIGHT)
        
        logout_btn = ttk.Button(logout_frame, text="🚪 Logout", command=self.logout, 
                               style="Danger.TButton")
        logout_btn.pack(padx=5)
        
        # Main content area
        content = ttk.Frame(container)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Search section at top
        search_section = ttk.LabelFrame(content, text="📚 Search Library", padding="20")
        search_section.pack(fill=tk.X, pady=(0, 20))
        
        search_inner = ttk.Frame(search_section)
        search_inner.pack(fill=tk.X)
        
        ttk.Label(search_inner, text="Search by:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        search_combo = ttk.Combobox(search_inner, values=["Title", "Author", "ISBN"], 
                                    state="readonly", width=12)
        search_combo.set("Title")
        search_combo.pack(side=tk.LEFT, padx=5)
        
        search_entry = ttk.Entry(search_inner, width=50)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(search_inner, text="🔍 SEARCH", 
                  command=lambda: self.search_book_window(search_combo.get(), search_entry.get()), 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        # Grid for main menu cards
        cards_frame = ttk.Frame(content)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        
        # Menu cards with icons and descriptions
        menu_items = [
            {
                "title": "📖 Book Management",
                "desc": "Add, update & remove books",
                "icon": "📖",
                "command": self.show_book_menu,
                "color": self.accent_primary
            },
            {
                "title": "👥 Member Management", 
                "desc": "Register & manage members",
                "icon": "👥",
                "command": self.show_member_menu,
                "color": self.accent_secondary
            },
            {
                "title": "🔄 Transactions",
                "desc": "Issue & return books",
                "icon": "🔄",
                "command": self.show_transaction_menu,
                "color": self.accent_tertiary
            }
        ]
        
        for idx, item in enumerate(menu_items):
            self.create_menu_card(cards_frame, item, row=0, col=idx)
    
    def create_menu_card(self, parent, item, row, col):
        """Create a professional card-style button"""
        card = tk.Frame(parent, bg=self.bg_tertiary, relief="flat", bd=0)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Add hover effect
        def on_enter(e):
            card.config(bg=self.bg_secondary)
        
        def on_leave(e):
            card.config(bg=self.bg_tertiary)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e: item["command"]())
        
        # Icon
        icon_label = tk.Label(card, text=item["icon"], font=("Segoe UI", 48), 
                             bg=self.bg_tertiary, fg=item["color"])
        icon_label.pack(pady=(40, 15))
        icon_label.bind("<Button-1>", lambda e: item["command"]())
        
        # Title
        title_label = tk.Label(card, text=item["title"].replace(item["icon"] + " ", ""), 
                              font=("Segoe UI", 16, "bold"), 
                              bg=self.bg_tertiary, fg=self.fg_text)
        title_label.pack(pady=(0, 8))
        title_label.bind("<Button-1>", lambda e: item["command"]())
        
        # Description
        desc_label = tk.Label(card, text=item["desc"], font=("Segoe UI", 9), 
                             bg=self.bg_tertiary, fg=self.fg_muted)
        desc_label.pack(pady=(0, 40))
        desc_label.bind("<Button-1>", lambda e: item["command"]())
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logged_in_user = None
            self.show_login_screen()

    # --- BOOK MANAGEMENT ---
    def show_book_menu(self):
        self.clear_screen()
        
        # Header with back button
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Label(header, text="📖 Book Management", font=("Segoe UI", 24, "bold"), 
                 foreground=self.accent_primary).pack(side=tk.LEFT)
        
        ttk.Button(header, text="← Back to Dashboard", command=self.show_main_menu, 
                  style="Secondary.TButton").pack(side=tk.RIGHT)
        
        # Menu options
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Create cards in a grid
        cards_frame = ttk.Frame(content)
        cards_frame.pack(expand=True)
        
        options = [
            ("➕ Add New Book", "Add books to library", self.add_book_window),
            ("✏️ Update Book", "Modify book details", self.update_book_window),
            ("🗑️ Remove Book", "Delete books from system", self.remove_book_window),
            ("📚 View All Books", "Browse complete inventory", self.view_all_books_window)
        ]
        
        for idx, (title, desc, cmd) in enumerate(options):
            row = idx // 2
            col = idx % 2
            
            btn_frame = ttk.Frame(cards_frame)
            btn_frame.grid(row=row, column=col, padx=20, pady=20, sticky="ew")
            
            btn = tk.Frame(btn_frame, bg=self.bg_tertiary, relief="flat", height=120, width=300)
            btn.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            btn.pack_propagate(False)
            
            # Hover effects
            def make_hover(widget, command):
                def on_enter(e):
                    widget.config(bg=self.bg_secondary)
                def on_leave(e):
                    widget.config(bg=self.bg_tertiary)
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", lambda e: command())
                return widget
            
            btn = make_hover(btn, cmd)
            
            # Center the content vertically
            content_frame = tk.Frame(btn, bg=self.bg_tertiary)
            content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(content_frame, text=title, font=("Segoe UI", 14, "bold"), 
                    bg=self.bg_tertiary, fg=self.fg_text).pack(pady=(0, 5))
            tk.Label(content_frame, text=desc, font=("Segoe UI", 9), 
                    bg=self.bg_tertiary, fg=self.fg_muted).pack()

    def add_book_window(self):
        win, main = self.setup_sub_window("Add New Book", "600x600")
        
        ttk.Label(main, text="➕ Add New Book", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_primary).pack(pady=(0, 20))
        
        group = ttk.LabelFrame(main, text="Book Information", padding="20")
        group.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Title", "title"), 
            ("Author", "author"), 
            ("ISBN", "isbn"), 
            ("Publisher", "publisher"),
            ("Publication Year", "year"),
            ("Category", "category"),
            ("Total Copies", "copies")
        ]
        
        ents = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(group, text=label, font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=10, padx=(0, 10))
            e = ttk.Entry(group, width=40)
            e.grid(row=i, column=1, sticky="ew", pady=10)
            ents[key] = e
        
        group.columnconfigure(1, weight=1)

        def save():
            try:
                year = int(ents["year"].get()) if ents["year"].get() else None
                copies = int(ents["copies"].get()) if ents["copies"].get() else 1
                
                self.cursor.execute('''INSERT INTO books 
                    (title, author, isbn, publisher, publication_year, category, total_copies, available_copies) 
                    VALUES (?,?,?,?,?,?,?,?)''',
                    (ents["title"].get(), ents["author"].get(), ents["isbn"].get(), 
                     ents["publisher"].get(), year, ents["category"].get(), copies, copies))
                self.conn.commit()
                book_id = self.cursor.lastrowid
                formatted_id = self.format_id(book_id)
                messagebox.showinfo("Success", f"Book added successfully!\nBook ID: {formatted_id}")
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "ISBN already exists!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for year and copies!")

        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="ADD BOOK", command=save, style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)

    def update_book_window(self):
        win, main = self.setup_sub_window("Update Book", "900x650")
        
        ttk.Label(main, text="✏️ Update Book Details", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_primary).pack(pady=(0, 20))
        
        # Search section
        search_frame = ttk.LabelFrame(main, text="Find Book", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Book ID:").pack(side=tk.LEFT, padx=5)
        id_entry = ttk.Entry(search_frame, width=15)
        id_entry.pack(side=tk.LEFT, padx=5)
        
        # Update form
        form_frame = ttk.LabelFrame(main, text="Book Information", padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("Title", "title"), 
            ("Author", "author"), 
            ("ISBN", "isbn"),
            ("Publisher", "publisher"),
            ("Publication Year", "year"),
            ("Category", "category"),
            ("Total Copies", "copies")
        ]
        
        ents = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))
            e = ttk.Entry(form_frame, width=40)
            e.grid(row=i, column=1, sticky="ew", pady=8)
            ents[key] = e
        
        form_frame.columnconfigure(1, weight=1)
        
        def parse_id(id_str):
            """Extract numeric ID from formatted or plain ID"""
            return int(id_str.lstrip('0')) if id_str.strip() else 0
        
        def load_book():
            try:
                book_id = parse_id(id_entry.get())
                self.cursor.execute('SELECT title, author, isbn, publisher, publication_year, category, total_copies FROM books WHERE book_id=?', (book_id,))
                result = self.cursor.fetchone()
                if result:
                    ents["title"].delete(0, tk.END)
                    ents["title"].insert(0, result[0])
                    ents["author"].delete(0, tk.END)
                    ents["author"].insert(0, result[1])
                    ents["isbn"].delete(0, tk.END)
                    ents["isbn"].insert(0, result[2])
                    ents["publisher"].delete(0, tk.END)
                    ents["publisher"].insert(0, result[3] or "")
                    ents["year"].delete(0, tk.END)
                    ents["year"].insert(0, result[4] or "")
                    ents["category"].delete(0, tk.END)
                    ents["category"].insert(0, result[5] or "")
                    ents["copies"].delete(0, tk.END)
                    ents["copies"].insert(0, result[6])
                else:
                    messagebox.showerror("Error", "Book not found!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid book ID!")
        
        def update():
            try:
                book_id = parse_id(id_entry.get())
                year = int(ents["year"].get()) if ents["year"].get() else None
                copies = int(ents["copies"].get())
                
                self.cursor.execute('''UPDATE books SET 
                    title=?, author=?, isbn=?, publisher=?, publication_year=?, category=?, total_copies=?
                    WHERE book_id=?''',
                    (ents["title"].get(), ents["author"].get(), ents["isbn"].get(),
                     ents["publisher"].get(), year, ents["category"].get(), copies, book_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Book updated successfully!")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(search_frame, text="LOAD", command=load_book, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="UPDATE BOOK", command=update, style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)

    def remove_book_window(self):
        win, main = self.setup_sub_window("Remove Book", "900x650")
        
        ttk.Label(main, text="🗑️ Remove Book", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_danger).pack(pady=(0, 20))
        
        # Search and display books
        search_frame = ttk.LabelFrame(main, text="Search Books", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("ID", "Title", "Author", "ISBN", "Copies")
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=15)
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        def search():
            tree.delete(*tree.get_children())
            query = f'%{search_entry.get()}%'
            self.cursor.execute('SELECT book_id, title, author, isbn, total_copies FROM books WHERE title LIKE ? OR author LIKE ?', (query, query))
            for r in self.cursor.fetchall():
                formatted_id = self.format_id(r[0])
                tree.insert("", tk.END, values=(formatted_id,) + r[1:], tags=(r[0],))
        
        def remove():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a book to remove!")
                return
            
            # Get actual book_id from tags
            book_id = tree.item(selected[0])['tags'][0]
            book_title = tree.item(selected[0])['values'][1]
            
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{book_title}'?"):
                try:
                    self.cursor.execute('DELETE FROM books WHERE book_id=?', (book_id,))
                    self.conn.commit()
                    messagebox.showinfo("Success", "Book removed successfully!")
                    search()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Cannot delete book with active transactions!")
        
        ttk.Button(search_frame, text="🔍 SEARCH", command=search, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="REMOVE SELECTED", command=remove, style="Danger.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        
        search()

    def search_book_window(self, search_by="title", search_term=""):
        win, main = self.setup_sub_window("Search Library", "1000x700")
        
        ttk.Label(main, text="🔍 Library Search", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_primary).pack(pady=(0, 20))
        
        # Search controls
        sf = ttk.LabelFrame(main, text="Search Filters", padding="10")
        sf.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sf, text="Search by:").pack(side=tk.LEFT, padx=5)
        combo = ttk.Combobox(sf, values=["title", "author", "isbn", "category"], state="readonly", width=15)
        combo.set(search_by)
        combo.pack(side=tk.LEFT, padx=5)
        
        entry = ttk.Entry(sf, width=40)
        entry.insert(0, search_term)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Results table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("ID", "Title", "Author", "ISBN", "Publisher", "Year", "Category", "Available/Total")
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=20)
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        def run_search():
            tree.delete(*tree.get_children())
            search_field = combo.get()
            search_value = f'%{entry.get()}%'
            
            self.cursor.execute(f'''SELECT book_id, title, author, isbn, publisher, publication_year, category, 
                                available_copies, total_copies FROM books WHERE {search_field} LIKE ?''', (search_value,))
            
            for r in self.cursor.fetchall():
                copies_display = f"{r[7]}/{r[8]}"
                formatted_id = self.format_id(r[0])
                tree.insert("", tk.END, values=(formatted_id,) + r[1:-2] + (copies_display,))

        ttk.Button(sf, text="🔍 SEARCH", command=run_search, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(sf, text="CLEAR", command=lambda: (entry.delete(0, tk.END), run_search()), 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        run_search()

    def view_all_books_window(self):
        win, main = self.setup_sub_window("All Books Inventory", "1100x750")
        
        ttk.Label(main, text="📚 Complete Book Inventory", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_primary).pack(pady=(0, 20))
        
        # Filter controls
        filter_frame = ttk.LabelFrame(main, text="Filter & Search", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(20, 5))
        status_combo = ttk.Combobox(filter_frame, values=["All", "Available", "Out of Stock"], 
                                    state="readonly", width=15)
        status_combo.set("All")
        status_combo.pack(side=tk.LEFT, padx=5)
        
        # Books table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("ID", "Title", "Author", "ISBN", "Publisher", "Year", "Category", "Total", "Available", "Status")
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=22)
        
        # Configure columns
        tree.column("ID", width=60)
        tree.column("Title", width=150)
        tree.column("Author", width=120)
        tree.column("ISBN", width=100)
        tree.column("Publisher", width=100)
        tree.column("Year", width=60)
        tree.column("Category", width=100)
        tree.column("Total", width=60)
        tree.column("Available", width=70)
        tree.column("Status", width=90)
        
        for c in cols:
            tree.heading(c, text=c)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        stats_labels = {
            'total': ttk.Label(stats_frame, text="Total Books: 0", font=("Segoe UI", 10)),
            'available': ttk.Label(stats_frame, text="Available: 0", font=("Segoe UI", 10), 
                                  foreground=self.accent_tertiary),
            'issued': ttk.Label(stats_frame, text="Currently Issued: 0", font=("Segoe UI", 10),
                               foreground=self.accent_secondary)
        }
        
        stats_labels['total'].pack(side=tk.LEFT, padx=20)
        stats_labels['available'].pack(side=tk.LEFT, padx=20)
        stats_labels['issued'].pack(side=tk.LEFT, padx=20)
        
        def refresh_books():
            tree.delete(*tree.get_children())
            
            # Build query based on filters
            search_term = f'%{search_entry.get()}%'
            status_filter = status_combo.get()
            
            query = '''SELECT book_id, title, author, isbn, publisher, publication_year, category, 
                       total_copies, available_copies FROM books 
                       WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'''
            params = [search_term, search_term, search_term]
            
            if status_filter == "Available":
                query += " AND available_copies > 0"
            elif status_filter == "Out of Stock":
                query += " AND available_copies = 0"
            
            query += " ORDER BY title"
            
            self.cursor.execute(query, params)
            
            total_books = 0
            total_available = 0
            total_issued = 0
            
            for r in self.cursor.fetchall():
                formatted_id = self.format_id(r[0])
                total_copies = r[7]
                available_copies = r[8]
                
                # Determine status
                if available_copies == 0:
                    status = "❌ Out of Stock"
                elif available_copies == total_copies:
                    status = "✅ All Available"
                else:
                    status = f"⚠️ {total_copies - available_copies} Issued"
                
                tree.insert("", tk.END, values=(
                    formatted_id, r[1], r[2], r[3], r[4] or "", r[5] or "", 
                    r[6] or "", total_copies, available_copies, status
                ))
                
                total_books += 1
                total_available += available_copies
                total_issued += (total_copies - available_copies)
            
            # Update statistics
            stats_labels['total'].config(text=f"Total Books: {total_books}")
            stats_labels['available'].config(text=f"Available Copies: {total_available}")
            stats_labels['issued'].config(text=f"Currently Issued: {total_issued}")
        
        ttk.Button(filter_frame, text="🔍 SEARCH", command=refresh_books, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="REFRESH", command=refresh_books, 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        refresh_books()

    # --- MEMBER MANAGEMENT ---
    def show_member_menu(self):
        self.clear_screen()
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Label(header, text="👥 Member Management", font=("Segoe UI", 24, "bold"), 
                 foreground=self.accent_secondary).pack(side=tk.LEFT)
        
        ttk.Button(header, text="← Back to Dashboard", command=self.show_main_menu, 
                  style="Secondary.TButton").pack(side=tk.RIGHT)
        
        # Content
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Menu cards
        cards_frame = ttk.Frame(content)
        cards_frame.pack(expand=True)
        
        options = [
            ("➕ Register Member", "Add new library member", self.add_member_window),
            ("👀 View Members", "Browse all members", self.view_members_window)
        ]
        
        for idx, (title, desc, cmd) in enumerate(options):
            row = idx // 2
            col = idx % 2
            
            btn_frame = ttk.Frame(cards_frame)
            btn_frame.grid(row=row, column=col, padx=20, pady=20, sticky="ew")
            
            btn = tk.Frame(btn_frame, bg=self.bg_tertiary, relief="flat", height=120, width=300)
            btn.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            btn.pack_propagate(False)
            
            def make_hover(widget, command):
                def on_enter(e):
                    widget.config(bg=self.bg_secondary)
                def on_leave(e):
                    widget.config(bg=self.bg_tertiary)
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", lambda e, c=command: c())
                return widget
            
            btn = make_hover(btn, cmd)
            
            # Center the content vertically
            content_frame = tk.Frame(btn, bg=self.bg_tertiary)
            content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(content_frame, text=title, font=("Segoe UI", 14, "bold"), 
                    bg=self.bg_tertiary, fg=self.fg_text).pack(pady=(0, 5))
            tk.Label(content_frame, text=desc, font=("Segoe UI", 9), 
                    bg=self.bg_tertiary, fg=self.fg_muted).pack()

    def add_member_window(self):
        win, main = self.setup_sub_window("Register New Member", "600x500")
        
        ttk.Label(main, text="➕ Register New Member", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_secondary).pack(pady=(0, 20))
        
        group = ttk.LabelFrame(main, text="Member Information", padding="20")
        group.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("Full Name", "name"),
            ("Email Address", "email"),
            ("Phone Number", "phone"),
            ("Address", "address")
        ]
        
        ents = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(group, text=label, font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=10, padx=(0, 10))
            e = ttk.Entry(group, width=40)
            e.grid(row=i, column=1, sticky="ew", pady=10)
            ents[key] = e
        
        group.columnconfigure(1, weight=1)
            
        def save():
            self.cursor.execute('INSERT INTO members (name, email, phone, address, membership_date) VALUES (?,?,?,?,?)',
                               (ents["name"].get(), ents["email"].get(), ents["phone"].get(), 
                                ents["address"].get(), datetime.now().strftime('%Y-%m-%d')))
            self.conn.commit()
            member_id = self.cursor.lastrowid
            formatted_id = self.format_member_id(member_id)
            messagebox.showinfo("Success", f"Member registered successfully!\nMember ID: {formatted_id}")
            win.destroy()
        
        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="REGISTER MEMBER", command=save, style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)

    def view_members_window(self):
        win, main = self.setup_sub_window("Member Directory", "1000x700")
        
        ttk.Label(main, text="👥 Member Directory", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_secondary).pack(pady=(0, 20))
        
        # Table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("ID", "Name", "Email", "Phone", "Joined", "Status")
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=25)
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        self.cursor.execute('SELECT member_id, name, email, phone, membership_date, status FROM members')
        for r in self.cursor.fetchall():
            formatted_id = self.format_member_id(r[0])
            tree.insert("", tk.END, values=(formatted_id,) + r[1:])

    # --- TRANSACTIONS ---
    def show_transaction_menu(self):
        self.clear_screen()
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Label(header, text="🔄 Transaction Management", font=("Segoe UI", 24, "bold"), 
                 foreground=self.accent_tertiary).pack(side=tk.LEFT)
        
        ttk.Button(header, text="← Back to Dashboard", command=self.show_main_menu, 
                  style="Secondary.TButton").pack(side=tk.RIGHT)
        
        # Content
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Menu cards
        cards_frame = ttk.Frame(content)
        cards_frame.pack(expand=True)
        
        options = [
            ("📤 Issue Book", "Lend book to member", self.borrow_book_window),
            ("📥 Return Book", "Process book return", self.return_book_window),
            ("📊 Issued Books Status", "View currently issued books", self.view_issued_books_window)
        ]
        
        for idx, (title, desc, cmd) in enumerate(options):
            row = idx // 2
            col = idx % 2
            
            btn_frame = ttk.Frame(cards_frame)
            btn_frame.grid(row=row, column=col, padx=20, pady=20, sticky="ew")
            
            btn = tk.Frame(btn_frame, bg=self.bg_tertiary, relief="flat", height=120, width=300)
            btn.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            btn.pack_propagate(False)
            
            def make_hover(widget, command):
                def on_enter(e):
                    widget.config(bg=self.bg_secondary)
                def on_leave(e):
                    widget.config(bg=self.bg_tertiary)
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", lambda e, c=command: c())
                return widget
            
            btn = make_hover(btn, cmd)
            
            # Center the content vertically
            content_frame = tk.Frame(btn, bg=self.bg_tertiary)
            content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(content_frame, text=title, font=("Segoe UI", 14, "bold"), 
                    bg=self.bg_tertiary, fg=self.fg_text).pack(pady=(0, 5))
            tk.Label(content_frame, text=desc, font=("Segoe UI", 9), 
                    bg=self.bg_tertiary, fg=self.fg_muted).pack()

    def borrow_book_window(self):
        win, main = self.setup_sub_window("Issue Book", "600x450")
        
        ttk.Label(main, text="📤 Issue Book to Member", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_tertiary).pack(pady=(0, 20))
        
        group = ttk.LabelFrame(main, text="Transaction Details", padding="20")
        group.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("Member ID", "member"),
            ("Book ID", "book"),
            ("Loan Duration (days)", "duration")
        ]
        
        ents = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(group, text=label, font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=12, padx=(0, 10))
            e = ttk.Entry(group, width=35)
            e.grid(row=i, column=1, sticky="ew", pady=12)
            ents[key] = e
        
        # Set default duration
        ents["duration"].insert(0, "14")
        
        # Add helper text
        ttk.Label(group, text="Tip: Member ID as mem001, Book ID as 0001 or just 1", font=("Segoe UI", 8), 
                 foreground=self.fg_muted).grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
        group.columnconfigure(1, weight=1)
        
        def parse_id(id_str):
            """Extract numeric ID from formatted or plain ID"""
            id_str = id_str.strip()
            # Handle member IDs with 'mem' prefix
            if id_str.lower().startswith('mem'):
                return int(id_str[3:]) if len(id_str) > 3 else 0
            # Handle regular numeric IDs
            return int(id_str.lstrip('0')) if id_str else 0
        
        def process():
            try:
                days = int(ents["duration"].get())
                due = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                
                # Parse IDs
                member_id = parse_id(ents["member"].get())
                book_id = parse_id(ents["book"].get())
                
                # Check if book is available
                self.cursor.execute('SELECT available_copies, title FROM books WHERE book_id=?', (book_id,))
                result = self.cursor.fetchone()
                
                if not result or result[0] <= 0:
                    messagebox.showerror("Error", "Book not available or doesn't exist!")
                    return
                
                # Verify member exists
                self.cursor.execute('SELECT name FROM members WHERE member_id=?', (member_id,))
                member = self.cursor.fetchone()
                if not member:
                    messagebox.showerror("Error", "Member not found!")
                    return
                
                self.cursor.execute('INSERT INTO transactions (member_id, book_id, borrow_date, due_date) VALUES (?,?,?,?)',
                                   (member_id, book_id, datetime.now().strftime('%Y-%m-%d'), due))
                self.cursor.execute('UPDATE books SET available_copies=available_copies-1 WHERE book_id=?', (book_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", f"Book '{result[1]}' issued to {member[0]}\nDue date: {due}")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid IDs and duration!")
        
        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="ISSUE BOOK", command=process, style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)

    def return_book_window(self):
        win, main = self.setup_sub_window("Return Book", "600x400")
        
        ttk.Label(main, text="📥 Process Book Return", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_tertiary).pack(pady=(0, 20))
        
        group = ttk.LabelFrame(main, text="Return Details", padding="20")
        group.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(group, text="Transaction ID", font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 2))
        t_e = ttk.Entry(group, width=40)
        t_e.pack(pady=(0, 20), fill=tk.X)
        
        info_frame = ttk.Frame(group)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_label = ttk.Label(info_frame, text="Enter transaction ID to process return (e.g., 0001 or 1)", 
                              font=("Segoe UI", 9), foreground=self.fg_muted)
        info_label.pack(pady=10)
        
        def parse_id(id_str):
            """Extract numeric ID from formatted or plain ID"""
            return int(id_str.lstrip('0')) if id_str.strip() else 0
        
        def process():
            try:
                transaction_id = parse_id(t_e.get())
                
                self.cursor.execute('SELECT book_id, due_date, status FROM transactions WHERE transaction_id=?', (transaction_id,))
                res = self.cursor.fetchone()
                
                if res:
                    if res[2] == "returned":
                        messagebox.showwarning("Warning", "This book has already been returned!")
                        return
                    
                    # Calculate fine if overdue
                    due_date = datetime.strptime(res[1], '%Y-%m-%d')
                    days_late = (datetime.now() - due_date).days
                    fine = max(0, days_late * 1.0)  # $1 per day late
                    
                    self.cursor.execute('UPDATE transactions SET status="returned", return_date=?, fine_amount=? WHERE transaction_id=?', 
                                       (datetime.now().strftime('%Y-%m-%d'), fine, transaction_id))
                    self.cursor.execute('UPDATE books SET available_copies=available_copies+1 WHERE book_id=?', (res[0],))
                    self.conn.commit()
                    
                    msg = "Book returned successfully!"
                    if fine > 0:
                        msg += f"\n\nLate fee: ${fine:.2f} ({days_late} days late)"
                    
                    messagebox.showinfo("Success", msg)
                    win.destroy()
                else:
                    messagebox.showerror("Error", "Transaction not found!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid transaction ID!")
        
        button_frame = ttk.Frame(main)
        button_frame.pack(pady=20, fill=tk.X)
        ttk.Button(button_frame, text="PROCESS RETURN", command=process, style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="CANCEL", command=win.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=5, ipady=8, fill=tk.X, expand=True)

    def view_issued_books_window(self):
        win, main = self.setup_sub_window("Issued Books Status", "1200x750")
        
        ttk.Label(main, text="📊 Currently Issued Books", font=("Segoe UI", 20, "bold"), 
                 foreground=self.accent_tertiary).pack(pady=(0, 20))
        
        # Filter options
        filter_frame = ttk.LabelFrame(main, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        status_combo = ttk.Combobox(filter_frame, values=["All", "Active (Not Returned)", "Overdue", "Returned"], 
                                    state="readonly", width=20)
        status_combo.set("Active (Not Returned)")
        status_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Search Member/Book:").pack(side=tk.LEFT, padx=(20, 5))
        search_entry = ttk.Entry(filter_frame, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("Trans ID", "Member ID", "Member Name", "Book ID", "Book Title", 
                "Issue Date", "Due Date", "Return Date", "Days", "Status", "Fine")
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=22)
        
        # Configure columns
        tree.column("Trans ID", width=70)
        tree.column("Member ID", width=80)
        tree.column("Member Name", width=120)
        tree.column("Book ID", width=70)
        tree.column("Book Title", width=180)
        tree.column("Issue Date", width=90)
        tree.column("Due Date", width=90)
        tree.column("Return Date", width=90)
        tree.column("Days", width=60)
        tree.column("Status", width=100)
        tree.column("Fine", width=70)
        
        for c in cols:
            tree.heading(c, text=c)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.LabelFrame(main, text="Summary", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        stats_labels = {
            'total': ttk.Label(stats_frame, text="Total Transactions: 0", font=("Segoe UI", 10)),
            'active': ttk.Label(stats_frame, text="Active: 0", font=("Segoe UI", 10), 
                               foreground=self.accent_tertiary),
            'overdue': ttk.Label(stats_frame, text="Overdue: 0", font=("Segoe UI", 10),
                                foreground=self.accent_danger),
            'fines': ttk.Label(stats_frame, text="Total Fines: $0.00", font=("Segoe UI", 10),
                              foreground=self.accent_secondary)
        }
        
        stats_labels['total'].pack(side=tk.LEFT, padx=15)
        stats_labels['active'].pack(side=tk.LEFT, padx=15)
        stats_labels['overdue'].pack(side=tk.LEFT, padx=15)
        stats_labels['fines'].pack(side=tk.LEFT, padx=15)
        
        def refresh_data():
            tree.delete(*tree.get_children())
            
            status_filter = status_combo.get()
            search_term = f'%{search_entry.get()}%'
            
            # Build query
            query = '''SELECT t.transaction_id, t.member_id, m.name, t.book_id, b.title,
                       t.borrow_date, t.due_date, t.return_date, t.status, t.fine_amount
                       FROM transactions t
                       JOIN members m ON t.member_id = m.member_id
                       JOIN books b ON t.book_id = b.book_id
                       WHERE (m.name LIKE ? OR b.title LIKE ?)'''
            
            params = [search_term, search_term]
            
            if status_filter == "Active (Not Returned)":
                query += " AND t.status = 'borrowed'"
            elif status_filter == "Overdue":
                query += " AND t.status = 'borrowed' AND date(t.due_date) < date('now')"
            elif status_filter == "Returned":
                query += " AND t.status = 'returned'"
            
            query += " ORDER BY t.borrow_date DESC"
            
            self.cursor.execute(query, params)
            
            total_trans = 0
            active_count = 0
            overdue_count = 0
            total_fines = 0.0
            
            for r in self.cursor.fetchall():
                trans_id = self.format_id(r[0])
                member_id = self.format_member_id(r[1])
                book_id = self.format_id(r[3])
                
                issue_date = r[5]
                due_date = r[6]
                return_date = r[7] if r[7] else "Not Returned"
                status = r[8]
                fine = r[9] if r[9] else 0.0
                
                # Calculate days
                if return_date == "Not Returned":
                    days_out = (datetime.now() - datetime.strptime(issue_date, '%Y-%m-%d')).days
                    days_display = f"{days_out} days"
                    
                    # Check if overdue
                    due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                    if datetime.now() > due_datetime:
                        days_overdue = (datetime.now() - due_datetime).days
                        status_display = f"⚠️ OVERDUE ({days_overdue}d)"
                        overdue_count += 1
                    else:
                        status_display = "✅ Active"
                        active_count += 1
                else:
                    issue_dt = datetime.strptime(issue_date, '%Y-%m-%d')
                    return_dt = datetime.strptime(return_date, '%Y-%m-%d')
                    days_out = (return_dt - issue_dt).days
                    days_display = f"{days_out} days"
                    status_display = "✔️ Returned"
                
                fine_display = f"${fine:.2f}" if fine > 0 else "-"
                
                tree.insert("", tk.END, values=(
                    trans_id, member_id, r[2], book_id, r[4], 
                    issue_date, due_date, return_date, days_display, 
                    status_display, fine_display
                ))
                
                total_trans += 1
                total_fines += fine
            
            # Update statistics
            stats_labels['total'].config(text=f"Total Transactions: {total_trans}")
            stats_labels['active'].config(text=f"Active: {active_count}")
            stats_labels['overdue'].config(text=f"Overdue: {overdue_count}")
            stats_labels['fines'].config(text=f"Total Fines: ${total_fines:.2f}")
        
        ttk.Button(filter_frame, text="🔍 FILTER", command=refresh_data, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="REFRESH", command=refresh_data, 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        refresh_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
