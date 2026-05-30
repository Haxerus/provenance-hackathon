# ProvenanceChain — Design System

## Philosophy

The aesthetic north star is a **fusion of Vercel and Linear**: clean, minimal, high-contrast, fast, and keyboard-first. Restraint that still has presence. Nothing decorative; everything legible. The interface should feel calm and trustworthy and get out of the user's way, because the user came to answer one question — *is this product genuinely Canadian, and can I trust the chain?*

The UI is **grayscale by default**. Colour is reserved for signal, and it appears in exactly three places:

1. **Node type** — in the graph canvas, each node carries its action-type colour as a small **solid swatch token** in the header (plus a type label in the same colour). This is the only categorical colour.
2. **Anomaly / attack states** — error and warning states on graph nodes and edges.
3. **Verification verdict** — a single small **status dot** (Vercel "deployment ready" style): green when the chain verifies, red when it does not. This is the *only* colour permitted outside the graph canvas, and it is deliberately tiny. The badge text itself stays ink; only the dot carries colour.

Everything else — nav, product headers, stats, designation badges, panels, buttons, forms — is black, white, and gray. Because colour is rationed, every coloured pixel means something: a node's type, a problem, or the verdict.

**Two things to communicate on every node**: what **type** it is, and whether it is **healthy**. They use separate visual channels so they never compete:

- **Type** → a solid colour swatch token + a colour-matched label in the node header.
- **Health** → the card border colour + background tint.

The border is therefore reserved entirely for health state. There are **no coloured side-stripes** anywhere; type lives in the swatch, not in an accent border.

---

## Colour Tokens

### Base palette — grayscale only

A cool-neutral ramp (Linear-flavoured), used everywhere outside the graph. Contrast-checked: text tokens meet WCAG AA (≥4.5:1) at body sizes on `--color-surface`.

| Token | Hex | Usage | Notes |
|---|---|---|---|
| `--color-bg` | `#FFFFFF` | Page background | |
| `--color-surface` | `#F8F9FB` | Card, panel, sidebar, input backgrounds | |
| `--color-canvas` | `#EBEBEB` | ReactFlow graph canvas background | |
| `--color-border` | `#E2E4ED` | Subtle borders, dividers (1px) | |
| `--color-border-mid` | `#C8CADE` | Focused inputs, stronger separators | |
| `--color-ink` | `#0F1117` | Primary text, buttons, active labels | |
| `--color-muted` | `#5E6478` | Secondary text, labels, captions, metadata, **placeholders** | ≈5.5:1 on surface — AA at 12px |
| `--color-faint` | `#B0B3C6` | Disabled affordances, decorative dividers — **non-text only** | Fails AA; never use for text the user must read |

No brand colour. No semantic greens or reds outside the graph **except** the verification status dot (below).

> **Contrast rule**: placeholder and helper text use `--color-muted`, not `--color-faint`. `--color-faint` is for non-text UI only (disabled states, hairline decoration). Any text on a tinted background must clear 4.5:1; bump toward ink if it is even close.

### Node type accent colours — graph only

Each node shows its type as an **8px solid rounded swatch** in the header, plus a colour-matched uppercase label. The card fill is white in the normal state; the swatch carries the colour, never a side-stripe.

| Action type | Swatch / label colour | Notes |
|---|---|---|
| `raw_material_supply` | `#1B3A6B` navy | |
| `component_manufacture` | `#2D7D46` forest green | Distinct from the verified status dot green |
| `subassembly` | `#9B6800` deep amber | Label meets AA (~4.6:1) on white |
| `final_integration` | `#0F1117` ink (filled dark swatch) | The product leaf — dark swatch + ink label, no special fill |

These colours appear **nowhere else** in the UI.

### Anomaly / attack colours — graph only

Health state overlays the card via the **border + tint** (the type swatch is unaffected; both are visible at once). Severity is encoded on **two channels** so it survives colour-blindness: a colour **and** a shape — a leading severity dot plus, for statistical cases, a dashed border.

| Anomaly type | Node border | Card background | Severity cue | Severity label |
|---|---|---|---|---|
| `invalid_signature` | `#C8202C` 1.5px solid | `#FFF1F2` | ● filled red dot | Critical |
| `parent_hash_mismatch` | `#C8202C` 1.5px solid | `#FFF1F2` | ● filled red dot | Critical |
| `mass_balance_violation` | `#B45309` 1.5px solid | `#FFFBEB` | ◐ half-filled amber dot | Warning |
| `timestamp_anomaly` | `#B45309` 1.5px solid | `#FFFBEB` | ◐ half-filled amber dot | Warning |
| `unknown_supplier` | `#B45309` 1.5px solid | `#FFFBEB` | ◐ half-filled amber dot | Warning |
| `t4_perturbed` / statistical | `#6D28D9` 1.5px **dashed** | `#FAF8FF` | ○ hollow violet dot | Subtle |

