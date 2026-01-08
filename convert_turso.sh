#!/bin/bash

INPUT="$1"
OUTPUT="$2"

echo "======================================================================"
echo "🔧 Converting SQLite Database for Turso"
echo "======================================================================"

if [ ! -f "$INPUT" ]; then
    echo "❌ Error: Input file '$INPUT' not found!"
    exit 1
fi

echo ""
echo "📁 Input file: $INPUT"
ls -lh "$INPUT"

echo ""
echo "📋 Creating clean copy..."
rm -f "$OUTPUT" "$OUTPUT-shm" "$OUTPUT-wal"
sqlite3 "$INPUT" ".backup $OUTPUT"
echo "✓ File copied successfully"

echo ""
echo "----------------------------------------------------------------------"
echo "🔍 Step 1: Checking database integrity..."
echo "----------------------------------------------------------------------"
INTEGRITY=$(sqlite3 "$OUTPUT" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "❌ Database integrity check failed: $INTEGRITY"
    rm -f "$OUTPUT"
    exit 1
fi
echo "✓ Integrity check: OK"

echo ""
echo "----------------------------------------------------------------------"
echo "🔄 Step 2: Converting to WAL mode..."
echo "----------------------------------------------------------------------"
CURRENT_MODE=$(sqlite3 "$OUTPUT" "PRAGMA journal_mode;")
echo "Current mode: $CURRENT_MODE"

sqlite3 "$OUTPUT" "PRAGMA journal_mode=WAL;"
NEW_MODE=$(sqlite3 "$OUTPUT" "PRAGMA journal_mode;")
echo "✓ Converted to: $NEW_MODE"

echo ""
echo "----------------------------------------------------------------------"
echo "📦 Step 3: Checkpointing WAL..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" "PRAGMA wal_checkpoint(TRUNCATE);"
echo "✓ Checkpoint completed"

echo ""
echo "----------------------------------------------------------------------"
echo "🧹 Step 4: Vacuuming database..."
echo "----------------------------------------------------------------------"
sqlite3 "$OUTPUT" "VACUUM;"
echo "✓ Database vacuumed successfully"

echo ""
echo "----------------------------------------------------------------------"
echo "✅ Step 5: Final verification..."
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

echo ""
echo "======================================================================"
echo "✅ Conversion completed successfully!"
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
