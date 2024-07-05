from app import app, db, Word

def clear_words():
    with app.app_context():
        num_rows_deleted = db.session.query(Word).delete()
        db.session.commit()
        print(f"{num_rows_deleted} words deleted from the database.")

if __name__ == '__main__':
    clear_words()
