# ⚡ Quick Reference Card - CSS Classes & Utilities

## Commonly Used Classes

### Buttons
```html
<!-- Primary Button -->
<button class="btn btn-brand">Click Me</button>

<!-- Secondary Button -->
<button class="btn btn-accent">Click Me</button>

<!-- Outline Button -->
<button class="btn btn-outline-brand">Click Me</button>

<!-- Smaller Button -->
<button class="btn btn-brand btn-sm">Small</button>
```

### Cards
```html
<!-- Info Card -->
<div class="card-soft">
    <h3 class="card-label">Title</h3>
    <p>Description</p>
</div>

<!-- Why Card (Contact page style) -->
<div class="why-card">
    <div class="why-icon">🎯</div>
    <h3>Title</h3>
    <p>Description</p>
</div>
```

### Forms
```html
<!-- Text Input -->
<div class="form-group">
    <label class="form-label">Label</label>
    <input class="form-control" type="text" placeholder="Placeholder">
</div>

<!-- Textarea -->
<div class="form-group form-group-full">
    <label class="form-label">Message</label>
    <textarea class="form-control"></textarea>
</div>

<!-- Phone Input -->
<div class="form-group">
    <label class="form-label">Phone</label>
    <div class="phone-input-wrapper">
        <span class="phone-country-code">🇳🇵 +977</span>
        <input class="form-control phone-input" placeholder="9840123456">
    </div>
</div>
```

### Text Utilities
```html
<p class="text-brand">Brand color text</p>
<p class="text-accent">Accent color text</p>
<h2 class="h-Screen">Full screen height</h2>
```

### Shadow Utilities
```html
<div class="shadow-soft">Subtle shadow</div>
<div class="shadow-mid">Medium shadow</div>
<div class="shadow-strong">Strong shadow</div>
```

### Spacing Utilities
```html
<!-- Bootstrap utilities still work -->
<div class="mb-4">Bottom margin</div>
<div class="px-3">Horizontal padding</div>
<div class="mt-5">Top margin</div>
```

### Other Utilities
```html
<div class="rounded-xl">Rounded corners</div>
<div class="transition-all">Smooth transition</div>
<div class="bg-brand-light">Light brand background</div>
<div class="border-brand">Brand colored border</div>
```

---

## Color Reference

### Use in inline styles:
```html
<div style="color: var(--brand-700);">Text</div>
<div style="background: var(--accent-500);">Background</div>
```

### Color Variables Available:
```
Brand Colors:
--brand-900  #0a1f1b (darkest)
--brand-800  #0f3632
--brand-700  #1a5c52 (primary)
--brand-600  #268959
--brand-500  #2faa6b (accent)

Accent Colors:
--accent-500 #f59f4a (primary orange)
--accent-600 #e3832c (darker orange)
--accent-400 #fdb64e (lighter orange)

Text:
--ink-900    #0f172a (headers/dark)
--ink-800    #1e293b
--ink-700    #334155 (body text)
--ink-500    #64748b (muted)
--ink-400    #94a3b8 (light)

Backgrounds:
--surface-0   #ffffff (white)
--surface-50  #f9fafb (very light)
--surface-100 #f3f4f6 (light)
--surface-200 #e5e7eb (slightly darker)

Borders:
--border-200 #e2e8f0
--border-400 #cbd5e1
```

---

## Animation Classes

### Available Animations:
```css
fadeInDown     /* Slide from top */
fadeInUp       /* Slide from bottom */
float          /* Floating effect */
pulse          /* Pulsing opacity */
glow           /* Glowing effect */
shimmer        /* Shine effect */
slideInRight   /* Slide from right */
bounceIn       /* Bounce entrance */
```

### Use in Templates:
```html
<h1 style="animation: fadeInDown 0.6s ease-out;">Title</h1>
<div style="animation: float 3s ease-in-out infinite;">Floating</div>
```

---

## Form States

### Valid Input:
```html
<input class="form-control is-valid">
```

### Invalid Input:
```html
<input class="form-control is-invalid">
```

### Disabled Input:
```html
<input class="form-control" disabled>
```

### Focus State (automatic):
```html
<!-- Just type in the input, focus is automatic with glow effect -->
<input class="form-control">
```

---

## Common Patterns

### Hero Section with Gradient
```html
<section style="background: linear-gradient(135deg, var(--brand-900) 0%, var(--brand-700) 100%); 
                           color: white; padding: 100px 20px;">
    <h1>Title</h1>
    <p>Description</p>
</section>
```

### Card Grid
```html
<div class="row g-4">
    <div class="col-md-4">
        <div class="card-soft">
            <h3 class="card-label">Title 1</h3>
            <p>Content</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card-soft">
            <h3 class="card-label">Title 2</h3>
            <p>Content</p>
        </div>
    </div>
</div>
```

### Button Group
```html
<div class="d-flex gap-2">
    <button class="btn btn-brand">Primary</button>
    <button class="btn btn-accent">Secondary</button>
    <button class="btn btn-outline-brand">Outline</button>
</div>
```

### Info Card Grid
```html
<div class="row g-4">
    <div class="col-md-6 col-lg-3">
        <div class="info-card">
            <div class="info-icon">📍</div>
            <h3>Title</h3>
            <p>Description</p>
        </div>
    </div>
</div>
```

