You are the lead brand designer and design-system engineer for **Fídíò**, an AI-powered creative production platform.

Your task is to design and implement the complete initial **Fídíò brand identity system** as production-ready SVG assets and supporting brand documentation.

# 1. BRAND

Brand name:

**Fídíò**

Technical identifier:

**fidio**

MVP product:

**Fídíò Studio**

Future product architecture:

- Fídíò
- Fídíò Studio
- Fídíò Engine
- Fídíò API
- Fídíò Cloud
- Fídíò Enterprise

Primary tagline:

**Imagine. Create. Fídíò.**

Product descriptor:

**AI-powered creative production**

The brand must communicate:

- cinematic
- minimal
- intelligent
- expressive
- premium
- modern
- technically credible
- internationally usable

Do NOT make the identity look like a generic AI startup.

Avoid:
- robot imagery
- brains
- circuit-board clichés
- generic play-button logos
- excessive neon
- excessive gradients
- stock-video aesthetics
- overly complex symbols
- childish/gaming aesthetics

# 2. CORE BRAND IDEA

Fídíò transforms an idea into finished media.

The conceptual flow is:

Idea
→ Intelligence
→ Creation
→ Composition
→ Media

The identity should subtly communicate:

- motion
- frames
- temporal progression
- synchronized creation
- intelligent orchestration

The acute accents over the two **í** characters are a key visual opportunity.

Treat them as a deliberate brand motif.

They may resemble:
- synchronized playheads
- cinematic frame markers
- motion indicators
- paired timeline markers

The motif must remain elegant and subtle rather than literal.

# 3. WORDMARK

Primary wordmark:

**Fídíò**

Requirements:

- Preserve the acute accents exactly.
- The two accented í characters must remain visually intentional.
- Explore custom treatment of the accent marks.
- Maintain excellent kerning.
- Use large typography.
- The wordmark must work at both large and small sizes.
- The wordmark must remain recognizable in monochrome.
- Do not distort the letters unnecessarily.

Create variants:

1. Primary dark-background wordmark
2. Light-background wordmark
3. Monochrome black
4. Monochrome warm-white
5. Accent version
6. Compact wordmark
7. Icon/monogram
8. App icon

Technical wordmark:

**fidio**

This must be plain ASCII and must NOT contain accent characters.

Use `fidio` for:
- repositories
- package names
- Docker images
- environment variables
- infrastructure
- URLs
- API identifiers

Use **Fídíò** for:
- marketing
- application UI
- documentation headings
- presentations
- brand communications

# 4. VISUAL LANGUAGE

Foundation:

Near-black / obsidian.

Typography:

Warm white.

Signature accent:

Choose ONE vivid accent color.

The accent should feel:
- cinematic
- energetic
- intelligent
- contemporary

Prefer a distinctive violet/magenta/coral direction over conventional corporate blue.

Do not use multiple competing accent colors.

Recommended conceptual palette:

- Obsidian
- Warm White
- Signature Accent
- Optional neutral gray scale

The exact HEX values should be selected by the design agent based on visual harmony.

# 5. TYPOGRAPHY

Establish a typography system.

Primary brand typography should be:
- contemporary
- geometric or humanist
- highly legible
- premium
- suitable for large editorial typography

Application typography should prioritize:
- readability
- accessibility
- compact UI rendering

Prefer open-source fonts where possible.

If using an external font, document the license and source.

# 6. LOGO SYSTEM

Create a coherent logo family.

Required:

### A. Full wordmark

Fídíò

### B. Technical wordmark

fidio

### C. Symbol

Create a standalone symbol derived from the Fídíò visual concept.

The symbol should NOT simply be:
- a play button
- a camera
- a film reel
- a generic letter F

Instead, explore the synchronized accent/playhead/frame concept.

### D. Monogram

Develop a compact Fídíò monogram suitable for:
- favicon
- mobile application
- browser tab
- social avatar
- small UI surfaces

### E. App icon

Create a square app icon using:
- near-black foundation
- signature accent
- simplified Fídíò symbol

It must remain legible at small dimensions.

# 7. SVG REQUIREMENTS

All final logo assets MUST be SVG.

SVG files must be:

- valid XML
- editable
- scalable
- vector-only
- free from embedded raster images
- free from unnecessary metadata
- free from excessive path complexity
- suitable for web use
- suitable for Figma import
- suitable for browser rendering

Where possible:
- use `<text>` only in editable/source versions
- provide outlined/path versions for distribution
- use semantic grouping
- use consistent viewBox dimensions
- avoid unnecessary transforms
- avoid embedded base64 assets

