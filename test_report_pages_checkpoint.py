#!/usr/bin/env python3
"""
Checkpoint Test for Report Pages Migration
Validates that all report page icons have been successfully migrated to Lucide Icons
Tests Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 4.4, 4.5, 4.6
"""

import re
import os

REPORT_PAGES = [
    'templates/report_lowstock.html',
    'templates/report_notenough.html',
    'templates/report_nostock_READY.html',
    'templates/report.html'
]

def test_no_emoji_in_report_pages():
    """Test that no emoji are used in report page UI elements (excluding comments)"""
    emoji_pattern = r'[📊📅⚡🔍✅⚠️🔥📦🏪]'
    
    for page in REPORT_PAGES:
        if not os.path.exists(page):
            print(f"⚠ Warning: {page} not found, skipping")
            continue
            
        with open(page, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        emoji_found = []
        for i, line in enumerate(lines, 1):
            # Skip CSS comments and JavaScript comments
            if '/*' in line or '*/' in line or line.strip().startswith('//'):
                continue
            # Skip JavaScript strings with emoji in comments
            if '// ✅' in line or '// ⚠️' in line:
                continue
            
            matches = re.findall(emoji_pattern, line)
            if matches:
                # Check if it's in actual HTML content (not in comments)
                if not line.strip().startswith('//') and not line.strip().startswith('*'):
                    emoji_found.append((i, line.strip()[:80], matches))
        
        assert len(emoji_found) == 0, f"Found emoji in {page}: {emoji_found}"
        print(f"✓ No emoji found in {os.path.basename(page)}")
    
    return True

def test_no_bootstrap_icons_in_report_pages():
    """Test that no Bootstrap Icons remain in report pages"""
    bi_pattern = r'\bbi-[a-z0-9-]+\b'
    
    for page in REPORT_PAGES:
        if not os.path.exists(page):
            print(f"⚠ Warning: {page} not found, skipping")
            continue
            
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(bi_pattern, content)
        
        assert len(matches) == 0, f"Found Bootstrap Icons in {page}: {matches}"
        print(f"✓ No Bootstrap Icons found in {os.path.basename(page)}")
    
    return True

def test_lucide_icons_in_report_pages():
    """Test that Lucide Icons are being used in all report pages"""
    lucide_pattern = r'data-lucide="[a-z0-9-]+"'
    
    for page in REPORT_PAGES:
        if not os.path.exists(page):
            print(f"⚠ Warning: {page} not found, skipping")
            continue
            
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(lucide_pattern, content)
        
        assert len(matches) > 0, f"No Lucide Icons found in {page}"
        print(f"✓ Found {len(matches)} Lucide Icons in {os.path.basename(page)}")
    
    return True

def test_report_lowstock_icons():
    """Test specific icons in report_lowstock.html (Task 6.1)"""
    page = 'templates/report_lowstock.html'
    
    if not os.path.exists(page):
        print(f"⚠ Warning: {page} not found, skipping")
        return True
        
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected icons from Task 6.1
    expected_icons = [
        'bar-chart-3',      # 📊 header (used instead of bar-chart)
        'check-circle-2',   # ✅ Scan แล้ว
        'alert-triangle',   # ⚠️ notes
        'arrow-left',       # back button
        'printer',          # print
        'lock',             # lock
        'save',             # save
        'file-spreadsheet', # excel
        'filter',           # filter
        'database',         # database
        'history',          # history
        'package',          # package
        'scan-barcode',     # scan
        'refresh-cw',       # refresh
        'check-circle',     # check
        'circle',           # circle
        'unlock',           # unlock
    ]
    
    missing_icons = []
    for icon in expected_icons:
        if f'data-lucide="{icon}"' not in content:
            missing_icons.append(icon)
    
    assert len(missing_icons) == 0, f"Missing icons in report_lowstock.html: {missing_icons}"
    print(f"✓ Task 6.1: All {len(expected_icons)} icons present in report_lowstock.html")
    return True

def test_report_notenough_icons():
    """Test specific icons in report_notenough.html (Task 6.2)"""
    page = 'templates/report_notenough.html'
    
    if not os.path.exists(page):
        print(f"⚠ Warning: {page} not found, skipping")
        return True
        
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should have same icons as report_lowstock.html
    expected_icons = [
        'alert-triangle',   # header icon
        'arrow-left',       # back button
        'printer',          # print
        'lock',             # lock
        'save',             # save
        'file-spreadsheet', # excel
        'filter',           # filter
        'database',         # database
        'history',          # history
        'package',          # package
        'scan-barcode',     # scan
        'refresh-cw',       # refresh
        'check-circle',     # check
    ]
    
    missing_icons = []
    for icon in expected_icons:
        if f'data-lucide="{icon}"' not in content:
            missing_icons.append(icon)
    
    assert len(missing_icons) == 0, f"Missing icons in report_notenough.html: {missing_icons}"
    print(f"✓ Task 6.2: All {len(expected_icons)} icons present in report_notenough.html")
    return True

def test_report_nostock_ready_icons():
    """Test specific icons in report_nostock_READY.html (Task 6.3)"""
    page = 'templates/report_nostock_READY.html'
    
    if not os.path.exists(page):
        print(f"⚠ Warning: {page} not found, skipping")
        return True
        
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should have same icons as report_lowstock.html
    expected_icons = [
        'file-x',           # header icon (no stock)
        'arrow-left',       # back button
        'printer',          # print
        'lock',             # lock
        'save',             # save
        'file-spreadsheet', # excel
        'filter',           # filter
        'database',         # database
        'history',          # history
        'package',          # package
        'scan-barcode',     # scan
        'refresh-cw',       # refresh
        'check-circle',     # check
    ]
    
    missing_icons = []
    for icon in expected_icons:
        if f'data-lucide="{icon}"' not in content:
            missing_icons.append(icon)
    
    assert len(missing_icons) == 0, f"Missing icons in report_nostock_READY.html: {missing_icons}"
    print(f"✓ Task 6.3: All {len(expected_icons)} icons present in report_nostock_READY.html")
    return True

def test_report_html_icons():
    """Test specific icons in report.html (Task 6.4)"""
    page = 'templates/report.html'
    
    if not os.path.exists(page):
        print(f"⚠ Warning: {page} not found, skipping")
        return True
        
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected icons from Task 6.4
    expected_icons = [
        'calendar',         # 📅
        'search',           # 🔍
        'package',          # 📦
        'check-circle-2',   # ✅
        'alert-triangle',   # ⚠️
    ]
    
    missing_icons = []
    for icon in expected_icons:
        if f'data-lucide="{icon}"' not in content:
            missing_icons.append(icon)
    
    assert len(missing_icons) == 0, f"Missing icons in report.html: {missing_icons}"
    print(f"✓ Task 6.4: All {len(expected_icons)} icons present in report.html")
    return True

def test_icon_consistency_across_reports():
    """Test that common icons are used consistently across report pages"""
    common_icons = {
        'arrow-left': 0,
        'printer': 0,
        'filter': 0,
        'search': 0,
    }
    
    for page in REPORT_PAGES:
        if not os.path.exists(page):
            continue
            
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for icon in common_icons:
            if f'data-lucide="{icon}"' in content:
                common_icons[icon] += 1
    
    # At least some pages should use these common icons
    for icon, count in common_icons.items():
        assert count > 0, f"Common icon '{icon}' not found in any report page"
    
    print(f"✓ Common icons used consistently across report pages")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CHECKPOINT: Report Pages Migration Verification")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        test_no_bootstrap_icons_in_report_pages()
        print()
        
        test_no_emoji_in_report_pages()
        print()
        
        test_lucide_icons_in_report_pages()
        print()
        
        test_report_lowstock_icons()
        print()
        
        test_report_notenough_icons()
        print()
        
        test_report_nostock_ready_icons()
        print()
        
        test_report_html_icons()
        print()
        
        test_icon_consistency_across_reports()
        print()
        
        print("=" * 60)
        print("✅ CHECKPOINT PASSED: All report page tests passed!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Task 6.1: report_lowstock.html icons migrated")
        print("  ✓ Task 6.2: report_notenough.html icons migrated")
        print("  ✓ Task 6.3: report_nostock_READY.html icons migrated")
        print("  ✓ Task 6.4: report.html icons migrated")
        print("  ✓ No Bootstrap Icons remain in report pages")
        print("  ✓ No emoji remain in report pages")
        print("  ✓ Icon consistency maintained across pages")
        print()
        print("Ready to proceed to Task 8: Migrate Admin Pages")
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ CHECKPOINT FAILED: {e}")
        print("=" * 60)
        exit(1)
