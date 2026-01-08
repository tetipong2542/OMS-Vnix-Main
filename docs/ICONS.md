# Icon Usage Guide

## Overview

This document provides comprehensive guidance on using Lucide Icons in the VNIX ERP Manager Console. The system has migrated from Bootstrap Icons and Emoji to Lucide Icons for a consistent, professional, and modern user interface.

## What is Lucide Icons?

Lucide Icons is an open-source icon library that provides beautiful, consistent icons with a modern design. It's a community fork of Feather Icons with additional icons and active maintenance.

- **Official Website**: https://lucide.dev
- **Icon Browser**: https://lucide.dev/icons
- **GitHub**: https://github.com/lucide-icons/lucide

## Basic Usage

### Adding a New Icon

To add a Lucide icon to any template:

```html
<i data-lucide="icon-name"></i>
```

The icon will be automatically initialized by the Lucide library loaded in `base.html`.

### Example

```html
<!-- Simple icon -->
<i data-lucide="package"></i>

<!-- Icon with text -->
<button class="btn btn-primary">
  <i data-lucide="save"></i> Save
</button>
```

## Icon Sizing

Lucide icons support multiple size variants through CSS classes:

| Class | Size | Use Case |
|-------|------|----------|
| (default) | 1em | Standard inline icons |
| `lucide-sm` | 0.875em | Small icons in compact spaces |
| `lucide-lg` | 1.25em | Larger icons for emphasis |
| `lucide-xl` | 1.5em | Extra large icons |
| `lucide-2xl` | 2em | Very large icons |

### Sizing Examples

```html
<!-- Small icon -->
<i data-lucide="info" class="lucide-sm"></i>

<!-- Large icon -->
<i data-lucide="alert-triangle" class="lucide-lg"></i>

<!-- Extra large icon -->
<i data-lucide="package" class="lucide-xl"></i>

<!-- 2X large icon -->
<i data-lucide="check-circle" class="lucide-2xl"></i>
```

## Icon Colors

Apply color classes to match your design system:

| Class | Color | Use Case |
|-------|-------|----------|
| `lucide-primary` | Primary brand color | Main actions |
| `lucide-success` | Success/green | Positive actions, confirmations |
| `lucide-danger` | Danger/red | Destructive actions, errors |
| `lucide-warning` | Warning/yellow | Warnings, cautions |
| `lucide-info` | Info/blue | Information, help |

### Color Examples

```html
<!-- Success icon -->
<i data-lucide="check-circle" class="lucide-success"></i>

<!-- Danger icon -->
<i data-lucide="alert-triangle" class="lucide-danger"></i>

<!-- Warning icon -->
<i data-lucide="alert-circle" class="lucide-warning"></i>

<!-- Info icon -->
<i data-lucide="info" class="lucide-info"></i>
```

## Common Usage Patterns

### Icons in Buttons

```html
<!-- Icon before text -->
<button class="btn btn-primary">
  <i data-lucide="save"></i> Save
</button>

<!-- Icon after text -->
<button class="btn btn-secondary">
  Next <i data-lucide="chevron-right"></i>
</button>

<!-- Icon only button -->
<button class="btn btn-sm btn-outline-secondary">
  <i data-lucide="edit"></i>
</button>
```

### Icons in Cards

```html
<div class="card">
  <div class="card-body">
    <div class="kpi-icon">
      <i data-lucide="package"></i>
    </div>
    <h5 class="card-title">Total Orders</h5>
    <p class="card-text">1,234</p>
  </div>
</div>
```

### Icons in Navigation

```html
<!-- Sidebar menu item -->
<li class="nav-item">
  <a class="nav-link" href="/dashboard">
    <i data-lucide="gauge"></i>
    <span>Dashboard</span>
  </a>
</li>

<!-- Dropdown menu -->
<div class="dropdown">
  <button class="btn dropdown-toggle">
    <i data-lucide="settings"></i> Settings
  </button>
</div>
```

