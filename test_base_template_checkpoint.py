#!/usr/bin/env python3
"""
Checkpoint Test for Base Template Migration
Validates that all base template icons have been successfully migrated to Lucide Icons
"""

import re

def test_no_bootstrap_icons():
    """Test that no Bootstrap Icons remain in base.html"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for Bootstrap Icons class patterns (bi-*)
    bi_pattern = r'\bbi-[a-z0-9-]+\b'
    matches = re.findall(bi_pattern, content)
    
    # Filter out matches in comments
    actual_matches = []
    for match in matches:
        # Check if it's in a comment
        if f'<!-- {match}' not in content and f'* {match}' not in content:
            actual_matches.append(match)
    
    assert len(actual_matches) == 0, f"Found Bootstrap Icons classes: {actual_matches}"
    print("✓ No Bootstrap Icons classes found in base.html")
    return True

def test_no_emoji_in_ui():
    """Test that no emoji are used in UI elements (excluding comments)"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    emoji_pattern = r'[📊📅⚡🔍✅⚠️🔥📦🏪]'
    emoji_found = []
    
    for i, line in enumerate(lines, 1):
        # Skip CSS comments
        if '/*' in line or '*/' in line or line.strip().startswith('//'):
            continue
        
        matches = re.findall(emoji_pattern, line)
        if matches:
            emoji_found.append((i, line.strip(), matches))
    
    assert len(emoji_found) == 0, f"Found emoji in UI: {emoji_found}"
    print("✓ No emoji found in UI elements")
    return True

def test_lucide_icons_present():
    """Test that Lucide Icons are being used"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for data-lucide attributes
    lucide_pattern = r'data-lucide="[a-z0-9-]+"'
    matches = re.findall(lucide_pattern, content)
    
    assert len(matches) > 0, "No Lucide Icons found in base.html"
    print(f"✓ Found {len(matches)} Lucide Icons in base.html")
    
    # Verify specific icons that should be present
    expected_icons = [
        'package',      # Brand logo
        'globe',        # แผนก Online
        'shopping-bag', # แผนก Sale
        'shopping-cart',# แผนก จัดซื้อ
        'headphones',   # แผนก Helpdesk
        'boxes',        # แผนก คลังสินค้า
        'calculator',   # แผนก บัญชี
        'users',        # แผนก HR
        'settings',     # ตั้งค่าระบบ
        'gauge',        # Dashboard
        'trending-up',  # ราคาตลาด
        'cloud-upload', # นำเข้าข้อมูล
        'shield',       # ผู้ดูแลระบบ
        'trash-2',      # ล้างข้อมูล
        'clock',        # Current Time
        'log-out',      # ออกจากระบบ
        'info',         # Flash messages
        'menu',         # Menu toggle
        'layout-grid',  # App name icon
        'more-vertical',# Mobile menu
        'x',            # Close sidebar
        'chevron-down', # Dropdown arrows
        'chevron-right',# Submenu arrows
    ]
    
    for icon in expected_icons:
        assert f'data-lucide="{icon}"' in content, f"Expected icon '{icon}' not found"
    
    print(f"✓ All {len(expected_icons)} expected icons are present")
    return True

def test_lucide_cdn_and_init():
    """Test that Lucide CDN and initialization are present"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check CDN
    assert 'unpkg.com/lucide' in content, "Lucide CDN not found"
    print("✓ Lucide CDN is present")
    
    # Check initialization
    assert 'lucide.createIcons' in content, "Lucide initialization not found"
    print("✓ Lucide initialization is present")
    
    # Check error handling
    assert 'Lucide Icons failed to load' in content, "Error handling not found"
    print("✓ Error handling is present")
    
    return True

def test_lucide_css_styling():
    """Test that Lucide CSS styling is present"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_styles = [
        '.lucide-icon',
        '.lucide-sm',
        '.lucide-lg',
        '.lucide-xl',
        '.lucide-2xl',
        '.lucide-primary',
        '.lucide-success',
        '.lucide-danger',
        '.lucide-warning',
        '.lucide-info',
        '.btn .lucide-icon',
        '.kpi-icon .lucide-icon',
    ]
    
    for style in required_styles:
        assert style in content, f"Required style '{style}' not found"
    
    print(f"✓ All {len(required_styles)} required CSS styles are present")
    return True

def test_icon_migration_completeness():
    """Test that all icon migrations from tasks 2.1-2.4 are complete"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Task 2.1: Sidebar brand logo
    assert 'data-lucide="package"' in content, "Brand logo not migrated"
    print("✓ Task 2.1: Sidebar brand logo migrated")
    
    # Task 2.2: Sidebar menu icons (8 icons)
    sidebar_icons = ['globe', 'shopping-bag', 'shopping-cart', 'headphones', 
                     'boxes', 'calculator', 'users', 'settings']
    for icon in sidebar_icons:
        assert f'data-lucide="{icon}"' in content, f"Sidebar icon '{icon}' not migrated"
    print(f"✓ Task 2.2: All {len(sidebar_icons)} sidebar menu icons migrated")
    
    # Task 2.3: Navigation bar icons (7 icons)
    nav_icons = ['gauge', 'trending-up', 'cloud-upload', 'shield', 
                 'trash-2', 'clock', 'log-out', 'info']
    for icon in nav_icons:
        assert f'data-lucide="{icon}"' in content, f"Navigation icon '{icon}' not migrated"
    print(f"✓ Task 2.3: All {len(nav_icons)} navigation bar icons migrated")
    
    # Task 2.4: Utility icons (5 icons)
    utility_icons = ['menu', 'layout-grid', 'more-vertical', 'x', 
                     'chevron-down', 'chevron-right']
    for icon in utility_icons:
        assert f'data-lucide="{icon}"' in content, f"Utility icon '{icon}' not migrated"
    print(f"✓ Task 2.4: All {len(utility_icons)} utility icons migrated")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CHECKPOINT: Base Template Migration Verification")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        test_lucide_cdn_and_init()
        print()
        
        test_lucide_css_styling()
        print()
        
        test_no_bootstrap_icons()
        print()
        
        test_no_emoji_in_ui()
        print()
        
        test_lucide_icons_present()
        print()
        
        test_icon_migration_completeness()
        print()
        
        print("=" * 60)
        print("✅ CHECKPOINT PASSED: All base template tests passed!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Task 1: Lucide Icons setup complete")
        print("  ✓ Task 2.1: Sidebar brand logo migrated")
        print("  ✓ Task 2.2: Sidebar menu icons migrated")
        print("  ✓ Task 2.3: Navigation bar icons migrated")
        print("  ✓ Task 2.4: Utility icons migrated")
        print()
        print("Ready to proceed to Task 4: Migrate Dashboard Page")
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ CHECKPOINT FAILED: {e}")
        print("=" * 60)
        exit(1)
