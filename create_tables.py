import psycopg2

# Your database connection
conn = psycopg2.connect(
    "postgresql://blog_zb5b_user:6T1crcUH0vuYp8vrIG9i9ERZh4UohKwL@dpg-d6ttpihj16oc73fjc2b0-a/blog_zb5b"
)

cursor = conn.cursor()

# Read schema.sql and execute it
with open("database/schema.sql", "r") as f:
    sql = f.read()

# Split by semicolon and execute each statement
for statement in sql.split(";"):
    statement = statement.strip()
    if statement:
        try:
            cursor.execute(statement)
            print(f"✓ Executed: {statement[:50]}...")
        except Exception as e:
            print(f"✗ Error: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n✅ Tables created successfully on Render!")