### Icons in Lists

```html
<ul class="list-unstyled">
  <li>
    <i data-lucide="check-circle" class="lucide-success"></i>
    Task completed
  </li>
  <li>
    <i data-lucide="clock" class="lucide-warning"></i>
    Task pending
  </li>
  <li>
    <i data-lucide="x-circle" class="lucide-danger"></i>
    Task failed
  </li>
</ul>
```

### Icons in Forms

```html
<!-- Input with icon -->
<div class="input-group">
  <span class="input-group-text">
    <i data-lucide="search"></i>
  </span>
  <input type="text" class="form-control" placeholder="Search...">
</div>

<!-- Label with icon -->
<label class="form-label">
  <i data-lucide="user"></i> Username
</label>
```

## Icon Mapping Reference

### Emoji to Lucide Icons

This table shows how emoji have been replaced with Lucide Icons:

| Emoji | Description | Lucide Icon | HTML |
|-------|-------------|-------------|------|
| 📊 | Dashboard/Chart | `bar-chart-3` | `<i data-lucide="bar-chart-3"></i>` |
| 📅 | Calendar/Date | `calendar` | `<i data-lucide="calendar"></i>` |
| ⚡ | Fast/Power | `zap` | `<i data-lucide="zap"></i>` |
| 🔍 | Search | `search` | `<i data-lucide="search"></i>` |
| ✅ | Check/Success | `check-circle-2` | `<i data-lucide="check-circle-2"></i>` |
| ⚠️ | Warning | `alert-triangle` | `<i data-lucide="alert-triangle"></i>` |
| 🔥 | Fire/Hot | `flame` | `<i data-lucide="flame"></i>` |
| 📦 | Package/Box | `package` | `<i data-lucide="package"></i>` |
| 🏪 | Store/Shop | `store` | `<i data-lucide="store"></i>` |

### Bootstrap Icons to Lucide Icons

This table shows the complete mapping from Bootstrap Icons to Lucide Icons:

| Bootstrap Icon | Lucide Icon | HTML |
|----------------|-------------|------|
| `bi-box-seam-fill` | `package` | `<i data-lucide="package"></i>` |
| `bi-globe2` | `globe` | `<i data-lucide="globe"></i>` |
| `bi-shop` | `shopping-bag` | `<i data-lucide="shopping-bag"></i>` |
| `bi-cart-check` | `shopping-cart` | `<i data-lucide="shopping-cart"></i>` |
| `bi-headset` | `headphones` | `<i data-lucide="headphones"></i>` |
| `bi-boxes` | `boxes` | `<i data-lucide="boxes"></i>` |
| `bi-calculator` | `calculator` | `<i data-lucide="calculator"></i>` |
| `bi-people` | `users` | `<i data-lucide="users"></i>` |
| `bi-gear` | `settings` | `<i data-lucide="settings"></i>` |
| `bi-speedometer2` | `gauge` | `<i data-lucide="gauge"></i>` |
| `bi-graph-up-arrow` | `trending-up` | `<i data-lucide="trending-up"></i>` |
| `bi-cloud-upload` | `cloud-upload` | `<i data-lucide="cloud-upload"></i>` |
| `bi-shield-lock` | `shield` | `<i data-lucide="shield"></i>` |
| `bi-trash` | `trash-2` | `<i data-lucide="trash-2"></i>` |
| `bi-clock` | `clock` | `<i data-lucide="clock"></i>` |
| `bi-check-circle` | `check-circle` | `<i data-lucide="check-circle"></i>` |
| `bi-exclamation-triangle` | `alert-triangle` | `<i data-lucide="alert-triangle"></i>` |
| `bi-x-octagon` | `octagon-x` | `<i data-lucide="octagon-x"></i>` |
| `bi-send` | `send` | `<i data-lucide="send"></i>` |
| `bi-box-seam` | `package` | `<i data-lucide="package"></i>` |
| `bi-upc-scan` | `scan-barcode` | `<i data-lucide="scan-barcode"></i>` |
| `bi-printer` | `printer` | `<i data-lucide="printer"></i>` |
| `bi-file-earmark-excel` | `file-spreadsheet` | `<i data-lucide="file-spreadsheet"></i>` |
| `bi-clock-history` | `history` | `<i data-lucide="history"></i>` |
| `bi-arrow-left` | `arrow-left` | `<i data-lucide="arrow-left"></i>` |
| `bi-calendar-check` | `calendar-check` | `<i data-lucide="calendar-check"></i>` |
| `bi-fire` | `flame` | `<i data-lucide="flame"></i>` |
| `bi-flag-fill` | `flag` | `<i data-lucide="flag"></i>` |
| `bi-layers` | `layers` | `<i data-lucide="layers"></i>` |
| `bi-clipboard-check` | `clipboard-check` | `<i data-lucide="clipboard-check"></i>` |
| `bi-filter` | `filter` | `<i data-lucide="filter"></i>` |
| `bi-x-circle` | `x-circle` | `<i data-lucide="x-circle"></i>` |
| `bi-list` | `menu` | `<i data-lucide="menu"></i>` |
| `bi-grid-3x3-gap-fill` | `layout-grid` | `<i data-lucide="layout-grid"></i>` |
| `bi-three-dots-vertical` | `more-vertical` | `<i data-lucide="more-vertical"></i>` |
| `bi-box-arrow-right` | `log-out` | `<i data-lucide="log-out"></i>` |
| `bi-info-circle-fill` | `info` | `<i data-lucide="info"></i>` |
| `bi-x-lg` | `x` | `<i data-lucide="x"></i>` |
| `bi-chevron-down` | `chevron-down` | `<i data-lucide="chevron-down"></i>` |
| `bi-chevron-right` | `chevron-right` | `<i data-lucide="chevron-right"></i>` |
| `bi-arrow-clockwise` | `refresh-cw` | `<i data-lucide="refresh-cw"></i>` |
| `bi-save` | `save` | `<i data-lucide="save"></i>` |
| `bi-database` | `database` | `<i data-lucide="database"></i>` |
| `bi-file-earmark-bar-graph-fill` | `bar-chart` | `<i data-lucide="bar-chart"></i>` |
| `bi-file-earmark-text` | `file-text` | `<i data-lucide="file-text"></i>` |
| `bi-file-earmark-x` | `file-x` | `<i data-lucide="file-x"></i>` |
| `bi-cloud-slash` | `cloud-off` | `<i data-lucide="cloud-off"></i>` |
| `bi-lock-fill` | `lock` | `<i data-lucide="lock"></i>` |
| `bi-unlock-fill` | `unlock` | `<i data-lucide="unlock"></i>` |
| `bi-circle-fill` | `circle` | `<i data-lucide="circle"></i>` |
| `bi-inbox` | `inbox` | `<i data-lucide="inbox"></i>` |

## Guidelines for Adding New Icons

### 1. Find the Right Icon

1. Visit the [Lucide Icons browser](https://lucide.dev/icons)
2. Search for the icon you need
3. Note the exact icon name (e.g., `package`, `user`, `settings`)

### 2. Use Semantic Icon Names

Choose icons that clearly represent their function:

- ✅ **Good**: `<i data-lucide="trash-2"></i>` for delete action
- ❌ **Bad**: `<i data-lucide="x"></i>` for delete action (too generic)

### 3. Maintain Consistency

- Use the same icon for the same action throughout the application
- Follow existing patterns in the codebase
- Check the mapping tables above before adding new icons

### 4. Consider Context

Choose icon size and color based on context:

```html
<!-- Primary action button - standard size, primary color -->
<button class="btn btn-primary">
  <i data-lucide="save"></i> Save
</button>

<!-- Warning message - larger size, warning color -->
<div class="alert alert-warning">
  <i data-lucide="alert-triangle" class="lucide-lg lucide-warning"></i>
  Please review your changes
</div>

<!-- KPI card - extra large size -->
<div class="kpi-icon">
  <i data-lucide="package" class="lucide-2xl"></i>
</div>
```

### 5. Test Across Browsers

After adding new icons, test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Android)