Tampered / hash-mismatch **edges**: `#C8202C` 1.5px dashed line.

Clean node default: `#E2E4ED` 1px border, `#FFFFFF` fill, no shadow (sits cleanly on the `#EBEBEB` canvas).

**Selection is shown by a ring shadow, not a border colour**, so it composes with anomaly borders: `box-shadow: 0 0 0 3px rgba(15,17,23,0.12)` (+ the node keeps whatever health border it has). A clean selected node also gets a `#0F1117` 1.5px border.

### Verification verdict — the one semantic colour outside the graph

A single small **status dot** beside the verdict text, in the spirit of a Vercel deployment indicator. Text stays ink; only the dot is coloured.

| State | Dot | Hex | Text (always ink) |
|---|---|---|---|
| Verified / chain valid | ● solid | `#2DA44E` green | "Chain verified" |
| Invalid / tampering found | ● solid | `#C8202C` red | "Chain invalid" |
| Verifying | ◐ pulsing | `--color-muted` | "Verifying…" |

The dot is the only place green or red leaves the graph. Keep it ~8px. Do not colour the surrounding text, the designation badge, or the percentage; the dot does the work.

---

## What stays grayscale

| Element | Treatment |
|---|---|
| Nav bar | White background, ink text, gray border |
| "ProvenanceChain" wordmark | Ink text only — no logo, no icon |
| Product name, attestation ID | Ink + muted gray; IDs/hashes in mono |
| Canadian content % (58.4%) | **Ink `#0F1117`** — large, bold, tabular figures, no colour |
| Designation badge (made_in_canada, etc.) | Gray pill — ink text, `--color-border` border, `--color-surface` background |
| Chain validity badge | Ink text + a coloured **status dot** (green/red) — the dot is the only colour |
| Stats (nodes, suppliers, cost, anomaly count) | Ink numbers, tabular figures — anomaly count stays ink |
| Primary buttons (Verify, Submit, Continue) | `#0F1117` background, white text |
| Secondary buttons | White background, ink border, ink text |
| Form inputs, dropdowns | White background, `--color-border-mid` border on focus, ink focus ring |
| Side panel headers | Ink text on white surface |
| Anomaly panel header | Gray surface — title in ink, count in ink |
| Copy/action labels | Ink or muted gray text |

> **The only colour outside the graph** is the verification status dot (green/red) and the anomaly count's optional red emphasis when `chain_valid: false` and anomalies > 0. Everything else is grayscale.

---

## Typography

Three families (within budget): **Inter** for UI, **a monospace** for cryptographic data, and that's it.

- **UI** — Inter (variable).
- **Mono** — JetBrains Mono or IBM Plex Mono, for `attestation_id`s, SHA-256 hashes, base64 signatures, and public-key fragments. Rendering these in a proportional font reads as amateur and is hard to scan; mono signals "this is verifiable data."
- **Tabular figures** — apply `font-variant-numeric: tabular-nums` to the % hero, the stats row, costs, quantities, and every table column so numbers align and don't jitter.

| Role | Family | Weight | Size | Line height | Tracking |
|---|---|---|---|---|---|
| Data hero (% display) | Inter | 700 Bold | 56px | 1 | -0.02em |
| Page title | Inter | 300 Light | 38px | 1.1 | -0.02em |
| Section heading | Inter | 600 SemiBold | 18px | 1.3 | -0.01em |
| Body | Inter | 400 Regular | 15px | 1.6 | 0 |
| Node title | Inter | 600 SemiBold | 13px | 1.4 | 0 |
| Node meta / row | Inter | 400 Regular | 12px | 1.4 | 0 |
| Caption / muted | Inter | 400 Regular | 12px | 1.4 | 0 |
| Badge / tag | Inter | 500 Medium | 11px | 1 | 0.05em, uppercase |
| Crypto data (ID, hash, sig) | Mono | 400 Regular | 12px | 1.4 | 0 |

> Caption weight is 400 (not 300 Light): light weight at 12px in muted gray drops below readable contrast. Reserve uppercase for labels/badges ≤4 words; never for body copy.

---

## Spacing & Layout