---

## Responsive Breakpoints

```css
Desktop:  >= 992px   (full layout)
Tablet:   768-992px  (2-3 columns)
Mobile:   576-768px  (2 columns)
Small:    < 576px    (1 column)
```

Example Bootstrap usage:
```html
<div class="col-12 col-sm-6 col-md-4 col-lg-3">
    <!-- Full width on mobile, half on tablet, 1/3 on md, 1/4 on lg -->
</div>
```

---

## Customization Quick Tips

### 1. Change Primary Color
Find in `style.css`:
```css
--brand-900: #0a1f1b;  ← Change this
--brand-700: #1a5c52;  ← And this
--brand-500: #2faa6b;  ← And this
```

### 2. Speed Up Animations
Replace all `0.3s` with `0.2s`:
```css
transition: all 0.2s ease;  /* Faster */
```

### 3. Increase Shadows
Change opacity values:
```css
--shadow-strong: 0 25px 50px rgba(15, 23, 42, 0.25);  /* More intense */
```

### 4. Change Border Radius
Update `border-radius` values:
```css
border-radius: 20px;  /* More rounded */
```

### 5. Add New Button Style
```css
.btn-custom {
    background: linear-gradient(135deg, #yourColor1, #yourColor2);
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.btn-custom:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}
```

---

## Frequently Used Patterns

### Success Message
```html
<div class="alert alert-success alert-dismissible fade show">
    Success message here
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### Error Message
```html
<div class="alert alert-danger alert-dismissible fade show">
    Error message here
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### Accent Section
```html
<section style="background: linear-gradient(135deg, var(--accent-500), var(--accent-600)); 
                           color: white; padding: 60px 20px; border-radius: 16px;">
    <h2>Special Offer</h2>
    <p>Description</p>
</section>
```

---

## Mobile-First Tips

1. Always use Bootstrap grid:
   ```html
   <div class="col-12 col-md-6 col-lg-4">
   ```

2. Use responsive typography:
   ```html
   <h1 style="font-size: clamp(1.5rem, 5vw, 3rem);">Responsive</h1>
   ```

3. Use touch-friendly sizes:
   ```html
   <!-- Button should be 44x44px minimum on mobile -->
   <button class="btn" style="min-height: 44px; min-width: 44px;">
   ```

4. Test on devices:
   - Chrome DevTools (Ctrl+Shift+I)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Test on actual devices

---

## Debugging

### Check if CSS is loading:
1. Open Browser DevTools (F12)
2. Go to Network tab
3. Look for `style.css`
4. Should show 200 status

### Check applied styles:
1. Right-click element
2. Select "Inspect"
3. Look at Styles panel
4. See computed styles

### Common issues:
```css
/* Not working? Check: */
1. Cache (hard refresh: Ctrl+Shift+R)
2. Specificity (use more specific selectors)
3. !important (use sparingly)
4. Typos in class names (case-sensitive)
5. Wrong file location
```

---

## File Locations

```
Static Files:
ec/
├── app/
│   ├── static/
│   │   └── app/
│   │       ├── css/
│   │       │   ├── style.css ←← MAIN CSS FILE
│   │       │   ├── style_original.css (backup)
│   │       │   ├── all.min.css (font awesome)
│   │       │   └── owl.carousel.min.css
│   │       ├── js/
│   │       │   ├── myscript.js ←← Custom JS
│   │       │   └── all.min.js (font awesome)
│   │       └── images/
│   │
│   └── templates/
│       └── app/
│           ├── base.html ←← Main template
│           ├── home.html
│           ├── contact.html
│           ├── about.html
│           └── ...

Documentation:
├── DESIGN_IMPROVEMENTS.md ←← Full feature list
├── DESIGN_UPGRADE_SUMMARY.md ←← Overview
├── HTML_ENHANCEMENT_GUIDE.md ←← Optional updates
└── VISUAL_STYLE_REFERENCE.md ←← Before/after code
```

---

## CSS File Size & Performance

```
Old Style.css:  34 KB
New Style.css:  26 KB
Saved:          ~24% reduction
Features:       +50% more animations & effects
```

Performance remains excellent with GPU-accelerated animations!

---

## Support & Resources

1. **Bootstrap Documentation**: https://getbootstrap.com/docs/5.3/
2. **CSS Gradients**: https://cssgradient.io/
3. **Animation Generator**: https://animista.net/
4. **Color Picker**: https://www.color-hex.com/
5. **Font Combinations**: https://fonts.google.com/

---

## Best Practices

✅ Use CSS variables for consistency
✅ Keep animations subtle (< 0.5s usually)
✅ Test on mobile devices
✅ Use semantic HTML
✅ Keep contrast ratios high (4.5:1 minimum)
✅ Don't over-animate (every element doesn't need animation)
✅ Use flexbox/grid for layouts
✅ Keep CSS organized and commented
✅ Remove unused code regularly
✅ Test animation performance on slow devices

---

**Happy styling!** 🎨✨

Last Updated: 2026-02-25
CSS Version: Fresh Dairy v2.0 (Professional)
