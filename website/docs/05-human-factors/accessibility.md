# Accessibility

**KOSMOS for Everyone**

:::info Inclusive Design
    KOSMOS is committed to WCAG 2.1 AA compliance, ensuring the platform is usable by people with diverse abilities.

---

## Compliance Standards

| Standard | Level | Status |
|----------|-------|--------|
| WCAG 2.1 | AA | ✅ Target |
| WCAG 2.1 | AAA | 🟡 Partial |
| Section 508 | Full | ✅ Target |
| EN 301 549 | Full | ✅ Target |

---

## Visual Accessibility

### Color and Contrast

```yaml
# accessibility-config.yaml
visual:
  contrast:
    minimum_ratio: 4.5  # WCAG AA for normal text
    large_text_ratio: 3.0
    ui_components: 3.0
  
  color_independence:
    # Never use color alone to convey information
    require_secondary_indicator: true
    examples:
      - error: red + icon + text
      - success: green + icon + text
      - warning: yellow + icon + text
```

### High Contrast Mode

```css
/* High contrast theme */
[data-theme="high-contrast"] {
  --text-primary: #FFFFFF;
  --text-secondary: #F0F0F0;
  --background-primary: #000000;
  --background-secondary: #1A1A1A;
  --accent: #FFD93D;
  --error: #FF6B6B;
  --success: #51CF66;
  --border: #FFFFFF;
  --focus-ring: 3px solid #FFD93D;
}
```

### Text Scaling

- Base font size: 16px minimum
- All text scalable to 200% without loss of functionality
- No text in images (except logos)
- Line height minimum 1.5 for body text

---

## Motor Accessibility

### Keyboard Navigation

All functionality available via keyboard:

| Category | Requirement | Implementation |
|----------|-------------|----------------|
| Focus indicators | Visible on all interactive elements | 3px outline, high contrast |
| Tab order | Logical, follows visual layout | Semantic HTML + tabindex |
| Skip links | Bypass repeated navigation | Hidden until focused |
| No timing | No time-limited interactions | Extend or disable timers |

### Focus Management

```javascript
// Focus trap for modals
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  element.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      } else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  });
}
```

### Touch Targets

- Minimum size: 44×44px
- Spacing between targets: 8px minimum
- No hover-only interactions

---

## Screen Reader Support

### Semantic HTML

```html
<!-- Proper heading hierarchy -->
<main>
  <h1>Dashboard</h1>
  <section aria-labelledby="tasks-heading">
    <h2 id="tasks-heading">Active Tasks</h2>
    <!-- content -->
  </section>
</main>

<!-- Accessible form -->
<form>
  <div role="group" aria-labelledby="contact-info">
    <span id="contact-info">Contact Information</span>
    <label for="email">Email</label>
    <input id="email" type="email" aria-describedby="email-hint" required>
    <span id="email-hint">We'll never share your email</span>
  </div>
</form>
```

### ARIA Implementation

```yaml
# aria-guidelines.yaml
aria:
  landmarks:
    - role: banner (header)
    - role: navigation
    - role: main
    - role: complementary (sidebar)
    - role: contentinfo (footer)
  
  live_regions:
    notifications: aria-live="polite"
    errors: aria-live="assertive"
    loading: aria-busy="true"
  
  states:
    expanded: aria-expanded
    selected: aria-selected
    disabled: aria-disabled
    hidden: aria-hidden
```

### Screen Reader Testing

| Reader | Platform | Status |
|--------|----------|--------|
| NVDA | Windows | ✅ Tested |
| JAWS | Windows | ✅ Tested |
| VoiceOver | macOS/iOS | ✅ Tested |
| TalkBack | Android | ✅ Tested |

---

## Cognitive Accessibility

### Clear Language

- Plain language for all UI text
- Avoid jargon without explanation
- Consistent terminology throughout
- Error messages explain how to fix

### Predictable Behavior

```yaml
# cognitive-accessibility.yaml
predictability:
  navigation:
    consistent_location: true
    no_unexpected_context_changes: true
  
  inputs:
    clear_labels: true
    visible_instructions: true
    error_prevention: true
    
  feedback:
    immediate_confirmation: true
    clear_success_states: true
    undo_available: true
```

### Reduced Motion

```css
/* Respect user preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Audio and Video

### Captions and Transcripts

| Media | Requirement | Implementation |
|-------|-------------|----------------|
| Pre-recorded video | Captions | Auto-generated + manual review |
| Live video | Captions | Real-time captioning |
| Audio content | Transcript | Full text transcript |
| Video description | Audio description | Optional track |

### Audio Controls

- No auto-playing audio
- Volume controls always accessible
- Mute option prominent
- Audio indicators visible

---

## Agent Accessibility

### Voice Interaction

```yaml
# voice-accessibility.yaml
voice:
  input:
    speech_to_text: enabled
    command_mode: "Hey KOSMOS"
    dictation_mode: "Start dictation"
  
  output:
    text_to_speech: enabled
    rate_control: adjustable
    voice_selection: multiple_options
```

### AI Response Accessibility

- All AI responses available as text
- Complex outputs (charts, diagrams) have text descriptions
- Response length options (concise, detailed)
- Reading level adjustment available

---

## Testing and Validation

### Automated Testing

```bash
# Run accessibility audit
npm run a11y:audit

# Tools used:
# - axe-core for automated checks
# - pa11y for CI integration
# - Lighthouse for overall score
```

### Manual Testing Checklist

```
□ Keyboard-only navigation complete
□ Screen reader announces all content correctly
□ Focus order is logical
□ Color contrast meets requirements
□ Text scales to 200% without breaking
□ All images have alt text
□ Forms have proper labels
□ Errors are clearly communicated
□ No content flashes more than 3 times/second
□ Session timeouts can be extended
```

### Accessibility Statement

Available at `/accessibility` with:
- Compliance status
- Known limitations
- Feedback mechanism
- Contact information

---

## See Also

- [Ergonomic Design](ergonomic-design)
- [UI/UX Guidelines](ui-ux-guidelines)
- [Iris Interface Agent](../02-architecture/agents/iris-interface)

---

**Last Updated:** December 2025