Do not rasterize the logo.

# 8. REQUIRED FILES

Create the following structure:

branding/
├── README.md
├── brand-guidelines.md
│
├── logo/
│   ├── fidio-wordmark-dark.svg
│   ├── fidio-wordmark-light.svg
│   ├── fidio-wordmark-mono-dark.svg
│   ├── fidio-wordmark-mono-light.svg
│   ├── fidio-wordmark-accent.svg
│   ├── fidio-technical.svg
│   ├── fidio-symbol.svg
│   ├── fidio-symbol-mono.svg
│   └── fidio-app-icon.svg
│
├── favicon/
│   ├── favicon.svg
│   └── fidio-mark.svg
│
├── social/
│   ├── fidio-social-avatar.svg
│   └── fidio-og-template.svg
│
├── palette/
│   └── colors.svg
│
└── typography/
    └── typography.svg

If the repository already has an established directory structure, integrate with it rather than unnecessarily restructuring the repository.

# 9. DESIGN TOKENS

Create machine-readable brand tokens where practical.

Define:

- brand colors
- neutral colors
- typography
- spacing
- corner radius
- logo clear space
- icon sizing
- accent usage

If the project already uses a token format, follow it.

Otherwise create:

branding/tokens.json

Example structure:

{
  "color": {},
  "typography": {},
  "spacing": {},
  "logo": {}
}

Do not invent excessive design tokens for elements that are not required.

# 10. BRAND GUIDELINES

Create concise but professional documentation covering:

## Brand essence

What Fídíò represents.

## Logo usage

Explain:
- clear space
- minimum size
- acceptable backgrounds
- monochrome usage
- accent usage

## Incorrect usage

Document examples such as:
- stretching
- rotating
- recoloring
- excessive effects
- removing the accent motif
- changing letter spacing
- placing on insufficient contrast

## Typography

Document:
- display typography
- UI typography
- hierarchy

## Color

Document:
- HEX
- RGB
- HSL where useful
- accessibility considerations

## Voice

Fídíò should sound:

- confident
- concise
- intelligent
- creative
- human
- optimistic

Avoid:
- exaggerated AI claims
- excessive buzzwords
- hype
- technical jargon in consumer-facing copy

# 11. BRAND VOICE

Preferred:

"Turn your ideas into compelling video."

"Imagine. Create. Fídíò."

"From idea to finished media."

Avoid:

"Revolutionary next-generation AI-powered disruption."

The brand should communicate capability through clarity rather than hype.

# 12. PRODUCT UI APPLICATION

Create a small SVG brand board demonstrating how the identity translates into the Fídíò Studio interface.

Include:

- application header
- wordmark
- primary action
- project card
- generation status
- timeline/playhead concept

Keep it conceptual and minimal.

Do not create an entire UI design system.

# 13. SVG QUALITY CONTROL

After generating all SVGs:

1. Parse every SVG.
2. Validate XML.
3. Confirm viewBox exists.
4. Confirm no raster images are embedded.
5. Confirm no accidental external dependencies.
6. Confirm all primary SVGs render correctly.
7. Confirm the Fídíò accents are preserved.
8. Confirm technical `fidio` assets contain only ASCII text.
9. Check light/dark contrast.
10. Check small-size readability.

If SVG tooling is available, use it for validation.

# 14. BRAND CONSISTENCY

Every asset must belong to the same visual system.

The following must feel related:

Fídíò
Fídíò Studio
Fídíò Engine
Fídíò API
Fídíò Cloud

Do not create separate visual identities for individual products.

# 15. IMPORTANT DESIGN PRINCIPLE

The logo should still look credible if the company eventually expands beyond video.

The brand should therefore communicate:

CREATION + MOTION + INTELLIGENCE

rather than simply:

VIDEO + CAMERA + PLAY

This distinction is essential.

# 16. IMPLEMENTATION RULE

Before creating assets:

1. Inspect the repository.
2. Read AGENTS.md.
3. Inspect existing frontend/design conventions.
4. Check whether a branding directory already exists.
5. Avoid overwriting existing assets without understanding their purpose.

Then create the branding system.

Do not merely describe proposed logos.

Actually create the SVG files.

# 17. FINAL DELIVERABLE

At completion provide:

1. All production SVG assets.
2. Brand guidelines.
3. Color palette.
4. Typography specification.
5. Design tokens.
6. README explaining the branding structure.
7. A visual brand board.
8. Validation results.
9. List of any assumptions.
10. List of any assets that require manual designer refinement.

The final result should be suitable as the initial professional brand foundation for **Fídíò Studio** and scalable to a future Fídíò platform.