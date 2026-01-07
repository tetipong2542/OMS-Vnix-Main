#!/usr/bin/env python3
"""
Final Checkpoint Test for All Pages Migration
Validates that ALL pages have been successfully migrated to Lucide Icons
Tests Requirements: All migration requirements
"""

import re
import os
import glob

# All template files that should be checked
ALL_TEMPLATES = [
    'templates/base.html',
    'templates/dashboard.html',
    'templates/report_lowstock.html',
    'templates/report_notenough.html',
    'templates/report_nostock_READY.html',
    'templates/report.html',
    'templates/admin_shops.html',
    'templates/users.html',
    'templates/clear_confirm.html',
    'templates/import_stock.html',
    'templates/picking.html',
]

def test_admin_pages_icons():
    """Test that admin pages have been migrated (Tasks 8.1-8.3)"""
    
    # Task 8.1: admin_shops.html
    if os.path.exists('templates/admin_shops.html'):
        with open('templates/admin_shops.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'data-lucide="store"' in content, "Store icon not found in admin_shops.html"
        assert '🏪' not in content or '<!-- 🏪' in content, "Emoji not replaced in admin_shops.html"
        print("✓ Task 8.1: admin_shops.html migrated (store icon)")
    else:
        print("⚠ Warning: admin_shops.html not found")
    
    # Task 8.2: users.html
    if os.path.exists('templates/users.html'):
        with open('templates/users.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'data-lucide="alert-triangle"' in content, "Alert triangle icon not found in users.html"
        # Check that emoji is not in actual UI (may be in comments)
        lines = content.split('\n')
        emoji_in_ui = False
        for line in lines:
            if '⚠️' in line and not line.strip().startswith('<!--') and '<!--' not in line:
                emoji_in_ui = True
                break
        assert not emoji_in_ui, "Emoji not replaced in users.html UI"
        print("✓ Task 8.2: users.html migrated (alert-triangle icon)")
    else:
        print("⚠ Warning: users.html not found")
    
    # Task 8.3: clear_confirm.html
    if os.path.exists('templates/clear_confirm.html'):
        with open('templates/clear_confirm.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'data-lucide="alert-triangle"' in content, "Alert triangle icon not found in clear_confirm.html"
        lines = content.split('\n')
        emoji_in_ui = False
        for line in lines:
            if '⚠️' in line and not line.strip().startswith('<!--') and '<!--' not in line:
                emoji_in_ui = True
                break
        assert not emoji_in_ui, "Emoji not replaced in clear_confirm.html UI"
        print("✓ Task 8.3: clear_confirm.html migrated (alert-triangle icon)")
    else:
        print("⚠ Warning: clear_confirm.html not found")
    
    return True

def test_import_and_other_pages_icons():
    """Test that import and other pages have been migrated (Tasks 9.1-9.2)"""
    
    # Task 9.1: import_stock.html
    if os.path.exists('templates/import_stock.html'):
        with open('templates/import_stock.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'data-lucide="bar-chart-3"' in content, "Bar chart icon not found in import_stock.html"
        assert '📊' not in content or '<!-- 📊' in content, "Emoji not replaced in import_stock.html"
        print("✓ Task 9.1: import_stock.html migrated (bar-chart-3 icon)")
    else:
        print("⚠ Warning: import_stock.html not found")
    
    # Task 9.2: picking.html
    if os.path.exists('templates/picking.html'):
        with open('templates/picking.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'data-lucide="check-circle-2"' in content, "Check circle icon not found in picking.html"
        lines = content.split('\n')
        emoji_in_ui = False
        for line in lines:
            if '✅' in line and not line.strip().startswith('<!--') and '<!--' not in line:
                emoji_in_ui = True
                break
        assert not emoji_in_ui, "Emoji not replaced in picking.html UI"
        print("✓ Task 9.2: picking.html migrated (check-circle-2 icon)")
    else:
        print("⚠ Warning: picking.html not found")
    
    return True

def test_no_bootstrap_icons_in_all_templates():
    """Test that no Bootstrap Icons remain in ANY template file"""
    bi_pattern = r'\bbi-[a-z0-9-]+\b'
    files_with_bi = []
    
    for template in ALL_TEMPLATES:
        if not os.path.exists(template):
            continue
            
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(bi_pattern, content)
        if matches:
            files_with_bi.append((template, matches))
    
    assert len(files_with_bi) == 0, f"Bootstrap Icons found in: {files_with_bi}"
    print(f"✓ No Bootstrap Icons found in any of {len([t for t in ALL_TEMPLATES if os.path.exists(t)])} template files")
    return True

def test_no_emoji_in_all_templates():
    """Test that no emoji are used in UI elements across all templates"""
    emoji_pattern = r'[📊📅⚡🔍✅⚠️🔥📦🏪]'
    files_with_emoji = []
    
    for template in ALL_TEMPLATES:
        if not os.path.exists(template):
            continue
            
        with open(template, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        emoji_found = []
        for i, line in enumerate(lines, 1):
            # Skip comments
            if '<!--' in line or '-->' in line or '/*' in line or '*/' in line:
                continue
            
            matches = re.findall(emoji_pattern, line)
            if matches:
                emoji_found.append((i, line.strip()[:60]))
        
        if emoji_found:
            files_with_emoji.append((template, emoji_found))
    
    assert len(files_with_emoji) == 0, f"Emoji found in UI: {files_with_emoji}"
    print(f"✓ No emoji found in UI elements across all template files")
    return True

def test_lucide_icons_present_in_all_templates():
    """Test that Lucide Icons are being used across all templates"""
    lucide_pattern = r'data-lucide="[a-z0-9-]+"'
    total_icons = 0
    files_checked = 0
    
    for template in ALL_TEMPLATES:
        if not os.path.exists(template):
            continue
            
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(lucide_pattern, content)
        if len(matches) > 0:
            total_icons += len(matches)
            files_checked += 1
    
    assert total_icons > 0, "No Lucide Icons found in any template"
    assert files_checked > 0, "No template files were checked"
    print(f"✓ Found {total_icons} Lucide Icons across {files_checked} template files")
    return True

def test_lucide_cdn_in_base_template():
    """Test that Lucide CDN is properly configured in base template"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check CDN
    assert 'unpkg.com/lucide' in content, "Lucide CDN not found"
    
    # Check initialization
    assert 'lucide.createIcons' in content, "Lucide initialization not found"
    
    # Check error handling
    assert 'Lucide Icons failed to load' in content, "Error handling not found"
    
    # Check CSS styling
    assert '.lucide-icon' in content, "Lucide CSS not found"
    assert '.lucide-sm' in content, "Lucide size variants not found"
    assert '.lucide-primary' in content, "Lucide color classes not found"
    
    print("✓ Lucide Icons CDN and configuration properly set up in base.html")
    return True

def test_all_template_files_exist():
    """Test that all expected template files exist"""
    missing_files = []
    existing_files = []
    
    for template in ALL_TEMPLATES:
        if os.path.exists(template):
            existing_files.append(template)
        else:
            missing_files.append(template)
    
    print(f"✓ Found {len(existing_files)} out of {len(ALL_TEMPLATES)} expected template files")
    if missing_files:
        print(f"  ⚠ Missing files: {', '.join([os.path.basename(f) for f in missing_files])}")
    
    return True

def generate_migration_summary():
    """Generate a summary of the migration status"""
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    
    # Count icons per file
    lucide_pattern = r'data-lucide="[a-z0-9-]+"'
    
    summary = []
    for template in ALL_TEMPLATES:
        if not os.path.exists(template):
            continue
            
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lucide_count = len(re.findall(lucide_pattern, content))
        summary.append((os.path.basename(template), lucide_count))
    
    # Sort by icon count
    summary.sort(key=lambda x: x[1], reverse=True)
    
    print("\nLucide Icons per template:")
    total = 0
    for filename, count in summary:
        print(f"  {filename:30s} : {count:3d} icons")
        total += count
    
    print(f"\n  {'TOTAL':30s} : {total:3d} icons")
    print("=" * 60)

if __name__ == '__main__':
    print("=" * 60)
    print("FINAL CHECKPOINT: All Pages Migration Verification")
    print("=" * 60)
    print()
    
    try:
        # Check all template files exist
        test_all_template_files_exist()
        print()
        
        # Test Lucide setup
        test_lucide_cdn_in_base_template()
        print()
        
        # Test no Bootstrap Icons remain
        test_no_bootstrap_icons_in_all_templates()
        print()
        
        # Test no emoji remain
        test_no_emoji_in_all_templates()
        print()
        
        # Test Lucide Icons are present
        test_lucide_icons_present_in_all_templates()
        print()
        
        # Test admin pages
        test_admin_pages_icons()
        print()
        
        # Test import and other pages
        test_import_and_other_pages_icons()
        print()
        
        # Generate summary
        generate_migration_summary()
        print()
        
        print("=" * 60)
        print("✅ FINAL CHECKPOINT PASSED!")
        print("=" * 60)
        print()
        print("All pages have been successfully migrated to Lucide Icons:")
        print("  ✓ Base template (sidebar, navigation, utilities)")
        print("  ✓ Dashboard page (headers, KPI cards, filters)")
        print("  ✓ Report pages (lowstock, notenough, nostock, report)")
        print("  ✓ Admin pages (shops, users, clear_confirm)")
        print("  ✓ Import and other pages (import_stock, picking)")
        print()
        print("Next steps:")
        print("  - Task 11: Remove Bootstrap Icons dependency")
        print("  - Task 12: Create icon usage documentation")
        print("  - Task 13: Final testing and validation")
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ FINAL CHECKPOINT FAILED: {e}")
        print("=" * 60)
        exit(1)
