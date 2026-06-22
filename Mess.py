import sqlite3
from datetime import datetime

conn = sqlite3.connect("mess.db")
cur = conn.cursor()

# ---------------- TABLES ----------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    id TEXT PRIMARY KEY,
    name TEXT,
    password TEXT,
    balance REAL DEFAULT 0.0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS meals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    meal_type TEXT,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS menu(
    day TEXT PRIMARY KEY,
    breakfast TEXT,
    lunch TEXT,
    dinner TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    date TEXT,
    meal_type TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fees(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    amount REAL,
    month TEXT,
    paid_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()

# ---------------- DEFAULT MENU ----------------
def setup_default_menu():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    default_meals = {
        'Monday': ('Idli/Sambar', 'Rice/Dal/Curry', 'Chapati/Paneer'),
        'Tuesday': ('Dosa/Chutney', 'Rice/Sambar/Veg', 'Roti/Matar Paneer'),
        'Wednesday': ('Pongal/Chutney', 'Rice/Dal/Fry', 'Chapati/Aloo Gobi'),
        'Thursday': ('Upma', 'Rice/Sambar/Egg', 'Roti/Dal'),
        'Friday': ('Puri/Sagu', 'Rice/Dal/Chicken', 'Chapati/Mix Veg'),
        'Saturday': ('Masala Dosa', 'Rice/Sambar/Fish', 'Roti/Paneer'),
        'Sunday': ('Idli/Vada', 'Rice/Dal/Sweet', 'Chapati/Special')
    }
    
    for day, (breakfast, lunch, dinner) in default_meals.items():
        cur.execute("INSERT OR IGNORE INTO menu VALUES(?,?,?,?)", 
                   (day, breakfast, lunch, dinner))
    conn.commit()

setup_default_menu()

# ---------------- REGISTER FUNCTION ----------------
def register_student(stu_id, name, password):
    try:
        cur.execute("SELECT id FROM students WHERE id=?", (stu_id,))
        existing = cur.fetchone()
        
        if existing:
            print("❌ ID already exists. Try another ID.")
        else:
            cur.execute("INSERT INTO students VALUES(?,?,?,0.0)", 
                       (stu_id, name, password))
            conn.commit()
            print("✅ Student registered successfully!")
            
    except Exception as e:
        print("Error:", e)

# ---------------- LOGIN FUNCTION ----------------
def login_student(stu_id, password):
    cur.execute("SELECT * FROM students WHERE id=? AND password=?", 
               (stu_id, password))
    user = cur.fetchone()
    
    if user:
        print("✅ Login successful!")
        print(f"Welcome {user[1]}!")
        print(f"Current Balance: ₹{user[3]:.2f}")
        return True
    else:
        print("❌ Invalid ID or password")
        return False

# ---------------- VIEW MENU ----------------
def view_menu():
    print("\n📋 WEEKLY MENU")
    print("-" * 60)
    cur.execute("SELECT * FROM menu ORDER BY CASE day "
                "WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 "
                "WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 "
                "WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 "
                "WHEN 'Sunday' THEN 7 END")
    menus = cur.fetchall()
    
    for menu in menus:
        print(f"\n{menu[0]}:")
        print(f"  Breakfast: {menu[1]}")
        print(f"  Lunch: {menu[2]}")
        print(f"  Dinner: {menu[3]}")
    print("-" * 60)

# ---------------- TAKE ATTENDANCE ----------------
def take_attendance(stu_id, meal_type):
    date = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT * FROM attendance WHERE student_id=? AND date=? AND meal_type=?", 
               (stu_id, date, meal_type))
    existing = cur.fetchone()
    
    if existing:
        print(f"❌ Already marked attendance for {meal_type} today")
    else:
        cur.execute("INSERT INTO attendance (student_id, date, meal_type, status) VALUES(?,?,?,?)",
                   (stu_id, date, meal_type, 'Present'))
        conn.commit()
        
        # Deduct meal cost (assume ₹50 per meal)
        cur.execute("UPDATE students SET balance = balance - 50 WHERE id=?", (stu_id,))
        conn.commit()
        print(f"✅ Attendance marked for {meal_type} | ₹50 deducted")

# ---------------- PAY FEES ----------------
def pay_fees(stu_id, amount):
    try:
        cur.execute("SELECT balance FROM students WHERE id=?", (stu_id,))
        current_balance = cur.fetchone()[0]
        
        new_balance = current_balance + amount
        cur.execute("UPDATE students SET balance=? WHERE id=?", (new_balance, stu_id))
        conn.commit()
        
        month = datetime.now().strftime("%B %Y")
        paid_date = datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO fees (student_id, amount, month, paid_date) VALUES(?,?,?,?)",
                   (stu_id, amount, month, paid_date))
        conn.commit()
        
        print(f"✅ ₹{amount} added successfully!")
        print(f"New Balance: ₹{new_balance:.2f}")
        
    except Exception as e:
        print("Error:", e)

# ---------------- VIEW ATTENDANCE ----------------
def view_attendance(stu_id):
    cur.execute("SELECT date, meal_type, status FROM attendance WHERE student_id=? ORDER BY date DESC LIMIT 10",
               (stu_id,))
    records = cur.fetchall()
    
    if records:
        print("\n📊 Recent Attendance:")
        print("-" * 40)
        for record in records:
            print(f"{record[0]} | {record[1]} | {record[2]}")
    else:
        print("No attendance records found")

