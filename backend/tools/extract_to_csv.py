import pandas as pd
import psycopg2

# Connexion à ta base Render PostgreSQL
conn = psycopg2.connect(
    dbname="poubelle_db_pd0z",
    user="poubelle_db_pd0z_user",
    password="phy1gGsk1Wgrhx0TtbZOlJGnUVORGXVT",
    host="dpg-d1i4bundiees738toq1g-a.frankfurt-postgres.render.com",
    port="5432"
)

# Requête sur la table Image (ou adapte selon ton modèle SQLAlchemy)
query = "SELECT * FROM caracteristiques_image ORDER BY caracteristiques_image.id ASC;"

# Charger dans un DataFrame
df = pd.read_sql_query(query, conn)

# Exporter en CSV
df.to_csv("caracteristiques_image.csv", index=False, encoding="utf-8")

print("✅ Export terminé : images.csv")
