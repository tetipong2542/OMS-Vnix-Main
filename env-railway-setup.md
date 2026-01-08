# Railway Environment Variables Setup
# Copy ค่าเหล่านี้ไปที่ Railway Dashboard → Settings → Variables

# ==============================================================================
# TURSO DATABASE CONFIGURATION (3 Separate Databases)
# ==============================================================================

# ==== DATA DB (Main Database) ====
DATA_DB_URL=libsql://data-tetipong2542.aws-ap-northeast-1.turso.io
DATA_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzMDksImlkIjoiMTY3YTExNDUtZGM0NC00MzIwLTk0MmMtMDM3ZjFiNTRjZjgxIiwicmlkIjoiZWE0ZjEzN2EtYTI0ZS00N2YyLWIxOWEtMWZjNTIzYmE2Y2JjIn0.hocKljFNemkcyZ4lYeYD7FUD3hMlDIEo-Xj0kpbCsEzOwe4h1EKHh0j68IjuOWwYZQ5IutCbIekP6B2Lqn9gBQ
DATA_DB_LOCAL=/data/data.db

# ==== PRICE DB (Pricing Database) ====
PRICE_DB_URL=libsql://price-tetipong2542.aws-ap-northeast-1.turso.io
PRICE_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzNzUsImlkIjoiZDhlNWZiYjktOWI3YS00YzU1LWIxMWMtODNhOTBiYjNiZGUwIiwicmlkIjoiMDhhOWRlNzAtNjI4Ny00MzQ5LWE1M2MtYzYxZTI1Mjc4Y2UxIn0.hgTCaKN3iFx--UuYvmUR6T9YP5iWDkY2NNFLe5BBY382ZOWaSnv6M-cz7hP51OWTWTv1Hu2S4sJZS2RZMTg7AQ
PRICE_DB_LOCAL=/data/price.db

# ==== SUPPLIER DB (Supplier & Stock Database) ====
SUPPLIER_DB_URL=libsql://supplier-stock-tetipong2542.aws-ap-northeast-1.turso.io
SUPPLIER_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzODksImlkIjoiODBkYTFlZmItZmM1Ni00OGQ3LWEwMzctODgyMWI3NGRhZTcwIiwicmlkIjoiMzA4M2VmMDUtZDM0NS00YWY1LWJlZTQtYjQ3OGZlNjcyMTk5In0.tF_3StAUdbz0wxuGgGl6XZe1TFvFL2N2XGZ01YNB5YODkWfvMC2Iz_UiNfCKf69v_lyuRwwz1LKyTRCJA-CTBw
SUPPLIER_DB_LOCAL=/data/supplier_stock.db

# ==== Railway Volume ====
RAILWAY_VOLUME_MOUNT_PATH=/data

# ==============================================================================
# GOOGLE SHEETS INTEGRATION (Optional)
# ==============================================================================
GOOGLE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
GOOGLE_CLIENT_EMAIL=vnix-sheet-importer@vnix-oms.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=116721842382656499585
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDNaBfT19Jfva7a
pakNfdccVCnmIKSDFDfR/u+rt8cfWObZt9VJbRWDMc2lEd5l2VYkVq3NTq4yjlxw
91ng/+qKtYM0cp+TnT8G739sC6nr36A7KQp0ViZud87KSaFGpoqVFPjHlNhZrSK6
F0P2Oc2l0hAQvQRqSaFtCeeRSgevgTxaLbde6nFloxUE7bUcx3uj8p9zdYAwM+dC
DEbWECuGPmVI/tiCOT9HcdFZigr0/n6G5OQLJOjWT79wwRf1tTddefONfqroS6jh
M7SWlFAkhZvLRp5iJMaLtfKfT+5+P+bDLmoXVYbZRSd2U5ITPo8UzCBkhKHWoYka
3CiZ3qe1AgMBAAECggEAUUWG6/xgUh5gkUVroplwY9aPL20p+m0k+vM2TEiuQiJw
UKOSgfdlxB+QAOiViNHZ6g3bvbiMZxd5zv6ncsV/PPu9mqJhrkvQ1MMtNQhWZqv4
H4BJESfHE/1WdiZ059ncSkled8VWZwEAlQXAj6tmSV5Yme7X0OAqPVTmaU+Tw+YV
l/ATRlbW02S8qJGIZrstE6MwVKxczk6fukgY883R91ZDZOKxZbeIwXhIlvMYumI6
qyqWrFsKG8Y6Uj4vW8+Ef4yAZWV35LzUxHQ8ebclm6Jz/5WXx2Iq6s+9sSPkavnn
7llDLrCVO9e4HmUsq0fYghKulczsF9xltGfvXa/uTwKBgQD+NuOpUYUR6o2zajlp
raHquvzmtB0s+eD4Dn7CK0qGP5wzaiwYeEpQUTgB+1ZBbyaYIQ7ZsJsX41o7RJs9
yHtO+9CJI9tn+m+wRE80nDxWzT14kTu5KXZaDGIPEkoIIHTrn1/6KE0QShAcqFlZ
63TqLXby/jtCsZkeHqtVGcgNGwKBgQDO2XDkMY7YjOmnvueuelTh0oCLdWDFblEZ
BbxuJNLY88LcW58HsI7Qi2J/xzWzYkNcs5b3YlXm26qY+WSe8kYF8viHpC2m4vj6
BFJ+3N92KqcAZqVT+MqtEups5hyvZHVm2092EepCQqVlpo7y1zpB5cuw0/Xri1PM
j/Yqb897bwKBgQDg0N4JUWSjcZEbSCe6A6ocEn2x8TuUGPARr4/+W5aunvaeqZiR
k1/1I76qUgH4IDo7c5DUh9DBEXkszQGVZAVY1m2XurRAgkPf2KlLV5gtE5j3VUlB
+R8Hh8f4mC4MfdeowOt6KcXtT/JrxZ4vXYGpz8dQIfF6i+Fjt6/BtOksXQKBgQCs
bkbVcxqJGq6Mz2+C2yd3OGs/1hFdg6DHIyj5CGlbwZhm6Vmgp2XmIstxiTcS2o8c
7/ihMLA7SlLkQsHGXmBRBUJ4kDweKocyo/fBGY6Oiu+8PdUEMxmBPYt+TDUNYMkd
fSS4YCbQJY6LNlVjylceJ9mtBoSyXer1U+z5Y0uqsQKBgQCm1UWGLHr7FD65PDFk
IBXi/5XaHQmR1v/dTbqyk4KDT1azGpfjwPF1quFYxzTBIUofDgWRZInCuRStYmqX
bdzwDCs6MwG15rqdgTBGa7w7kexLklHMKB2s+CLuWLRBxt1g6apLVMOpPHOKlpni
mfVe0NXx5FDEevHcgZZZPK0AqQ==
-----END PRIVATE KEY-----
GOOGLE_PRIVATE_KEY_ID=da922b3018874afa6e4ff8a28ebc550e6c8345b0
GOOGLE_PROJECT_ID=vnix-oms
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# ==============================================================================
# IMPORTANT NOTES
# ==============================================================================
#
# 1. ใช้ /data/xxx.db สำหรับ Railway (ไม่ใช่ xxx.db)
# 2. ต้องมี Railway Volume mount ที่ /data
# 3. Tokens ที่สร้างด้วย "turso db tokens create" จะเป็น rw (read-write)
# 4. หลังตั้งค่า Environment Variables แล้ว ต้อง Redeploy Railway
#
# ==============================================================================