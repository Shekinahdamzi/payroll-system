from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# Create database
conn = sqlite3.connect("payroll.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
id TEXT,
name TEXT,
position TEXT,
salary REAL,
allowance REAL,
tax REAL,
net REAL
)
""")
conn.commit()
conn.close()

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["user"] = "admin"
            return redirect("/dashboard")
    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()

    if request.method == "POST":
        emp_id = request.form["id"]
        name = request.form["name"]
        position = request.form["position"]
        salary = float(request.form["salary"])
        allowance = float(request.form["allowance"])
        tax = float(request.form["tax"])

        net = salary + allowance - tax

        cursor.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?)",
                       (emp_id,name,position,salary,allowance,tax,net))
        conn.commit()

    cursor.execute("SELECT * FROM employees")
    data = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", employees=data)

@app.route("/payslip/<emp_id>")
def payslip(emp_id):
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
    emp = cursor.fetchone()
    conn.close()

    file_name = f"{emp_id}_payslip.pdf"

    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("EMPLOYEE PAYSLIP", styles['Title']))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"ID: {emp[0]}", styles['Normal']))
    content.append(Paragraph(f"Name: {emp[1]}", styles['Normal']))
    content.append(Paragraph(f"Position: {emp[2]}", styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Salary: {emp[3]}", styles['Normal']))
    content.append(Paragraph(f"Allowance: {emp[4]}", styles['Normal']))
    content.append(Paragraph(f"Tax: {emp[5]}", styles['Normal']))
    content.append(Paragraph(f"Net Salary: {emp[6]}", styles['Normal']))

    doc.build(content)

    return f"Payslip generated: {file_name}"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
