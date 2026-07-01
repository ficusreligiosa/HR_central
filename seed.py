from app.database import SessionLocal, engine
from app.models.user import User
from app.models.employee import Employee
from app.database import Base
from app.auth import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Already seeded. Skipping.")
        db.close()
        return

    users = [
        User(username="admin", password_hash=hash_password("Admin@123"), display_name="Administrator", role="admin"),
        User(username="harsh", password_hash=hash_password("Harsh@123"), display_name="Harsh Kumar", role="hr"),
        User(username="nupur", password_hash=hash_password("Nupur@123"), display_name="Nupur Pandey", role="doc"),
        User(username="emp",   password_hash=hash_password("Emp@123"),   display_name="Employee", role="emp"),
    ]
    for u in users:
        db.add(u)
    db.commit()
    print("✅ Users created successfully")
    print("   admin / Admin@123")
    print("   harsh / Harsh@123")
    print("   nupur / Nupur@123")
    print("   emp   / Emp@123")
    db.close()

if __name__ == "__main__":
    seed()