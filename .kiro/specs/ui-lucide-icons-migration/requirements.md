# Requirements Document

## Introduction

ระบบ VNIX ERP Manager Console ปัจจุบันใช้ Bootstrap Icons และ Emoji/Symbols ปะปนกันอยู่ในหลายส่วนของ UI ซึ่งทำให้ดูไม่สม่ำเสมอและไม่เป็นมืออาชีพ การปรับปรุงนี้จะเปลี่ยนไปใช้ Lucide Icons ทั้งระบบเพื่อความสวยงาม สม่ำเสมอ และเป็นมืออาชีพมากขึ้น

## Glossary

- **Lucide_Icons**: ไลบรารี icon แบบ open-source ที่มีดีไซน์สวยงาม สม่ำเสมอ และรองรับการใช้งานแบบ modern
- **Bootstrap_Icons**: ไลบรารี icon ที่ใช้อยู่ในปัจจุบัน (จะถูกแทนที่)
- **Emoji**: สัญลักษณ์อิโมจิที่ใช้ใน HTML (เช่น 📊, 📅, ⚡, 🔍)
- **UI_Component**: ส่วนประกอบของ User Interface เช่น ปุ่ม, การ์ด, เมนู
- **Template_File**: ไฟล์ HTML template ที่ใช้ render หน้าเว็บ

## Requirements

### Requirement 1: ติดตั้งและตั้งค่า Lucide Icons

**User Story:** ในฐานะนักพัฒนา ฉันต้องการติดตั้ง Lucide Icons เข้าสู่โปรเจกต์ เพื่อให้สามารถใช้งาน icon ใหม่ได้

#### Acceptance Criteria

1. WHEN THE System loads THE base template SHALL include Lucide Icons library via CDN
2. THE System SHALL verify Lucide Icons library loads successfully before rendering icons
3. THE System SHALL maintain backward compatibility during migration period

### Requirement 2: แทนที่ Emoji ด้วย Lucide Icons

**User Story:** ในฐานะผู้ใช้งาน ฉันต้องการเห็น icon ที่สวยงามและสม่ำเสมอแทน emoji เพื่อความเป็นมืออาชีพ

#### Acceptance Criteria

1. WHEN displaying dashboard icons THEN THE System SHALL use Lucide Icons instead of emoji
2. WHEN displaying status indicators THEN THE System SHALL use Lucide Icons with appropriate colors
3. WHEN displaying navigation icons THEN THE System SHALL use Lucide Icons consistently
4. THE System SHALL replace emoji 📊 with Lucide BarChart3 icon
5. THE System SHALL replace emoji 📅 with Lucide Calendar icon
6. THE System SHALL replace emoji ⚡ with Lucide Zap icon
7. THE System SHALL replace emoji 🔍 with Lucide Search icon
8. THE System SHALL replace emoji ✅ with Lucide CheckCircle2 icon
9. THE System SHALL replace emoji ⚠️ with Lucide AlertTriangle icon
10. THE System SHALL replace emoji 🔥 with Lucide Flame icon
11. THE System SHALL replace emoji 📦 with Lucide Package icon
12. THE System SHALL replace emoji 🏪 with Lucide Store icon

### Requirement 3: แทนที่ Bootstrap Icons ด้วย Lucide Icons

**User Story:** ในฐานะนักพัฒนา ฉันต้องการใช้ icon library เดียวทั้งระบบ เพื่อความสม่ำเสมอและง่ายต่อการบำรุงรักษา

#### Acceptance Criteria

1. WHEN rendering sidebar menu THEN THE System SHALL use Lucide Icons for all menu items
2. WHEN rendering navigation bar THEN THE System SHALL use Lucide Icons for all navigation items
3. WHEN rendering buttons THEN THE System SHALL use Lucide Icons consistently
4. WHEN rendering form controls THEN THE System SHALL use Lucide Icons for input decorations
5. THE System SHALL maintain icon sizing consistency across all components
6. THE System SHALL maintain icon color consistency with design system

