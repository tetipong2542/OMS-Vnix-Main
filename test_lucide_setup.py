#!/usr/bin/env python3
"""
Simple test to verify Lucide Icons setup in base.html
Tests Requirements 1.1 and 1.2
"""

def test_lucide_cdn_present():
    """Test that Lucide Icons CDN script is present in base.html"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Lucide CDN script
    assert 'unpkg.com/lucide' in content, "Lucide Icons CDN script not found in base.html"
    print("✓ Lucide Icons CDN script is present")
    
    # Check for initialization script
    assert 'lucide.createIcons' in content, "Lucide Icons initialization script not found"
    print("✓ Lucide Icons initialization script is present")
    
    # Check for error handling
    assert 'Lucide Icons failed to load' in content, "Error handling for CDN failure not found"
    print("✓ Error handling for CDN failure is present")
    
    return True

def test_lucide_css_present():
    """Test that Lucide Icons CSS styling is present in base.html"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for base styling
    assert 'LUCIDE ICONS STYLING' in content, "Lucide Icons CSS section not found"
    print("✓ Lucide Icons CSS section is present")
    
    # Check for size variants
    assert '.lucide-sm' in content, "Lucide size variant .lucide-sm not found"
    assert '.lucide-lg' in content, "Lucide size variant .lucide-lg not found"
    assert '.lucide-xl' in content, "Lucide size variant .lucide-xl not found"
    assert '.lucide-2xl' in content, "Lucide size variant .lucide-2xl not found"
    print("✓ Lucide size variants are present")
    
    # Check for color classes
    assert '.lucide-primary' in content, "Lucide color class .lucide-primary not found"
    assert '.lucide-success' in content, "Lucide color class .lucide-success not found"
    assert '.lucide-danger' in content, "Lucide color class .lucide-danger not found"
    assert '.lucide-warning' in content, "Lucide color class .lucide-warning not found"
    assert '.lucide-info' in content, "Lucide color class .lucide-info not found"
    print("✓ Lucide color classes are present")
    
    # Check for button styling
    assert '.btn .lucide-icon' in content, "Lucide button styling not found"
    print("✓ Lucide button styling is present")
    
    # Check for card styling
    assert '.kpi-icon .lucide-icon' in content, "Lucide card styling not found"
    print("✓ Lucide card styling is present")
    
    return True

def test_lucide_initialization_order():
    """Test that Lucide script is loaded before initialization"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find positions
    cdn_pos = content.find('unpkg.com/lucide')
    init_pos = content.find('lucide.createIcons')
    
    assert cdn_pos > 0, "Lucide CDN script not found"
    assert init_pos > 0, "Lucide initialization not found"
    assert cdn_pos < init_pos, "Lucide CDN must be loaded before initialization"
    print("✓ Lucide CDN is loaded before initialization")
    
    return True

if __name__ == '__main__':
    print("Testing Lucide Icons Setup in base.html")
    print("=" * 50)
    
    try:
        test_lucide_cdn_present()
        print()
        test_lucide_css_present()
        print()
        test_lucide_initialization_order()
        print()
        print("=" * 50)
        print("✅ All tests passed! Lucide Icons setup is complete.")
        print("\nRequirements validated:")
        print("  - 1.1: Lucide Icons CDN script added to base.html ✓")
        print("  - 1.2: Lucide Icons initialization script added ✓")
        print("  - CSS styling for Lucide icons added ✓")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
