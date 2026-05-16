# This is a simple Flask application for managing tasks. It allows users to add, complete, delete, and export tasks as a CSV file. The application uses SQLite for data storage and includes basic search functionality on the main page.
# The code includes routes for the main page, adding tasks, completing tasks, deleting tasks, and exporting tasks. The export functionality generates a CSV file containing all tasks with their ID, title, and status.
# Note: The delete route has been simplified to use a GET request for easier testing, but in a production environment, it is recommended to use POST or DELETE methods for such actions to enhance security.
#  To run this application, ensure you have Flask installed and a SQLite database named 'task.db' with a 'tasks' table that has columns 'id', 'title', and 'status'. You can create the database and table using the following SQL commands:
import os

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

import csv
import io
from flask import Response  # Add Response to your imports at the top

# This is a simple Flask application for managing tasks. It allows users to add, complete, delete, and export tasks as a CSV file. The application uses SQLite for data storage and includes basic search functionality on the main page.
# The code includes routes for the main page, adding tasks, completing tasks, deleting tasks, and exporting tasks. The export functionality generates a CSV file containing all tasks with their ID, title, and status.
# Note: The delete route has been simplified to use a GET request for easier testing, but in a production environment, it is recommended to use POST or DELETE methods for such actions to enhance security.
#  To run this application, ensure you have Flask installed and a SQLite database named 'task.db' with a 'tasks' table that has columns 'id', 'title', and 'status'. You can create the database and table using the following SQL commands:

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Function to get a database connection
# This function connects to the SQLite database and sets the row factory to sqlite3.Row, which allows us to access columns by name.
# It returns the connection object, which can be used to execute SQL queries and manage the database.
# Note: Remember to close the connection after using it to free up resources.

def get_db_connection():
    conn = sqlite3.connect("task.db")
    conn.row_factory = sqlite3.Row
    return conn

# Function to initialize the database and create the 'tasks' table if it doesn't exist. 
# This function is called once when the application starts to ensure that the necessary table is available for storing tasks. 
# The 'tasks' table has three columns: 'id' (an auto-incrementing primary key), 'title' (a text field for the task title), and 'status' (a text field to indicate whether the task is pending or completed).
# After executing the SQL command to create the table, the connection is committed and closed to save changes and free up resources. 
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Call the function once when the script starts
init_db()


# Route for the main page of the application. It handles both displaying all tasks and searching for tasks based on a query parameter.
# If a 'search' parameter is present in the URL, it performs a SQL query to find tasks whose titles contain the search term using the LIKE operator. If no search term is provided, it retrieves all tasks from the database.
# The results are then passed to the 'index.html' template for rendering, along with the search query to maintain the search state in the UI. Finally, the database connection is closed to free up resources.
# Example usage: Accessing the main page with a search query would look like this: http://localhost:5000/?search=groceries
# The search functionality allows users to quickly find specific tasks by their title, enhancing the usability of the application.
@app.route("/")
def index():
    # Look for a 'search' parameter in the URL (e.g., /?search=groceries)
    search_query = request.args.get("search", "")

    conn = get_db_connection()

    if search_query:
        # Use LIKE with % wildcards to find tasks containing the search term
        query = "SELECT * FROM tasks WHERE title LIKE ?"
        tasks = conn.execute(query, ("%" + search_query + "%",)).fetchall()
    else:
        # No search term, get all tasks
        tasks = conn.execute("SELECT * FROM tasks").fetchall()

    conn.close()
    return render_template("index.html", tasks=tasks, search_query=search_query)

# Route to handle adding a new task. It listens for POST requests at the '/add' endpoint. When a new task is submitted, it retrieves the task title from the form data, checks if it's not empty, and then inserts it into the 'tasks' table in the database with a default status of "Pending". After successfully adding the task, it flashes a success message to the user and redirects back to the main page.
# Example usage: To add a new task, you would typically fill out a form on the main page and submit it, which would send a POST request to this route with the task title in the form data.

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    if title:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tasks (title, status) VALUES (?, ?)", (title, "Pending")
        )
        conn.commit()
        conn.close()
        flash("Task added successfully!", "success")
    return redirect(url_for("index"))


# --- FIX 1: COMPLETE TASK ROUTE ---
# This route is responsible for marking a task as completed. It listens for GET requests at the '/complete/<int:id>' endpoint, where 'id' is the unique identifier of the task to be marked as completed. When this route is accessed, it updates the status of the specified task in the database to "Completed". After updating the task, it flashes an informational message to the user and redirects back to the main page.
# Example usage: To mark a task as completed, you would typically click a "Complete" button next to the task on the main page, which would send a GET request to this route with the task's ID in the URL (e.g., http://localhost:5000/complete/1 to mark the task with ID 1 as completed).
# Note: In a production environment, it is recommended to use POST or PUT methods for such actions to enhance security, but for simplicity in this example, we are using GET.
# This route allows users to easily update the status of their tasks, helping them keep track of what has been completed and what is still pending.
# Note: In a production environment, it is recommended to use POST or PUT methods for such actions to enhance security, but for simplicity in this example, we are using GET.

