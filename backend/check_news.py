import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="brvm_db",
    user="brvm_user",
    password="brvm_password"
)
cur = conn.cursor()

print("=== TABLE NEWS ===")
cur.execute("SELECT COUNT(*) FROM news")
print(f"Total articles : {cur.fetchone()[0]}")

cur.execute("SELECT MIN(date_publication), MAX(date_publication) FROM news")
row = cur.fetchone()
print(f"Date la plus ancienne : {row[0]}")
print(f"Date la plus recente  : {row[1]}")

print("\n--- Par source ---")
cur.execute("SELECT provenance, COUNT(*) FROM news GROUP BY provenance ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} articles")

print("\n--- Par annee ---")
cur.execute("SELECT EXTRACT(YEAR FROM date_publication)::int, COUNT(*) FROM news WHERE date_publication IS NOT NULL GROUP BY 1 ORDER BY 1")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} articles")

print("\n--- 5 exemples d'articles ---")
cur.execute("SELECT DATE(date_publication), titre, provenance, ticker FROM news n LEFT JOIN actions a ON n.action_id = a.id ORDER BY date_publication DESC LIMIT 5")
for r in cur.fetchall():
    print(f"  [{r[0]}] [{r[2]}] [{r[3]}] {r[1][:80]}")

cur.close()
conn.close()
