#!/usr/bin/env python3
"""
Script to upload SQLite database dumps to Turso (libSQL)
Usage: python3 upload_to_turso.py
"""

import asyncio
import libsql_client

# Turso connection details
TURSO_DB_URL = "libsql://vnix-erp-tetipong2542.aws-ap-northeast-1.turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc3ODEyNTgsImlkIjoiNmU3MjkxNmEtYmMwMC00Mzg2LTg2Y2EtMzcxMTg3YjhlOWI0IiwicmlkIjoiMjdmOTg0N2EtZWIxYy00OTZjLWIyYzgtZWU3NzczODgzMjk3In0.xL8bAxMtu1UdEeQWrF2MFVCP1qTsZZAYcMK4RA8X_U6tskVi4ao2wS8MNiNEXWCyFFVMNr6e2LKcyoFODwRbBg"

async def upload_database(sql_dump_file: str):
    """Upload a SQL dump file to Turso"""
    print(f"\n{'='*60}")
    print(f"Uploading: {sql_dump_file}")
    print(f"{'='*60}\n")

    # Create client
    client = libsql_client.create_client(
        url=TURSO_DB_URL,
        auth_token=TURSO_AUTH_TOKEN
    )

    try:
        # Read SQL dump file
        with open(sql_dump_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"📄 File size: {len(sql_content)} characters")

        # Split SQL statements (simple approach - split by semicolon)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        print(f"📊 Found {len(statements)} SQL statements")

        # Execute statements in batches
        batch_size = 100
        executed = 0
        errors = 0

        for i in range(0, len(statements), batch_size):
            batch = statements[i:i+batch_size]

            for stmt in batch:
                if not stmt or stmt.startswith('--'):
                    continue

                try:
                    await client.execute(stmt)
                    executed += 1

                    # Show progress every 100 statements
                    if executed % 100 == 0:
                        print(f"   ✓ Executed {executed}/{len(statements)} statements...")

                except Exception as e:
                    errors += 1
                    # Only show first few errors to avoid spam
                    if errors <= 5:
                        print(f"   ⚠️  Error (statement {executed + 1}): {str(e)[:100]}")
                    elif errors == 6:
                        print(f"   ⚠️  Too many errors, suppressing further error messages...")

        print(f"\n✅ Upload complete!")
        print(f"   - Executed: {executed} statements")
        print(f"   - Errors: {errors} statements")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise
    finally:
        await client.close()


async def main():
    """Main function to upload all databases"""
    print("\n" + "="*60)
    print("  Turso Database Upload Tool")
    print("="*60)
    print(f"Target: {TURSO_DB_URL}")
    print("="*60)

    # Upload databases one by one
    databases = [
        'data_dump.sql',
        'price_dump.sql',
        'supplier_stock_dump.sql'
    ]

    for db_file in databases:
        try:
            await upload_database(db_file)
            print(f"\n✅ Successfully uploaded {db_file}")
        except Exception as e:
            print(f"\n❌ Failed to upload {db_file}: {e}")
            user_input = input("\nContinue with next database? (y/n): ")
            if user_input.lower() != 'y':
                break

    print("\n" + "="*60)
    print("  Upload Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