@app.route("/complete/<int:id>")
def complete_task(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("Completed", id))
    conn.commit()
    conn.close()
    flash("Task marked as Completed!", "info")
    return redirect(url_for("index"))


# --- FIX 2: DELETE TASK ROUTE (Simplified to GET) ---
# This route is responsible for deleting a task from the database. It listens for GET requests at the '/delete/<int:id>' endpoint, where 'id' is the unique identifier of the task to be deleted. When this route is accessed, it executes a SQL query to remove the specified task from the 'tasks' table in the database. After successfully deleting the task, it flashes a warning message to the user and redirects back to the main page.
# Example usage: To delete a task, you would typically click a "Delete" button next to the task on the main page, which would send a GET request to this route with the task's ID in the URL (e.g., http://localhost:5000/delete/1 to delete the task with ID 1).
# Note: In a production environment, it is recommended to use POST or DELETE methods for such actions to enhance security, but for simplicity in this example, we are using GET. This route allows users to remove tasks that are no longer needed, helping them keep their task list organized and up-to-date.

@app.route("/delete/<int:id>")
def delete_task(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Task deleted successfully!", "warning")
    return redirect(url_for("index"))

# --- FIX 3: EXPORT TASKS AS CSV ---
# This route is responsible for exporting all tasks in the database as a CSV file. It listens
# for GET requests at the '/export' endpoint. When this route is accessed, it retrieves all tasks from the 'tasks' table in the database and writes them to an in-memory string file using the csv module. The CSV file includes a header row with column names ("ID", "Task Title", "Status") followed by rows of task data. Finally, it prepares the response as a downloadable file with the appropriate MIME type and headers to prompt the user to download the generated CSV file (e.g., "my_tasks.csv"). This functionality allows users to easily export their task data for backup or analysis purposes.
# Example usage: To export tasks, you would typically click an "Export" button on the main page, which would send a GET request to this route (e.g., http://localhost:5000/export) and trigger the download of the CSV file containing all tasks.
# Note: In a production environment, you may want to implement additional features such as filtering tasks before export or allowing users to choose the file format (e.g., Excel, JSON) for better flexibility.

# This route allows users to easily export their task data for backup or analysis purposes. It retrieves all tasks from the database, writes them to a CSV format in memory, and sends the file as a downloadable response to the user. The CSV file includes a header row with column names ("ID", "Task Title", "Status") followed by rows of task data, making it easy for users to view and manage their tasks outside of the application.
# Example usage: To export tasks, you would typically click an "Export" button on the main page, which would send a GET request to this route (e.g., http://localhost:5000/export) and trigger the download of the CSV file containing all tasks.
# Note: In a production environment, you may want to implement additional features such as filtering tasks before export or allowing users to choose the file format (e.g., Excel, JSON) for better flexibility.

@app.route("/export")
def export_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT id, title, status FROM tasks").fetchall()
    conn.close()

    # Create an in-memory string file
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the Header row
    writer.writerow(["ID", "Task Title", "Status"])

    # Write the Data rows
    for task in tasks:
        writer.writerow([task["id"], task["title"], task["status"]])

    # Prepare the response as a downloadable file
    # The 'seek(0)' method is called to move the file pointer back to the beginning of the in-memory file before reading its content for the response. This ensures that the entire CSV content is included in the response when the user downloads the file.   
    # The 'Response' object is used to create an HTTP response with the CSV content, setting the appropriate MIME type for CSV files and including headers to prompt the user to download the file with a specified filename (e.g., "my_tasks.csv"). This allows users to easily export their task data for backup or analysis purposes.    
    # Example usage: To export tasks, you would typically click an "Export" button on the main page, which would send a GET request to this route (e.g., http://localhost:5000/export) and trigger the download of the CSV file containing all tasks.   
    # Note: In a production environment, you may want to implement additional features such as filtering tasks before export or allowing users to choose the file format (e.g., Excel, JSON) for better flexibility.    

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=my_tasks.csv"},
    )

# Run the Flask application in debug mode. This allows for easier development and debugging by providing detailed error messages and automatically reloading the server when code changes are detected. To start the application, simply run this script, and it will be accessible at http://localhost:5000/ by default.
# Note: In a production environment, you should set 'debug=False' and consider using a production-ready server such as Gunicorn or uWSGI to serve the application for better performance and security.

if __name__ == "__main__":
    app.run(debug=True)
# To run the application on a specific port, you can set the 'PORT' environment variable. 
# If the 'PORT' variable is not set, it will default to 5000. 
# This allows for flexibility in deployment environments where the port may be dynamically assigned (e.g., when deploying to platforms like Heroku). 
# The application will listen on all available network interfaces (host="                      
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)  