### 6. Accessibility Considerations

Always consider accessibility when using icons:

```html
<!-- Icon with text (accessible by default) -->
<button>
  <i data-lucide="save"></i> Save
</button>

<!-- Icon-only button (needs aria-label) -->
<button aria-label="Save">
  <i data-lucide="save" aria-hidden="true"></i>
</button>

<!-- Decorative icon (hide from screen readers) -->
<h2>
  <i data-lucide="package" aria-hidden="true"></i>
  Orders
</h2>
```

## Troubleshooting

### Icons Not Displaying

If icons are not displaying:

1. **Check the icon name**: Ensure the icon name is correct and exists in Lucide
2. **Check the script**: Verify that the Lucide CDN script is loaded in `base.html`
3. **Check initialization**: Ensure `lucide.createIcons()` is called after DOM load
4. **Check browser console**: Look for JavaScript errors

### Icons Look Wrong

If icons appear incorrectly:

1. **Check CSS classes**: Ensure you're using the correct size and color classes
2. **Check parent container**: Some containers may override icon styles
3. **Check stroke-width**: Default is 2, but can be adjusted if needed
4. **Clear browser cache**: Old styles may be cached

### Performance Issues

If you notice performance issues:

1. **Limit icon count**: Too many icons on one page can slow rendering
2. **Use appropriate sizes**: Don't use oversized icons unnecessarily
3. **Consider lazy loading**: For pages with many icons, consider lazy initialization

## Technical Details

### How Lucide Icons Work

Lucide Icons are loaded via CDN and initialized with JavaScript:

```html
<!-- In base.html, before closing </body> tag -->
<script src="https://unpkg.com/lucide@latest"></script>
<script>
  lucide.createIcons({
    attrs: {
      class: ['lucide-icon'],
      'stroke-width': 2
    }
  });
</script>
```

When `lucide.createIcons()` is called, it:
1. Finds all elements with `data-lucide` attribute
2. Replaces them with inline SVG elements
3. Applies the specified icon based on the attribute value

### Custom Styling

Icons inherit color from their parent element by default. You can customize further:

```css
/* Custom icon color */
.my-custom-icon {
  stroke: #ff6b6b;
}

/* Custom icon size */
.my-custom-icon {
  width: 24px;
  height: 24px;
}

/* Custom stroke width */
.my-custom-icon {
  stroke-width: 1.5;
}
```

## Best Practices

1. **Use semantic HTML**: Wrap icons in appropriate elements (`<button>`, `<a>`, etc.)
2. **Provide text alternatives**: Always include text or `aria-label` for icon-only elements
3. **Be consistent**: Use the same icon for the same action throughout the app
4. **Don't overuse**: Too many icons can be overwhelming
5. **Test thoroughly**: Verify icons work across all supported browsers
6. **Document changes**: Update this guide when adding new icon patterns

## Resources

- **Lucide Icons Official Site**: https://lucide.dev
- **Icon Browser**: https://lucide.dev/icons
- **Documentation**: https://lucide.dev/guide/
- **GitHub Repository**: https://github.com/lucide-icons/lucide
- **CDN Usage**: https://lucide.dev/guide/packages/lucide

## Support

For questions or issues related to icons:

1. Check this documentation first
2. Browse the [Lucide Icons documentation](https://lucide.dev/guide/)
3. Search for similar icons in the [icon browser](https://lucide.dev/icons)
4. Consult the design document at `.kiro/specs/ui-lucide-icons-migration/design.md`

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Maintained by**: VNIX ERP Development Team