# ---------------- STUDENT DASHBOARD ----------------
def student_dashboard(stu_id):
    while True:
        print("\n" + "="*50)
        print("🎯 STUDENT DASHBOARD")
        print("="*50)
        print("1. View Menu")
        print("2. Mark Attendance")
        print("3. Pay Fees")
        print("4. View My Attendance")
        print("5. Check Balance")
        print("6. Logout")
        print("="*50)
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            view_menu()
            
        elif choice == "2":
            print("\nMeal Types:")
            print("1. Breakfast")
            print("2. Lunch")
            print("3. Dinner")
            meal_choice = input("Select meal (1-3): ")
            
            meal_map = {'1': 'Breakfast', '2': 'Lunch', '3': 'Dinner'}
            if meal_choice in meal_map:
                take_attendance(stu_id, meal_map[meal_choice])
            else:
                print("❌ Invalid choice")
            
        elif choice == "3":
            try:
                amount = float(input("Enter amount to pay: ₹"))
                if amount > 0:
                    pay_fees(stu_id, amount)
                else:
                    print("❌ Amount must be positive")
            except ValueError:
                print("❌ Invalid amount")
            
        elif choice == "4":
            view_attendance(stu_id)
            
        elif choice == "5":
            cur.execute("SELECT balance FROM students WHERE id=?", (stu_id,))
            balance = cur.fetchone()[0]
            print(f"\n💰 Current Balance: ₹{balance:.2f}")
            
        elif choice == "6":
            print("Logging out...")
            break
            
        else:
            print("❌ Invalid choice")

# ---------------- ADMIN FUNCTIONS ----------------
def admin_login():
    admin_pass = "admin123"
    pwd = input("Enter Admin Password: ")
    return pwd == admin_pass

def admin_dashboard():
    if not admin_login():
        print("❌ Invalid admin password")
        return
    
    while True:
        print("\n" + "="*50)
        print("👑 ADMIN DASHBOARD")
        print("="*50)
        print("1. View All Students")
        print("2. View All Attendance")
        print("3. View All Payments")
        print("4. Update Menu")
        print("5. View Student Details")
        print("6. Back to Main Menu")
        print("="*50)
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            cur.execute("SELECT id, name, balance FROM students")
            students = cur.fetchall()
            print("\n📚 All Students:")
            print("-" * 50)
            for stu in students:
                print(f"ID: {stu[0]} | Name: {stu[1]} | Balance: ₹{stu[2]:.2f}")
                
        elif choice == "2":
            cur.execute("SELECT * FROM attendance ORDER BY date DESC LIMIT 20")
            records = cur.fetchall()
            print("\n📊 All Attendance Records:")
            print("-" * 60)
            for rec in records:
                print(f"Student: {rec[1]} | Date: {rec[2]} | Meal: {rec[3]} | Status: {rec[4]}")
                
        elif choice == "3":
            cur.execute("SELECT * FROM fees ORDER BY paid_date DESC")
            fees = cur.fetchall()
            print("\n💰 Payment Records:")
            print("-" * 60)
            for fee in fees:
                print(f"Student: {fee[1]} | Amount: ₹{fee[2]} | Month: {fee[3]} | Date: {fee[4]}")
                
        elif choice == "4":
            update_menu()
            
        elif choice == "5":
            sid = input("Enter Student ID: ")
            cur.execute("SELECT * FROM students WHERE id=?", (sid,))
            student = cur.fetchone()
            if student:
                print(f"\n📋 Student Details:")
                print(f"ID: {student[0]}")
                print(f"Name: {student[1]}")
                print(f"Balance: ₹{student[3]:.2f}")
                
                # Show attendance summary
                cur.execute("SELECT meal_type, COUNT(*) FROM attendance WHERE student_id=? GROUP BY meal_type",
                          (sid,))
                summary = cur.fetchall()
                print("\nAttendance Summary:")
                for item in summary:
                    print(f"  {item[0]}: {item[1]} times")
            else:
                print("❌ Student not found")
            
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")

def update_menu():
    print("\n📝 Update Menu:")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        print(f"\n{day}:")
        breakfast = input("  Breakfast: ")
        lunch = input("  Lunch: ")
        dinner = input("  Dinner: ")
        
        cur.execute("UPDATE menu SET breakfast=?, lunch=?, dinner=? WHERE day=?",
                   (breakfast, lunch, dinner, day))
    conn.commit()
    print("✅ Menu updated successfully!")

# ---------------- MAIN MENU ----------------
while True:
    print("\n" + "="*50)
    print("🏫 MESS MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Student Registration")
    print("2. Student Login")
    print("3. Admin Login")
    print("4. View Menu (Public)")
    print("5. Exit")
    print("="*50)
    
    choice = input("Enter choice: ")
    
    if choice == "1":
        sid = input("Enter Student ID: ")
        name = input("Enter Name: ")
        pwd = input("Enter Password: ")
        register_student(sid, name, pwd)
        
    elif choice == "2":
        sid = input("Enter Student ID: ")
        pwd = input("Enter Password: ")
        if login_student(sid, pwd):
            student_dashboard(sid)
            
    elif choice == "3":
        admin_dashboard()
        
    elif choice == "4":
        view_menu()
        
    elif choice == "5":
        print("👋 Thank you for using Mess Management System!")
        break
        
    else:
        print("❌ Invalid choice")

# ---------------- CLOSE CONNECTION ----------------
conn.close()