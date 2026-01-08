#!/bin/bash

INPUT="$1"
OUTPUT="$2"

echo "======================================================================"
echo "🔧 Safe Database Conversion for Turso (Dump & Restore Method)"
echo "======================================================================"

if [ ! -f "$INPUT" ]; then
    echo "❌ Error: Input file '$INPUT' not found!"
    exit 1
fi

echo ""
echo "📁 Input file: $INPUT"
ls -lh "$INPUT"

# Clean up old files
rm -f "$OUTPUT" "$OUTPUT-shm" "$OUTPUT-wal" "${OUTPUT}.sql"

echo ""
echo "----------------------------------------------------------------------"
echo "🔍 Step 1: Checking source database integrity..."
echo "----------------------------------------------------------------------"
INTEGRITY=$(sqlite3 "$INPUT" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "❌ Source database integrity check failed: $INTEGRITY"
    exit 1
fi
echo "✓ Source integrity check: OK"

echo ""
echo "----------------------------------------------------------------------"
echo "💾 Step 2: Dumping database to SQL..."
echo "----------------------------------------------------------------------"
echo "This may take 30-60 seconds for large databases..."
sqlite3 "$INPUT" ".dump" > "${OUTPUT}.sql"
DUMP_SIZE=$(ls -lh "${OUTPUT}.sql" | awk '{print $5}')
echo "✓ SQL dump created: ${OUTPUT}.sql (${DUMP_SIZE})"

echo ""
echo "----------------------------------------------------------------------"
echo "🔨 Step 3: Creating new clean database from dump..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" < "${OUTPUT}.sql"
echo "✓ Database restored from SQL dump"

echo ""
echo "----------------------------------------------------------------------"
echo "🔄 Step 4: Converting to WAL mode..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" "PRAGMA journal_mode=WAL;"
NEW_MODE=$(sqlite3 "$OUTPUT" "PRAGMA journal_mode;")
echo "✓ Converted to: $NEW_MODE"

echo ""
echo "----------------------------------------------------------------------"
echo "📦 Step 5: Checkpointing WAL..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" "PRAGMA wal_checkpoint(TRUNCATE);"
echo "✓ Checkpoint completed"

echo ""
echo "----------------------------------------------------------------------"
echo "🧹 Step 6: Vacuuming database..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" "VACUUM;"
echo "✓ Database vacuumed successfully"

echo ""
echo "----------------------------------------------------------------------"
echo "✅ Step 7: Final verification..."
echo "----------------------------------------------------------------------"
FINAL_CHECK=$(sqlite3 "$OUTPUT" "PRAGMA integrity_check;")
if [ "$FINAL_CHECK" != "ok" ]; then
    echo "❌ Final integrity check failed: $FINAL_CHECK"
    rm -f "$OUTPUT"
    exit 1
fi
echo "✓ Final integrity check: OK"

TABLE_COUNT=$(sqlite3 "$OUTPUT" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
echo "✓ Tables: $TABLE_COUNT"

# Clean up SQL dump
echo ""
echo "Cleaning up temporary files..."
rm -f "${OUTPUT}.sql"
echo "✓ Temporary files removed"

echo ""
echo "======================================================================"
echo "✅ Safe Conversion completed successfully!"
echo "======================================================================"
echo ""
echo "📁 Output file: $OUTPUT"
ls -lh "$OUTPUT"

echo ""
echo "======================================================================"
echo "🚀 Next Steps:"
echo "======================================================================"
echo "1. Go to https://vnix-erp.up.railway.app/system-status"
echo "2. Find the Turso database you want to replace"
echo "3. Click 'Upload & Sync to Turso'"
echo "4. Select the converted file: $OUTPUT"
echo "5. Wait for upload and sync to complete"
echo ""
echo "⚠️  WARNING: This will REPLACE all data in Turso Cloud!"
echo "======================================================================"
