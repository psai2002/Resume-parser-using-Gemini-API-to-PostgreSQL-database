from pypdf import PdfReader
import pandas as pd
import requests
import google.generativeai as genai
import os
import json
import psycopg2
from sqlalchemy import create_engine
from tabulate import tabulate

conn_string = "postgresql://postgres:postgres@localhost/newdb"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

pdf_file = 'Resume.pdf'
text = ''
with open(pdf_file, 'rb') as file:
	reader = PdfReader(file)
	for page in reader.pages:
		text += page.extract_text() + '\n'

model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config={"response_mime_type":"application/json"})
response = model.generate_content(f"from {text} extract name, email, phone, college, skills. in skills remove colon. in skills remove text before colon. give json data.")

data = response.text
dictionary = json.loads(data)
df = pd.DataFrame([dictionary])
print(df)

db = create_engine(conn_string)
conn = db.connect()
df.to_sql('candidate',
	con=conn,
	if_exists='append',
	index=False,
)
conn = psycopg2.connect(conn_string)
print("Connected to database.")

conn.autocommit = True
cur = conn.cursor()
sql = 'select * from candidate'
cur.execute(sql)
for i in cur.fetchall():
	print(i, '\n')

cur.close()
conn.close()
