"""Run this script once to set the admin password after importing database.sql"""
from werkzeug.security import generate_password_hash
import sys

password = input("Enter admin password (default: admin123): ").strip() or "admin123"
hashed = generate_password_hash(password)
print(f"\nGenerated hash: {hashed}")
print(f"\nRun this SQL in phpMyAdmin:")
print(f"UPDATE users SET password_hash = '{hashed}' WHERE email = 'admin@vsalon.com';")
