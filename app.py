from flask import Flask, request, render_template, redirect, url_for
import oracledb

app = Flask(__name__)

# Connection details
username = 'C##admin'
password = 'Password1'
dsn = '127.0.0.1:1521/FREE'

@app.route('/')
def home():
    users = get_all_users()
    return render_template('index.html', users=users)

@app.route('/test')
def test_connection():
    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        return "Connection successful!"
    except oracledb.DatabaseError as e:
        error, = e.args
        return f"Error: {error.message}", 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/insert', methods=['POST'])
def insert_user():

    first_name = request.form['firstName']
    last_name = request.form['lastName']
    username = request.form['username']
    email = request.form['email']

    insert_query = """
    INSERT INTO USERS (firstName, lastName, username, email)
    VALUES (:1, :2, :3, :4)
    """

    try:
        print(f"Inserting user: {first_name}, {last_name}, {username}, {email}")
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        with conn.cursor() as cur:
            cur.execute(insert_query, (first_name, last_name, username, email))
        conn.commit()
    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Error during insertion: {error.message}")  # Log detailed error
        return f"Error: {error.message}", 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return redirect(url_for('home'))


@app.route('/edit/<int:user_id>', methods=['GET', 'PUT'])
def edit_user(user_id):
    if request.method == 'PUT':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['username']
        email = request.form['email']

        update_query = """
        UPDATE USERS
        SET firstName = :1, lastName = :2, username = :3, email = :4
        WHERE id = :5
        """

        try:
            conn = oracledb.connect(user=username, password=password, dsn=dsn)
            with conn.cursor() as cur:
                cur.execute(update_query, (first_name, last_name, username, email, user_id))
            conn.commit()
        except oracledb.DatabaseError as e:
            error, = e.args
            return f"Error: {error.message}", 500
        finally:
            if 'conn' in locals() and conn:
                conn.close()
        return redirect(url_for('home'))

    user = get_user(user_id)
    return render_template('edit.html', user=user)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    delete_query = "DELETE FROM USERS WHERE id = :1"

    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        with conn.cursor() as cur:
            cur.execute(delete_query, (user_id,))
        conn.commit()
    except oracledb.DatabaseError as e:
        error, = e.args
        return f"Error: {error.message}", 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return redirect(url_for('home'))

def get_all_users():
    select_query = "SELECT id, firstName, lastName, username, email FROM USERS"
    users = []
    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        with conn.cursor() as cur:
            cur.execute(select_query)
            users = cur.fetchall()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return users

def get_user(user_id):
    select_query = "SELECT id, firstName, lastName, username, email FROM USERS WHERE id = :1"
    user = None
    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        with conn.cursor() as cur:
            cur.execute(select_query, (user_id,))
            user = cur.fetchone()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return user

if __name__ == '__main__':
    app.run(debug=True)
