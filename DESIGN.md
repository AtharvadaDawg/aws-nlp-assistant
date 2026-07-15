---
name: AWS NLP Assistant - Cyber Brutalism
description: Raw, dark, high-contrast infrastructure queries. Deep blacks. Neon accents. Geometric brutalist forms.
colors:
  bg: "#0a0a0a"
  bg-raised: "#1a1a1a"
  bg-card: "#151515"
  neon-cyan: "#00d9ff"
  neon-cyan-dark: "#00a8cc"
  neon-lime: "#39ff14"
  neon-pink: "#ff006e"
  neon-yellow: "#ffff00"
  neon-white: "#f0f0f0"
  ink: "#f0f0f0"
  ink-muted: "#888888"
  border: "#333333"
  success: "#39ff14"
  warning: "#ffff00"
  critical: "#ff006e"
typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(1.5rem, 3vw, 2rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0.01em"
  body-sm:
    fontFamily: "Courier New, monospace"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.05em"
  label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.1em"
    textTransform: "uppercase"
rounded:
  sm: "0px"
  md: "2px"
  lg: "4px"
  full: "0px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.neon-cyan}"
    textColor: "{colors.bg}"
    rounded: "0px"
    padding: "12px 24px"
    fontWeight: 700
    textTransform: "uppercase"
    letterSpacing: "0.08em"
    border: "2px solid {colors.neon-cyan}"
  button-primary-hover:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.neon-cyan}"
    border: "2px solid {colors.neon-cyan}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.neon-white}"
    rounded: "0px"
    padding: "12px 24px"
    border: "2px solid {colors.border}"
    fontWeight: 700
  badge-success:
    backgroundColor: "{colors.neon-lime}"
    textColor: "{colors.bg}"
    rounded: "0px"
    padding: "6px 12px"
    fontWeight: 700
    border: "1px solid {colors.neon-lime}"
  badge-warning:
    backgroundColor: "{colors.neon-yellow}"
    textColor: "{colors.bg}"
    rounded: "0px"
    padding: "6px 12px"
    fontWeight: 700
    border: "1px solid {colors.neon-yellow}"
  badge-critical:
    backgroundColor: "{colors.neon-pink}"
    textColor: "{colors.bg}"
    rounded: "0px"
    padding: "6px 12px"
    fontWeight: 700
    border: "1px solid {colors.neon-pink}"
  card:
    backgroundColor: "{colors.bg-card}"
    rounded: "0px"
    padding: "0px"
    border: "1px solid {colors.border}"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.neon-cyan}"
    rounded: "0px"
    padding: "8px 16px"
    border: "2px solid {colors.neon-cyan}"
    fontWeight: 600
---

## Overview

AWS NLP Assistant is a technical tool for DevOps and SRE professionals. The design prioritizes clarity, scanability, and confident authority—users need instant visual understanding of infrastructure status during daily standups.

