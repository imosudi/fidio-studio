# Fídíò Brand Assets & Directory Structure

This directory contains the production vector SVG assets, color palettes, typography specifications, design tokens, and brand guidelines for **Fídíò** and **Fídíò Studio**.

---

## Directory Overview

```
branding/
├── README.md                          # Asset manifest & usage guide
├── brand-guidelines.md                # Comprehensive brand identity standards
├── tokens.json                        # Machine-readable JSON design tokens
├── brand-board.svg                    # Conceptual product UI brand board SVG
│
├── logo/                              # Official Vector Logos
│   ├── fidio-wordmark-dark.svg        # Primary dark-surface wordmark
│   ├── fidio-wordmark-light.svg       # Light-surface wordmark
│   ├── fidio-wordmark-mono-dark.svg   # Monochrome white wordmark
│   ├── fidio-wordmark-mono-light.svg  # Monochrome obsidian wordmark
│   ├── fidio-wordmark-accent.svg      # Full gradient wordmark
│   ├── fidio-technical.svg            # Plain ASCII 'fidio' technical wordmark
│   ├── fidio-symbol.svg               # Standalone dual-playhead symbol
│   ├── fidio-symbol-mono.svg          # Monochrome symbol
│   └── fidio-app-icon.svg             # Square app icon
│
├── favicon/                           # Web & Browser Assets
│   ├── favicon.svg                    # Scalable vector favicon
│   └── fidio-mark.svg                 # Compact browser mark
│
├── social/                            # Social & OpenGraph Assets
│   ├── fidio-social-avatar.svg        # Social profile avatar
│   └── fidio-og-template.svg          # OpenGraph card template
│
├── palette/                           # Swatches
│   └── colors.svg                     # Visual color palette matrix SVG
│
└── typography/                        # Type Specs
    └── typography.svg                 # Typography specimen SVG
```

---

## Naming Conventions & Usage

- **User-Facing Product & Marketing:** Use **Fídíò** / **Fídíò Studio** (with acute accents over both `í`s).
- **Technical Infrastructure & Code:** Use **`fidio`** (plain ASCII). Never use accented characters in code identifiers, package names, environment keys, Docker tags, or URLs.
