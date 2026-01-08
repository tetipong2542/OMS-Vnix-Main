# Implementation Plan: UI Lucide Icons Migration

## Overview

การ implement จะทำทีละ phase ตามลำดับที่กำหนดใน design document โดยเริ่มจากการติดตั้ง Lucide Icons ใน base template จากนั้นจึงค่อยๆ migrate แต่ละหน้าทีละหน้า เพื่อให้สามารถทดสอบและตรวจสอบได้ง่าย

## Tasks

- [x] 1. Setup Lucide Icons in Base Template
  - Add Lucide Icons CDN script to base.html before closing body tag
  - Add Lucide Icons initialization script
  - Add CSS styling for Lucide icons (base styles, size variants, colors)
  - Test that Lucide library loads successfully
  - _Requirements: 1.1, 1.2_

- [x] 1.1 Write unit test for Lucide CDN presence
  - Test that script tag with Lucide CDN is present in base.html
  - Test that lucide.createIcons() is called
  - _Requirements: 1.1_

- [x] 2. Migrate Base Template Icons
  - [x] 2.1 Update sidebar brand logo icon
    - Replace `bi-box-seam-fill` with `<i data-lucide="package"></i>`
    - _Requirements: 3.1, 4.1_
  
  - [x] 2.2 Update sidebar menu icons
    - Replace `bi-globe2` with `<i data-lucide="globe"></i>` (แผนก Online)
    - Replace `bi-shop` with `<i data-lucide="shopping-bag"></i>` (แผนก Sale)
    - Replace `bi-cart-check` with `<i data-lucide="shopping-cart"></i>` (แผนก จัดซื้อ)
    - Replace `bi-headset` with `<i data-lucide="headphones"></i>` (แผนก Helpdesk)
    - Replace `bi-boxes` with `<i data-lucide="boxes"></i>` (แผนก คลังสินค้า)
    - Replace `bi-calculator` with `<i data-lucide="calculator"></i>` (แผนก บัญชี)
    - Replace `bi-people` with `<i data-lucide="users"></i>` (แผนก HR)
    - Replace `bi-gear` with `<i data-lucide="settings"></i>` (ตั้งค่าระบบ)
    - _Requirements: 3.1, 4.1_
  
  - [x] 2.3 Update navigation bar icons
    - Replace `bi-speedometer2` with `<i data-lucide="gauge"></i>` (Dashboard)
    - Replace `bi-graph-up-arrow` with `<i data-lucide="trending-up"></i>` (ราคาตลาด)
    - Replace `bi-cloud-upload` with `<i data-lucide="cloud-upload"></i>` (นำเข้าข้อมูล)
    - Replace `bi-shield-lock` with `<i data-lucide="shield"></i>` (ผู้ดูแลระบบ)
    - Replace `bi-trash` with `<i data-lucide="trash-2"></i>` (ล้างข้อมูล)
    - Replace `bi-clock` with `<i data-lucide="clock"></i>` (Current Time)
    - Replace `bi-box-arrow-right` with `<i data-lucide="log-out"></i>` (ออกจากระบบ)
    - Replace `bi-info-circle-fill` with `<i data-lucide="info"></i>` (Flash messages)
    - _Requirements: 3.2, 4.1_
  
  - [x] 2.4 Update utility icons
    - Replace `bi-list` with `<i data-lucide="menu"></i>` (Menu toggle)
    - Replace `bi-grid-3x3-gap-fill` with `<i data-lucide="layout-grid"></i>` (App name icon)
    - Replace `bi-three-dots-vertical` with `<i data-lucide="more-vertical"></i>` (Mobile menu)
    - Replace `bi-x-lg` with `<i data-lucide="x"></i>` (Close sidebar)
    - Replace `bi-chevron-down` with `<i data-lucide="chevron-down"></i>` (Dropdown arrows)
    - Replace `bi-chevron-right` with `<i data-lucide="chevron-right"></i>` (Submenu arrows)
    - _Requirements: 3.3, 4.1_