### Requirement 4: อัปเดต Template Files

**User Story:** ในฐานะนักพัฒนา ฉันต้องการอัปเดตไฟล์ template ทั้งหมด เพื่อให้ใช้ Lucide Icons แทน icon เก่า

#### Acceptance Criteria

1. WHEN updating base.html THEN THE System SHALL include Lucide Icons CDN link
2. WHEN updating dashboard.html THEN THE System SHALL replace all emoji and Bootstrap Icons
3. WHEN updating report_lowstock.html THEN THE System SHALL replace all emoji and Bootstrap Icons
4. WHEN updating report.html THEN THE System SHALL replace all emoji and Bootstrap Icons
5. WHEN updating report_notenough.html THEN THE System SHALL replace all emoji and Bootstrap Icons
6. WHEN updating report_nostock_READY.html THEN THE System SHALL replace all emoji and Bootstrap Icons
7. WHEN updating admin_shops.html THEN THE System SHALL replace all emoji and Bootstrap Icons
8. WHEN updating users.html THEN THE System SHALL replace all emoji and Bootstrap Icons
9. WHEN updating picking.html THEN THE System SHALL replace all emoji and Bootstrap Icons
10. WHEN updating clear_confirm.html THEN THE System SHALL replace all emoji and Bootstrap Icons
11. WHEN updating import_stock.html THEN THE System SHALL replace all emoji and Bootstrap Icons

### Requirement 5: รักษาความสอดคล้องของ Icon Styling

**User Story:** ในฐานะผู้ใช้งาน ฉันต้องการเห็น icon ที่มีขนาดและสีสันสอดคล้องกัน เพื่อประสบการณ์การใช้งานที่ดี

#### Acceptance Criteria

1. WHEN displaying icons THEN THE System SHALL apply consistent sizing classes
2. WHEN displaying icons in buttons THEN THE System SHALL maintain proper spacing
3. WHEN displaying icons in cards THEN THE System SHALL maintain proper alignment
4. WHEN displaying colored icons THEN THE System SHALL use design system color palette
5. THE System SHALL ensure icon stroke width is consistent across all components

### Requirement 6: ทดสอบการแสดงผลใน Browser

**User Story:** ในฐานะผู้ทดสอบ ฉันต้องการตรวจสอบว่า icon แสดงผลถูกต้องในทุก browser เพื่อความมั่นใจในคุณภาพ

#### Acceptance Criteria

1. WHEN loading pages in Chrome THEN THE System SHALL display all Lucide Icons correctly
2. WHEN loading pages in Firefox THEN THE System SHALL display all Lucide Icons correctly
3. WHEN loading pages in Safari THEN THE System SHALL display all Lucide Icons correctly
4. WHEN loading pages in Edge THEN THE System SHALL display all Lucide Icons correctly
5. WHEN loading pages on mobile devices THEN THE System SHALL display all Lucide Icons correctly
6. THE System SHALL ensure icons load within acceptable time limits

### Requirement 7: ลบ Dependencies ที่ไม่ใช้แล้ว

**User Story:** ในฐานะนักพัฒนา ฉันต้องการลบ Bootstrap Icons CDN link ออก เพื่อลดขนาดและเพิ่มประสิทธิภาพ

#### Acceptance Criteria

1. WHEN migration is complete THEN THE System SHALL remove Bootstrap Icons CDN link from base.html
2. WHEN migration is complete THEN THE System SHALL verify no Bootstrap Icons classes remain in templates
3. THE System SHALL maintain page load performance after migration

### Requirement 8: สร้างเอกสารการใช้งาน Icon

**User Story:** ในฐานะนักพัฒนา ฉันต้องการเอกสารแนะนำการใช้ Lucide Icons เพื่อใช้อ้างอิงในอนาคต

#### Acceptance Criteria

1. THE System SHALL provide documentation listing all icon mappings (old → new)
2. THE System SHALL provide examples of common icon usage patterns
3. THE System SHALL provide guidelines for adding new icons in the future