- Base unit: 4px
- Common gaps: 4, 8, 12, 16, 24, 32, 48, 64
- Nav height: 60px
- Product header bar: ~80px
- Side panel width: 340px (desktop)
- Graph canvas: fills remaining width and height
- Card border radius: 10px (nodes), 12px (info cards), 8px (badges/pills)
- Node dimensions (ReactFlow): 220px wide × ~90px tall

### Responsive — purchaser flow is mobile-first

Lookup is QR-driven, so the purchaser view must work on a phone. A tier-N DAG is unusable as the primary surface on a 390px screen.

- **Mobile (< 768px)**: the **verdict + % + designation + anomaly list** is the primary surface, stacked vertically. The graph is secondary — a zoomable/pannable view or a simplified vertical chain reachable from a "View provenance graph" control.
- **Desktop (≥ 1024px)**: graph + 340px detail panel side by side as specified.
- Touch targets ≥ 44×44px. Preserve lookup state if the user is interrupted and returns.

---

## ReactFlow Node Specification

### Node anatomy

```
┌─────────────────────────────────────────┐
│ ▪ TYPE LABEL              ● CA           │  ← 8px swatch + 10px/500 uppercase label (type colour); country dot + code
│                                          │
│ Node Name                                │  ← 13px 600, ink
│ 8 m² · $520 CAD                          │  ← 12px 400, muted, tabular figures
│                                          │
│ ● Anomaly message — shown if flagged     │  ← 11px, severity dot + message (error/warning colour)
└─────────────────────────────────────────┘
 No side-stripe. Type = swatch + label. Health = border + tint.
```

### Node type display labels

| Enum | Display label | Swatch / label colour |
|---|---|---|
| `raw_material_supply` | `RAW MATERIAL` | `#1B3A6B` navy |
| `component_manufacture` | `COMPONENT MFG` | `#2D7D46` forest green |
| `subassembly` | `SUBASSEMBLY` | `#9B6800` deep amber |
| `final_integration` | `FINAL INTEGRATION` | `#0F1117` ink (dark swatch) |

### State precedence (resolves prior contradictions)

The card composes from three independent channels — no rule overrides another:

- **Swatch + label** = action type. Always shown.
- **Border colour** = health. Clean → `#E2E4ED` 1px. Anomaly → severity colour 1.5px (dashed for statistical).
- **Fill** = white by default; tinted **only** by an anomaly (`#FFF1F2` / `#FFFBEB` / `#FAF8FF`).
- **Selection** = ring shadow (and ink border only when otherwise clean), so a selected *and* anomalous node shows both.

`final_integration` is distinguished by its **dark swatch + ink label**, not by a special fill, so it still tints and borders correctly when flagged.

### Country indicator

A small dot + country code (e.g. `● CA` filled / `○ US` hollow). Filled-vs-hollow (not colour) distinguishes Canadian from non-Canadian steps. The dot is gray for all countries — Canadian content is communicated in the header stats, not per-node colour.

---

## States

States are the bulk of the experience; design them, don't ship only the happy path.

### Purchaser

- **Verifying** — status dot pulsing, "Verifying…", skeleton for the graph/panel.
- **Verified** — green dot + "Chain verified", % hero, designation, graph.
- **Invalid** — red dot + "Chain invalid", anomaly list elevated above the graph.
- **Not found** — product/attestation id resolves to nothing: plain message + "Scan another code" / search affordance. (Absence from the anchor registry is *not* an error — an unanchored clean chain is valid; do not show a scary state for it.)
- **Verify failed** — backend/network error: ink message, retry button; never expose raw stack traces.

### Supplier

- **Empty** — no attestations yet: a calm first-run state that explains what an attestation is and a primary "Create attestation" action.
- **Validating / signing** — disabled submit with progress; canonicalization + signature in flight.
- **Signed success** — confirmation with the new attestation id (mono) and a copy affordance.
- **Submit error** — inline, field-anchored messages in plain language.

---

## Interaction Patterns

### Node hover
- `box-shadow: 0 4px 16px rgba(15,17,23,0.08)` lifts the card
- Cursor: pointer

### Node selected
- Ring shadow `box-shadow: 0 0 0 3px rgba(15,17,23,0.12)`; ink 1.5px border only if the node is otherwise clean
- Side panel updates with full attestation details

### Node with anomaly — click
- Side panel switches to anomaly detail view for that node

### Edge (connection)
- Default: `#C8CADE` 1.5px with arrowhead
- Hash-mismatch / tampered: `#C8202C` 1.5px dashed
- Hovered: `#9396A8` 2px

### Focus (keyboard)
- Visible focus ring on all interactive elements: `box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px #0F1117` (ink ring). Full keyboard path through the supplier form and purchaser lookup; `Esc` dismisses panels/dialogs.

