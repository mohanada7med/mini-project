from flask import Flask, render_template, request, redirect, url_for, flash
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "db"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "appuser"),
    "password": os.environ.get("MYSQL_PASSWORD", "app_pass"),
    "database": os.environ.get("MYSQL_DATABASE", "mydatabase"),
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email:
            flash("Name and email are required.")
            return redirect(url_for("index"))

        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = (
            "INSERT INTO submissions (name, email, message) VALUES (%s, %s, %s)"
        )
        cursor.execute(insert_query, (name, email, message))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Data saved successfully.")
        return redirect(url_for("show_data"))

    return render_template("index.html")


@app.route("/show")
def show_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, message, created_at FROM submissions ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("show.html", submissions=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