- [ ]* 2.5 Write unit tests for base template icon replacements
  - Test sidebar icons are Lucide icons
  - Test navigation icons are Lucide icons
  - Test no Bootstrap Icons classes remain in base.html
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Checkpoint - Test Base Template
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Migrate Dashboard Page
  - [x] 4.1 Update dashboard header icons
    - Replace emoji 📊 with `<i data-lucide="bar-chart-3"></i>`
    - Replace emoji 📅 with `<i data-lucide="calendar"></i>`
    - Replace emoji ⚡ with `<i data-lucide="zap"></i>`
    - Replace emoji 🔍 with `<i data-lucide="search"></i>`
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 4.2_
  
  - [x] 4.2 Update KPI card icons
    - Replace `bi-inbox` with `<i data-lucide="inbox"></i>` (รวมงานค้าง)
    - Replace `bi-check-circle` with `<i data-lucide="check-circle"></i>` (กอง 1)
    - Replace `bi-exclamation-triangle` with `<i data-lucide="alert-triangle"></i>` (กอง 2)
    - Replace `bi-x-octagon` with `<i data-lucide="octagon-x"></i>` (กอง 3)
    - Replace `bi-file-earmark-x` with `<i data-lucide="file-x"></i>` (ยังไม่ได้แพ็ค)
    - Replace `bi-cloud-slash` with `<i data-lucide="cloud-off"></i>` (ยังไม่นำเข้า SBS)
    - Replace `bi-upc-scan` with `<i data-lucide="scan-barcode"></i>` (รอ Scan)
    - Replace `bi-send` with `<i data-lucide="send"></i>` (จ่ายงานแล้ว)
    - Replace `bi-box-seam` with `<i data-lucide="package"></i>` (แพ็คแล้ว)
    - Replace `bi-layers` with `<i data-lucide="layers"></i>` (คลังรับงาน)
    - Replace `bi-clipboard-check` with `<i data-lucide="clipboard-check"></i>` (กอง 1 คลัง)
    - _Requirements: 2.8, 2.9, 2.12, 3.1, 3.2, 4.2_
  
  - [x] 4.3 Update section label icons
    - Replace emoji 🔥 with `<i data-lucide="flame"></i>` (งานค้าง)
    - Replace `bi-fire` with `<i data-lucide="flame"></i>`
    - Replace `bi-flag-fill` with `<i data-lucide="flag"></i>` (งานจบวันนี้)
    - Replace `bi-box-seam-fill` with `<i data-lucide="package"></i>` (คลังรับงาน)
    - _Requirements: 2.10, 4.2_
  
  - [x] 4.4 Update filter and action icons
    - Replace `bi-filter` with `<i data-lucide="filter"></i>`
    - Replace `bi-x-circle` with `<i data-lucide="x-circle"></i>`
    - Replace `bi-arrow-left` with `<i data-lucide="arrow-left"></i>`
    - Replace `bi-calendar-check` with `<i data-lucide="calendar-check"></i>`
    - Replace emoji 🔍 with `<i data-lucide="search"></i>` (Global Search)
    - _Requirements: 2.7, 3.3, 4.2_

- [ ]* 4.5 Write unit tests for dashboard icon replacements
  - Test all emoji are replaced with Lucide icons
  - Test all Bootstrap Icons are replaced with Lucide icons
  - Test icon sizing is consistent
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 5.1_

- [x] 5. Checkpoint - Test Dashboard Page
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Migrate Report Pages
  - [x] 6.1 Update report_lowstock.html
    - Replace emoji 📊 with `<i data-lucide="bar-chart-3"></i>` (header)
    - Replace emoji ✅ with `<i data-lucide="check-circle-2"></i>` (Scan แล้ว)
    - Replace emoji ⚠️ with `<i data-lucide="alert-triangle"></i>` (notes)
    - Replace `bi-arrow-left` with `<i data-lucide="arrow-left"></i>`
    - Replace `bi-file-earmark-bar-graph-fill` with `<i data-lucide="bar-chart"></i>`
    - Replace `bi-printer` with `<i data-lucide="printer"></i>`
    - Replace `bi-lock-fill` with `<i data-lucide="lock"></i>`
    - Replace `bi-save` with `<i data-lucide="save"></i>`
    - Replace `bi-file-earmark-excel` with `<i data-lucide="file-spreadsheet"></i>`
    - Replace `bi-filter` with `<i data-lucide="filter"></i>`
    - Replace `bi-database` with `<i data-lucide="database"></i>`
    - Replace `bi-clock-history` with `<i data-lucide="history"></i>`
    - Replace `bi-box-seam` with `<i data-lucide="package"></i>`
    - Replace `bi-exclamation-triangle` with `<i data-lucide="alert-triangle"></i>`
    - Replace `bi-upc-scan` with `<i data-lucide="scan-barcode"></i>`
    - Replace `bi-arrow-clockwise` with `<i data-lucide="refresh-cw"></i>`
    - Replace `bi-check-circle` with `<i data-lucide="check-circle"></i>`
    - Replace `bi-circle-fill` with `<i data-lucide="circle"></i>`
    - Replace `bi-unlock-fill` with `<i data-lucide="unlock"></i>`
    - _Requirements: 2.4, 2.8, 2.9, 4.4_
  
  - [x] 6.2 Update report_notenough.html
    - Apply same icon replacements as report_lowstock.html
    - _Requirements: 2.4, 2.8, 2.9, 4.5_
  
  - [x] 6.3 Update report_nostock_READY.html
    - Apply same icon replacements as report_lowstock.html
    - _Requirements: 2.4, 2.8, 2.9, 4.6_
  
  - [x] 6.4 Update report.html
    - Replace emoji 📅 with `<i data-lucide="calendar"></i>`
    - Replace emoji 🔍 with `<i data-lucide="search"></i>`
    - Replace emoji 📦 with `<i data-lucide="package"></i>`
    - Replace emoji ✅ with `<i data-lucide="check-circle-2"></i>`
    - Replace emoji ⚠️ with `<i data-lucide="alert-triangle"></i>`
    - Replace `bi-search` with `<i data-lucide="search"></i>`
    - _Requirements: 2.5, 2.7, 2.8, 2.9, 2.11, 4.4_

