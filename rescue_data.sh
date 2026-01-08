#!/bin/bash

INPUT="$1"
OUTPUT="$2"

echo "======================================================================"
echo "🚑 Data Recovery & Fresh Database Creation"
echo "======================================================================"

if [ ! -f "$INPUT" ]; then
    echo "❌ Error: Input file '$INPUT' not found!"
    exit 1
fi

echo ""
echo "📁 Source file: $INPUT"
ls -lh "$INPUT"

# Clean up
rm -f "$OUTPUT" "$OUTPUT-shm" "$OUTPUT-wal" "${OUTPUT}.sql"

echo ""
echo "----------------------------------------------------------------------"
echo "🔍 Step 1: Analyzing source database..."
echo "----------------------------------------------------------------------"

# Get table list
echo "Getting table list..."
TABLES=$(sqlite3 "$INPUT" "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;" 2>/dev/null)

if [ -z "$TABLES" ]; then
    echo "❌ Error: Could not read tables from source database!"
    exit 1
fi

echo "✓ Found tables:"
echo "$TABLES" | while read table; do echo "  - $table"; done

echo ""
echo "----------------------------------------------------------------------"
echo "💾 Step 2: Recovering data from tables..."
echo "----------------------------------------------------------------------"

# Create fresh database with WAL mode first
echo "Creating fresh database..."
sqlite3 "$OUTPUT" "PRAGMA journal_mode=WAL;"
echo "✓ Fresh database created in WAL mode"

# Recover data table by table
echo ""
echo "Recovering data from each table..."

RECOVERED=0
FAILED=0

echo "$TABLES" | while read table; do
    if [ -n "$table" ]; then
        echo -n "  Processing: $table ... "
        
        # Try to get schema
        SCHEMA=$(sqlite3 "$INPUT" ".schema $table" 2>/dev/null)
        
        if [ $? -eq 0 ] && [ -n "$SCHEMA" ]; then
            # Create table in new database
            echo "$SCHEMA" | sqlite3 "$OUTPUT" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                # Try to copy data
                sqlite3 "$INPUT" ".mode insert $table" ".output /tmp/recover_${table}.sql" "SELECT * FROM $table;" 2>/dev/null
                
                if [ -f "/tmp/recover_${table}.sql" ]; then
                    sqlite3 "$OUTPUT" < "/tmp/recover_${table}.sql" 2>/dev/null
                    
                    if [ $? -eq 0 ]; then
                        COUNT=$(sqlite3 "$OUTPUT" "SELECT COUNT(*) FROM $table;" 2>/dev/null)
                        echo "✓ ($COUNT rows)"
                        RECOVERED=$((RECOVERED + 1))
                    else
                        echo "⚠ Schema OK, data copy failed"
                        FAILED=$((FAILED + 1))
                    fi
                    rm -f "/tmp/recover_${table}.sql"
                else
                    echo "⚠ Could not extract data"
                    FAILED=$((FAILED + 1))
                fi
            else
                echo "⚠ Schema creation failed"
                FAILED=$((FAILED + 1))
            fi
        else
            echo "⚠ Could not read schema"
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo ""
echo "----------------------------------------------------------------------"
echo "🔄 Step 3: Optimizing recovered database..."
echo "----------------------------------------------------------------------"

sqlite3 "$OUTPUT" "PRAGMA wal_checkpoint(TRUNCATE);"
echo "✓ WAL checkpoint completed"

sqlite3 "$OUTPUT" "VACUUM;"
echo "✓ Database vacuumed"

echo ""
echo "----------------------------------------------------------------------"
echo "✅ Step 4: Verifying recovered database..."
echo "----------------------------------------------------------------------"

INTEGRITY=$(sqlite3 "$OUTPUT" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "❌ Integrity check failed: $INTEGRITY"
    exit 1
fi
echo "✓ Integrity check: OK"

MODE=$(sqlite3 "$OUTPUT" "PRAGMA journal_mode;")
echo "✓ Journal mode: $MODE"

TABLE_COUNT=$(sqlite3 "$OUTPUT" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
echo "✓ Tables recovered: $TABLE_COUNT"

echo ""
echo "======================================================================"
echo "✅ Data Recovery Completed!"
echo "======================================================================"
echo ""
echo "📁 Output file: $OUTPUT"
ls -lh "$OUTPUT"

echo ""
echo "======================================================================"
echo "📊 Recovery Summary:"
echo "======================================================================"
echo "Tables in source: $(echo "$TABLES" | wc -l | tr -d ' ')"
echo "Tables recovered: $TABLE_COUNT"
echo ""

# Show row counts for important tables
echo "Row counts in recovered database:"
for table in products orders users shops; do
    COUNT=$(sqlite3 "$OUTPUT" "SELECT COUNT(*) FROM $table;" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "  - $table: $COUNT rows"
    fi
done

echo ""
echo "======================================================================"
echo "🚀 Next Steps:"
echo "======================================================================"
echo "1. Verify the data in $OUTPUT looks correct"
echo "2. Go to https://vnix-erp.up.railway.app/system-status"
echo "3. Click 'Upload & Sync to Turso'"
echo "4. Select: $OUTPUT"
echo "======================================================================"