---

## Anomaly Type — Display Mapping

| Anomaly type | Severity | Node border | Background tint | Severity cue | Inline message |
|---|---|---|---|---|---|
| `invalid_signature` | Critical | `#C8202C` 1.5px | `#FFF1F2` | ● red | "Signature does not verify" |
| `parent_hash_mismatch` | Critical | `#C8202C` 1.5px | `#FFF1F2` | ● red | "Parent hash mismatch" |
| `mass_balance_violation` | Warning | `#B45309` 1.5px | `#FFFBEB` | ◐ amber | "Over-consumed: X of Y produced" |
| `timestamp_anomaly` | Warning | `#B45309` 1.5px | `#FFFBEB` | ◐ amber | "Timestamp out of expected range" |
| `unknown_supplier` | Warning | `#B45309` 1.5px | `#FFFBEB` | ◐ amber | "Supplier not in registry" |
| `t4_perturbed` | Subtle | `#6D28D9` 1.5px dashed | `#FAF8FF` | ○ violet | "Statistically anomalous" |

The severity cue (dot shape + dashed border) is the colour-independent channel; never rely on hue alone to separate Critical from Warning.

---

## Component Inventory

### Shared
- `<NavBar>` — text wordmark, tab nav, user label
- `<ProductHeaderBar>` — product name + ID (mono), % hero (ink, tabular), designation (gray pill), stats row (tabular)
- `<DesignationBadge type="made_in_canada | product_of_canada | none" />` — always gray
- `<ChainValidityBadge valid={bool} anomalyCount={n} />` — ink text + green/red **status dot**; the dot is the only colour
- `<StatusDot state="verified | invalid | verifying" />` — the Vercel-style verdict dot

### Graph (ReactFlow)
- `<ProvenanceNode>` — base node, props: `actionType`, `country`, `anomalies[]`, `selected`. Type swatch + label header; border/tint health; no side-stripe
- `<ProvenanceEdge>` — default (gray) and tampered (red dashed) variants
- `<GraphLegend>` — action-type swatch key + anomaly severity key; **persistently visible** (comprehension depends on it)

### Supplier flow
- `<AttestationForm>` — stepped form (5 steps), sidebar progress, live preview card
- `<ActionTypeSelector>` — 4 cards, each with the type **swatch token** (no left stripe)
- `<CountrySelect>` — dropdown, no colour treatment
- `<ParentPicker>` — searchable list of existing attestations; selecting a parent **locks the consume-unit to the parent's `output.unit`** (error prevention)
- `<CostFields>` — material_cad, labour_hours, labour_cost_cad (tabular)
- `<OutputFields>` — name, quantity, unit
- **Inline validation**: warn on over-consumption (mass balance) before signing, so the form prevents the very anomalies the backend detects

### Purchaser flow
- `<LookupPage>` — search bar + QR scan note (no QR placeholder graphic); mobile-first verdict-led layout
- `<NodeDetailPanel>` — attestation details, crypto verification status (text + status dot), CA contribution bar (gray), the per-node cost split that feeds the %, parent list, and **copy affordances for IDs/hashes (mono)**
- `<AnomalyPanel>` — chain-invalid header (gray), anomaly list with severity dot + colour label

---

## Do / Don't

| Do | Don't |
|---|---|
| Keep all UI chrome (nav, panels, stats, badges) grayscale | Add brand colour to nav, headers, or buttons |
| Encode node type with a solid colour **swatch token** + matching label, in the graph only | Use a coloured left/right side-stripe on nodes, cards, or selector items |
| Use anomaly colours only on flagged graph nodes and tampered edges | Use red/amber to style the anomaly panel header or nav |
| Show the verdict with a small green/red **status dot**, text in ink | Colour the verdict text, designation, or % figure |
| Encode severity on two channels (colour + dot shape / dashed) | Rely on hue alone to separate Critical from Warning |
| Render IDs, hashes, and signatures in **mono**; numbers with tabular figures | Render cryptographic data in the proportional UI font |
| Use `--color-muted` for any text, including placeholders (AA-safe) | Use `--color-faint` for text the user must read |
| Display the Canadian % hero in ink, large and bold | Colour the % figure |
| Design the empty, loading, not-found, and error states | Ship only the happy path |
| Use text-only wordmark and dot-plus-text status indicators | Add logo marks, icons, or path-based SVG symbols anywhere |
| Use solid coloured swatches or dots as the only colour indicators | Use green/red anywhere except node-type swatches, anomalies, and the verdict dot |