- [ ]* 6.5 Write unit tests for report pages icon replacements
  - Test all emoji are replaced in all report pages
  - Test all Bootstrap Icons are replaced in all report pages
  - Test icon consistency across report pages
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2_

- [x] 7. Checkpoint - Test Report Pages
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Migrate Admin Pages
  - [x] 8.1 Update admin_shops.html
    - Replace emoji 🏪 with `<i data-lucide="store"></i>`
    - _Requirements: 2.12, 4.7_
  
  - [x] 8.2 Update users.html
    - Replace emoji ⚠️ with `<i data-lucide="alert-triangle"></i>` (delete confirmation)
    - _Requirements: 2.9, 4.8_
  
  - [x] 8.3 Update clear_confirm.html
    - Replace emoji ⚠️ with `<i data-lucide="alert-triangle"></i>` (warning)
    - _Requirements: 2.9, 4.10_

- [ ]* 8.4 Write unit tests for admin pages icon replacements
  - Test all emoji are replaced in admin pages
  - Test icon consistency in admin pages
  - _Requirements: 2.1, 2.2, 3.1_

- [x] 9. Migrate Import and Other Pages
  - [x] 9.1 Update import_stock.html
    - Replace emoji 📊 with `<i data-lucide="bar-chart-3"></i>`
    - _Requirements: 2.4, 4.11_
  
  - [x] 9.2 Update picking.html
    - Replace emoji ✅ with `<i data-lucide="check-circle-2"></i>` (ยืนยันจ่ายงาน button)
    - _Requirements: 2.8, 4.9_

- [ ]* 9.3 Write unit tests for import and other pages
  - Test all emoji are replaced
  - Test icon consistency
  - _Requirements: 2.1, 2.2, 3.1_

- [x] 10. Checkpoint - Test All Pages
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Remove Bootstrap Icons Dependency
  - Remove Bootstrap Icons CDN link from base.html
  - Verify no Bootstrap Icons classes remain in any template
  - Test that all pages still render correctly
  - _Requirements: 7.1, 7.2_

- [ ]* 11.1 Write property test for no Bootstrap Icons remnants
  - **Property 6: No Bootstrap Icons Remnants**
  - **Validates: Requirements 7.2**
  - Test that no `bi-` class names exist in any template file
  - _Requirements: 7.2_

- [x] 12. Create Icon Usage Documentation
  - Create docs/ICONS.md file with icon usage guide
  - Document all icon mappings (emoji → Lucide, Bootstrap → Lucide)
  - Provide examples of common icon usage patterns
  - Add guidelines for adding new icons
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 13. Final Testing and Validation
  - [x] 13.1 Browser compatibility testing
    - Test in Chrome (latest)
    - Test in Firefox (latest)
    - Test in Safari (latest)
    - Test in Edge (latest)
    - Test on mobile Safari (iOS 14+)
    - Test on mobile Chrome (Android 10+)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 13.2 Visual regression testing
    - Take screenshots of all pages
    - Compare with baseline screenshots
    - Review and approve visual changes
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 13.3 Performance testing
    - Measure page load times
    - Compare with baseline performance
    - Verify performance is maintained
    - _Requirements: 7.3, 6.6_

- [ ]* 13.4 Write property tests for correctness properties
  - **Property 1: Lucide Icons Library Loading**
  - **Validates: Requirements 1.2**
  - Test that Lucide library loads before icon rendering
  
  - **Property 2: Icon Replacement Completeness**
  - **Validates: Requirements 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4**
  - Test that all emoji and Bootstrap Icons are replaced
  
  - **Property 3: Icon Display Consistency**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
  - Test that icons display with consistent sizing and styling
  
  - **Property 4: Cross-Browser Compatibility**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  - Test that icons render correctly in all browsers
  
  - **Property 5: Template File Update Completeness**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11**
  - Test that all template files are updated
  
  - **Property 7: Performance Maintenance**
  - **Validates: Requirements 7.3, 6.6**
  - Test that page load performance is maintained

- [-] 14. Final Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Migration is done in phases to allow testing at each step
- Backward compatibility is maintained until all pages are migrated