**Design principles in action:**
- **Calm, focused violet** (#7547d0) carries the brand voice; the surface stays pure white so the primary color dominates.
- **System status lives in color**: green (healthy), amber (warning), red (critical). These are the only places color speaks "state," keeping cognitive load low.
- **Clean sans-serif (Inter)** with tight display tracking and generous body line-height for rapid scanning at arm's length.
- **Purposeful motion** (300–500ms, ease-out curves) on reveals and transitions—AI thinking steps fade in, metrics slide, chat messages appear in sequence—but motion never delays comprehension.
- **Full palette across chat, metrics, and data viz**: purple for brand authority, blue accents for secondary info, status colors for infrastructure health.

---

## Colors

The palette is built in OKLCH for perceptual consistency:

**Primary Brand**
- `oklch(0.56 0.12 294)` → #7547d0 — violet anchor. Carries badges, primary buttons, brand presence. Never diluted; only used at full saturation.
- `oklch(0.62 0.10 294)` → #9570e3 — lighter violet for hover/focus states.

**Accent (Data Viz & Secondary)**
- `oklch(0.58 0.13 260)` → #4f96d4 — cool blue, distinct from purple. Used for secondary metrics, alt data series in charts, secondary badges.
- `oklch(0.66 0.10 260)` → #7eb3e8 — light blue for hover states on accent elements.

**Status & Semantic**
- `oklch(0.61 0.19 140)` → #10b981 — green for healthy systems, running instances, success states.
- `oklch(0.70 0.20 90)` → #f59e0b — amber for warnings, degraded performance, attention needed.
- `oklch(0.60 0.22 29)` → #ef4444 — red for critical errors, failures, down services.

**Neutral & Architectural**
- `oklch(1.00 0.00 0)` → #ffffff — pure white. Body background. Lets brand colors carry voice.
- `oklch(0.98 0.01 294)` → #f9f7fb — barely-tinted surface. Cards, panels, input backgrounds. Subtly echoes brand hue.
- `oklch(0.18 0.00 0)` → #1a1046 — near-black. Body text. 7:1 contrast on white.
- `oklch(0.55 0.01 294)` → #8b7ec8 — muted text. Secondary labels, hints, timestamps. 3.5:1 contrast on white.

**Usage guidelines:**
- Filled buttons and status pills: white text on saturated color (primary, status colors). Never dark text on saturated fills.
- Text links: primary violet, underline on hover.
- Data viz (Recharts): primary for line 1, accent-blue for line 2. Status colors for categorical breakdowns (healthy/warning/critical).

---

## Typography

**Type Hierarchy**
- **Display** (clamp 2–3rem): h1 headlines, major section breaks. 600 weight, tight tracking (-0.02em). Sets the confident tone.
- **Headline** (clamp 1.5–2rem): h2/h3 subsections, chat response headers. 600 weight, tighter tracking (-0.01em).
- **Body** (1rem): conversation text, metric labels, descriptions. 400 weight, generous 1.6 line-height for scannability.
- **Body Small** (0.875rem): secondary text, timestamps, muted hints.
- **Label** (0.75rem): all-caps badges, status pills, button text. 600 weight, wider tracking (0.02em). Used for metadata.

**Font Stack**
Inter with safe fallbacks to system fonts. Keep text rendering consistent across browsers; use `font-smoothing: antialiased` on the body.

**Line Length & Wrapping**
- Chat messages and prose: cap at 65–75 characters. Use flexbox with max-width constraints.
- Headings: use `text-wrap: balance` to avoid widows on wrapped h1–h3.

---

## Elevation

AWS NLP Assistant uses flat design with soft shadows for depth. No gradient fills, no glassmorphism.

**Shadow Vocabulary**
- **sm**: 0 1px 2px rgba(0,0,0,0.04) — subtle depth on interactive elements.
- **md**: 0 4px 6px rgba(0,0,0,0.07) — card and panel shadows.
- **lg**: 0 10px 15px rgba(0,0,0,0.10) — modals, dropdowns, elevated overlays.

Shadows use neutral black at low opacity; never colored shadows.

**Focus States**
- All interactive elements (buttons, links, inputs, focusable divs): 2px solid border in primary violet, 4px padding adjustment. No outline; use border instead for better visual affordance.

---

## Components

**Buttons**
- **Primary**: violet bg, white text, 10px vertical / 20px horizontal padding, 6px radius. Hover: lighter violet.
- **Secondary**: surface bg, dark text, same padding and radius. Hover: slightly darker surface.
- **Icon Button**: 40x40 touch target, violet icon, hover background subtle.

**Badges & Status Pills**
- **Skill Badge** (thinking step): "🖥️ Checking system health" → surface bg with 0.875rem label weight, subtle left border (4px, primary).
- **Status Pill** (health): success/warning/critical colors, white text, rounded-full, 4–12px padding. Always use pill shape; never rectangular.
- **Metric Badge**: primary violet fill, white text, 6px radius, 6px vertical / 14px horizontal.

**Chat Message**
- **User**: right-aligned, primary violet bg, white text, 12px radius, generous 16px padding, 280px max-width.
- **Assistant**: left-aligned, surface bg, dark text, 12px radius, 16px padding, 440px max-width.
- Thinking steps fade in above assistant message, small label font, 0.75 opacity, 200ms fade-in.

**Cards & Metrics**
- **Card**: surface bg, 12px radius, 16px padding, 1px border in subtle primary (hue 294, L 0.92, C 0.04).
- **Metric Card**: card wrapper, grid 2-column layout on tablet+, single column on mobile. Headline number (0.875 size), label below, optional mini-chart (Recharts, 200px height max).
- **Mini Chart**: Recharts bar/line, primary line, accent-blue alt series, no legend (legend in prose nearby), responsive width, 120px min-height.

**Input**
- **Text Input**: surface bg, 1px border in muted color on default, 2px primary border on focus, 8px horizontal padding, 10px vertical, 6px radius. Placeholder text in muted. No shadow.

---

## Do's and Don'ts

**Do:**
- Use violet (#7547d0) for primary CTAs, thinking badges, brand moments.
- Use status colors (green/amber/red) to communicate infrastructure health. Never for "flavor."
- Keep surfaces clean. One card per logical section; never nested cards.
- Pair display headings with tight tracking. Never -0.05em or tighter; -0.02em is the floor.
- Use generous spacing (16px–24px) between sections. Rhythm beats density.
- Motion on reveals (chat messages, thinking steps, metrics sliding in). No motion on layout shifts or scroll.

**Don't:**
- Use gradient fills, glassmorphism, or decorative borders (no side-stripe accents).
- Pair dark text with saturated color fills; always white text on primary, status, or accent fills.
- Tint the background toward warmth "for elegance"; pure white is the architectural choice.
- Animate layout properties (width, height, top/left). Only transform, opacity, and blur.
- Use more than 3 accent colors across the interface (primary + accent-blue + status = 3 + neutrals).
- Over-round corners (cards stay 12px; full-pill is for badges only).
