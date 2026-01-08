#!/usr/bin/env python3
"""
Checkpoint Test for Dashboard Page Migration
Validates that all dashboard icons have been successfully migrated to Lucide Icons
"""

import re

def test_no_emoji_in_dashboard():
    """Test that no emoji are used in dashboard UI elements (excluding comments)"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove CSS comments and JavaScript strings
    content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content_no_comments = re.sub(r'//.*?$', '', content_no_comments, flags=re.MULTILINE)
    
    # Search for emoji in actual UI (not in comments or strings)
    emoji_pattern = r'[📊📅⚡🔍✅⚠️🔥📦🏪]'
    
    # Split by lines and check each line
    lines = content.split('\n')
    emoji_found = []
    
    for i, line in enumerate(lines, 1):
        # Skip CSS comments
        if '/*' in line or '*/' in line:
            continue
        # Skip JavaScript strings with emoji
        if 'confirm(' in line or 'alert(' in line:
            continue
        
        matches = re.findall(emoji_pattern, line)
        if matches:
            # Check if it's in actual HTML content (not in comments)
            if not line.strip().startswith('//') and not line.strip().startswith('*'):
                emoji_found.append((i, line.strip(), matches))
    
    assert len(emoji_found) == 0, f"Found emoji in UI: {emoji_found}"
    print("✓ No emoji found in dashboard UI elements")
    return True

def test_no_bootstrap_icons_in_dashboard():
    """Test that no Bootstrap Icons remain in dashboard.html"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for Bootstrap Icons class patterns (bi-*)
    bi_pattern = r'\bbi-[a-z0-9-]+\b'
    matches = re.findall(bi_pattern, content)
    
    assert len(matches) == 0, f"Found Bootstrap Icons classes: {matches}"
    print("✓ No Bootstrap Icons classes found in dashboard.html")
    return True

def test_lucide_icons_in_dashboard():
    """Test that Lucide Icons are being used in dashboard"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for data-lucide attributes
    lucide_pattern = r'data-lucide="[a-z0-9-]+"'
    matches = re.findall(lucide_pattern, content)
    
    assert len(matches) > 0, "No Lucide Icons found in dashboard.html"
    print(f"✓ Found {len(matches)} Lucide Icons in dashboard.html")
    
    # Verify specific icons that should be present based on tasks 4.1-4.4
    expected_icons = [
        # Task 4.1: Dashboard header icons
        'bar-chart-3',  # 📊
        'calendar',     # 📅
        'zap',          # ⚡
        'search',       # 🔍
        
        # Task 4.2: KPI card icons
        'inbox',            # รวมงานค้าง
        'check-circle',     # กอง 1
        'alert-triangle',   # กอง 2
        'octagon-x',        # กอง 3
        'file-x',           # ยังไม่ได้แพ็ค
        'cloud-off',        # ยังไม่นำเข้า SBS
        'scan-barcode',     # รอ Scan
        'send',             # จ่ายงานแล้ว
        'package',          # แพ็คแล้ว
        'layers',           # คลังรับงาน
        'clipboard-check',  # กอง 1 คลัง
        
        # Task 4.3: Section label icons
        'flame',            # 🔥 งานค้าง
        'flag',             # งานจบวันนี้
        
        # Task 4.4: Filter and action icons
        'filter',
        'x-circle',
        'arrow-left',
        'calendar-check',
    ]
    
    missing_icons = []
    for icon in expected_icons:
        if f'data-lucide="{icon}"' not in content:
            missing_icons.append(icon)
    
    assert len(missing_icons) == 0, f"Expected icons not found: {missing_icons}"
    print(f"✓ All {len(expected_icons)} expected dashboard icons are present")
    return True

def test_dashboard_icon_migration_completeness():
    """Test that all icon migrations from tasks 4.1-4.4 are complete"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Task 4.1: Dashboard header icons (4 icons)
    header_icons = ['bar-chart-3', 'calendar', 'zap', 'search']
    for icon in header_icons:
        assert f'data-lucide="{icon}"' in content, f"Header icon '{icon}' not migrated"
    print(f"✓ Task 4.1: All {len(header_icons)} dashboard header icons migrated")
    
    # Task 4.2: KPI card icons (11 icons)
    kpi_icons = ['inbox', 'check-circle', 'alert-triangle', 'octagon-x', 
                 'file-x', 'cloud-off', 'scan-barcode', 'send', 
                 'package', 'layers', 'clipboard-check']
    for icon in kpi_icons:
        assert f'data-lucide="{icon}"' in content, f"KPI icon '{icon}' not migrated"
    print(f"✓ Task 4.2: All {len(kpi_icons)} KPI card icons migrated")
    
    # Task 4.3: Section label icons (2 icons)
    section_icons = ['flame', 'flag']
    for icon in section_icons:
        assert f'data-lucide="{icon}"' in content, f"Section icon '{icon}' not migrated"
    print(f"✓ Task 4.3: All {len(section_icons)} section label icons migrated")
    
    # Task 4.4: Filter and action icons (5 icons)
    filter_icons = ['filter', 'x-circle', 'arrow-left', 'calendar-check', 'search']
    for icon in filter_icons:
        assert f'data-lucide="{icon}"' in content, f"Filter icon '{icon}' not migrated"
    print(f"✓ Task 4.4: All {len(filter_icons)} filter and action icons migrated")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CHECKPOINT: Dashboard Page Migration Verification")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        test_no_bootstrap_icons_in_dashboard()
        print()
        
        test_no_emoji_in_dashboard()
        print()
        
        test_lucide_icons_in_dashboard()
        print()
        
        test_dashboard_icon_migration_completeness()
        print()
        
        print("=" * 60)
        print("✅ CHECKPOINT PASSED: All dashboard tests passed!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Task 4.1: Dashboard header icons migrated")
        print("  ✓ Task 4.2: KPI card icons migrated")
        print("  ✓ Task 4.3: Section label icons migrated")
        print("  ✓ Task 4.4: Filter and action icons migrated")
        print()
        print("Ready to proceed to Task 6: Migrate Report Pages")
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ CHECKPOINT FAILED: {e}")
        print("=" * 60)
        exit(1)
