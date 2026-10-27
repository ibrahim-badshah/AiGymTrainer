import streamlit as st
import sqlite3
from pathlib import Path

_DB_PATH = str(Path(__file__).parent.parent.parent/"data.db")

@st.cache_resource
def _get_connection():
    conn = sqlite3.connect(_DB_PATH,check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()

    with conn:
        conn.execute("""
            create table if not exists users(
                id INTEGER primary key autoincrement,
                username TEXT unique NOT NULL,
                created_at TIMESTAMP default CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            create table if not exists exercises(
                id INTEGER primary key autoincrement,
                user_id INTEGER NOT NULL references users(id),
                exercise_name text not null,
                reps INTEGER not null default 0,
                sets INTEGER not null default 0,
                time INTEGER not null default 0,
                created_at TIMESTAMP default CURRENT_TIMESTAMP
            )
        """)

def get_user(username):
    conn = _get_connection()

    return conn.execute("""
            select * from users where username = (?)    
    """,(username,)).fetchone()

def create_user(username):
    conn = _get_connection()

    with conn:
        conn.execute("""
            insert into users (username) Values (?)
        """,(username,))

    return get_user(username)

def get_or_create_user(username):
    user = get_user(username)

    if user is None:
        user = create_user(username)

    return user


def add_exercise(user_id,exercise_name,reps,sets,time):
    conn = _get_connection()

    with conn:
        existing = conn.execute("""
            select * from exercises 
            where user_id = ? and exercise_name = ? and date('created_at') = data('now')
        """,(user_id,exercise_name)).fetchone()

        if existing:
            conn.execute("""
                update exercises
                set reps = reps + ?,sets = sets + ?,time = time + ?
                where id = ?
            """,(reps,sets,time,existing['id']))
        else:
            conn.execute("""
                insert into exercises (user_id,exercise_name,sets,reps,time)
                values (?,?,?,?,?,?)
            """,(user_id,exercise_name,sets,reps,time))


def get_users_exercises(user_id):
    conn = _get_connection()

    return conn.execute("""
        select * from exercises
        where user_id = ?
    """,(user_id)).fetchall()