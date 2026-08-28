---
name: diagram
category: design
description: Generate architecture and system diagrams as SVG/PNG. Use when asked to create a diagram, draw a system architecture, visualize a flow, or produce any technical illustration.
---

# Diagram Skill

Generate clean, readable architecture and system diagrams using hand-authored SVG, rasterized to PNG via `@resvg/resvg-js`.

## Toolchain

- **SVG authoring:** Write SVG directly — full control over label placement, edge routing, typography, and shape variety
- **Rasterization:** `@resvg/resvg-js` — install with `npm install --prefix ~/.local @resvg/resvg-js` if missing

## Render Pipeline

```bash
node -e "
const { Resvg } = require(require('path').join(require('os').homedir(), '.local/node_modules/@resvg/resvg-js'));
const fs = require('fs');
const svg = fs.readFileSync('diagram.svg', 'utf8');
const resvg = new Resvg(svg, { fitTo: { mode: 'width', value: 2400 } });
fs.writeFileSync('diagram.png', resvg.render().asPng());
"
```

Always inspect the PNG with `Read` after rendering to verify the output before sending.

## SVG Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 WIDTH HEIGHT" width="WIDTH" height="HEIGHT">
  <rect x="0" y="0" width="WIDTH" height="HEIGHT" fill="#ffffff"/>
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="10" refY="5"
            markerWidth="10" markerHeight="10" orient="auto">
      <polygon points="0,0 10,5 0,10" fill="#333"/>
    </marker>
  </defs>
  <!-- components and edges here -->
</svg>
```

## Arrowheads

Use **filled triangle** arrowheads (`polygon`), not open chevrons (`path`). Open chevrons render too small and ambiguously on vertical lines.

```xml
<marker id="arr" viewBox="0 0 10 10" refX="10" refY="5"
        markerWidth="10" markerHeight="10" orient="auto">
  <polygon points="0,0 10,5 0,10" fill="#333"/>
</marker>
```

For muted/secondary edges (like "guards" relationships):
```xml
<marker id="arr-muted" viewBox="0 0 10 10" refX="10" refY="5"
        markerWidth="8" markerHeight="8" orient="auto">
  <polygon points="0,0 10,5 0,10" fill="#9673a6"/>
</marker>
```

## Shape Vocabulary

Use distinct shapes for different component types — shape communicates function at a glance without needing a color legend.

### Rounded Rectangle — processes and compute

```xml
<rect x="X" y="Y" width="W" height="55" rx="8" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<text x="CX" y="CY-5" font-family="sans-serif" font-size="13" font-weight="bold"
      fill="#232F3E" text-anchor="middle">Name</text>
<text x="CX" y="CY+12" font-family="sans-serif" font-size="11"
      fill="#555" text-anchor="middle">(subtitle)</text>
```

Use for: active processes, compute. CX = X + W/2, CY = Y + H/2 + 4.

### Pill (high rx) — relays and gateways

```xml
<rect x="X" y="Y" width="W" height="55" rx="20" fill="#d5e8d4" stroke="#82b366" stroke-width="1.5"/>
```

Use for: network gateways, relays, proxies. Same text pattern as rounded rect.

### Cylinder — data stores

```xml
<ellipse cx="CX" cy="Y" rx="RX" ry="8" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<rect x="X" y="Y" width="W" height="48" fill="FILL" stroke="none"/>
<line x1="X" y1="Y" x2="X" y2="Y+48" stroke="STROKE" stroke-width="1.5"/>
<line x1="X+W" y1="Y" x2="X+W" y2="Y+48" stroke="STROKE" stroke-width="1.5"/>
<ellipse cx="CX" cy="Y+48" rx="RX" ry="8" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<text x="CX" y="Y+21" font-family="sans-serif" font-size="13" font-weight="bold"
      fill="#232F3E" text-anchor="middle">Name</text>
<text x="CX" y="Y+37" font-family="sans-serif" font-size="11"
      fill="#555" text-anchor="middle">(subtitle)</text>
```

Use for: databases, journals, logs, any persistent store. Keep ry=8 (flatter ovals prevent text overlap). Position text in upper half of body, well above bottom ellipse.

### Cloud — external services

```xml
<path d="M X1 CY C ... Z" fill="#dae8fc" stroke="#6c8ebf" stroke-width="1.5"/>
```

Use for: external APIs, cloud services. Hand-draw cloud paths with 6-7 control points. Center text at the cloud's visual center.

### Hexagon — infrastructure

```xml
<polygon points="X1,CY X2,Y1 X3,CY X3,Y2 X2,Y3 X1,Y2"
         fill="#e1d5e7" stroke="#9673a6" stroke-width="1.5"/>
```

Use for: supervisors, firewalls, infrastructure components. Give enough vertical span for text — at least 80px tall.

### Document (folded corner) — config and file-based

```xml
<polygon points="X,Y X2,Y X3,Y+15 X3,Y+H X,Y+H" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<polygon points="X2,Y X2,Y+15 X3,Y+15" fill="FILL_LIGHT" stroke="STROKE" stroke-width="1"/>
```

Use for: configuration files, templates, any file-based component. X2 = X3 - 15 for the fold triangle.

### Folder — filesystem mounts

```xml
<path d="M X,Y+15 L X,Y L X+60,Y L X+75,Y+15 L X+W,Y+15 L X+W,Y+H L X,Y+H Z"
      fill="#dae8fc" stroke="#6c8ebf" stroke-width="1.5"/>
```

Use for: mounted volumes, workspace directories. The tab gives the folder silhouette.

## Color Palette

Colors reinforce shape, not replace it. Each shape type has a default color:

| Shape | Fill | Stroke | Use for |
|-------|------|--------|---------|
| Rounded rect | `#fff2cc` | `#d6b656` | Processes, compute |
| Pill | `#d5e8d4` | `#82b366` | Relays, gateways |
| Cylinder | `#f5f5f5` | `#666` | Storage |
| Cylinder (critical) | `#f8cecc` | `#b85450` | Critical/identity store |
| Cloud | `#dae8fc` | `#6c8ebf` | External services |
| Hexagon | `#e1d5e7` | `#9673a6` | Infrastructure |
| Document | `#fff2cc` | `#d6b656` | Active config |
| Document (neutral) | `#f5f5f5` | `#666` | Static config |
| Folder | `#dae8fc` | `#6c8ebf` | Mounts, volumes |
| Rectangle | `#f5f5f5` | `#666` | Neutral/external |

## Boundary Zones

Dashed rectangles for deployment boundaries:

```xml
<!-- Lighter boundary (host, less trust) -->
<rect x="X" y="Y" width="W" height="H" rx="14" fill="#fafafa"
      stroke="#bbb" stroke-width="1.5" stroke-dasharray="6,3"/>

<!-- Darker boundary (container, trust boundary) -->
<rect x="X" y="Y" width="W" height="H" rx="14" fill="#f7f9ff"
      stroke="#666" stroke-width="2" stroke-dasharray="8,4"/>
```

## Boundary Crossing Markers

When an edge crosses a deployment boundary, place a small circle at the crossing point:

```xml
<circle cx="CROSS_X" cy="CROSS_Y" r="5" fill="#fff" stroke="#666" stroke-width="1.5"/>
```

## Edge Routing Rules (CRITICAL)

These rules prevent diagram clutter. Follow them strictly.

### 1. Never route an edge through a box

Before drawing any edge, trace its full path and verify it does not pass through any component rectangle. If it does, reroute through a margin corridor.

### 2. Use margin corridors for edges that skip rows

When an edge connects two components that are not in adjacent rows (e.g., row 1 to row 3), it MUST route through a corridor outside all boxes:

- **Left margin:** Between the boundary wall and the leftmost box column
- **Column gap:** Between the left and right box columns
- **Right margin:** Between the rightmost box column and the boundary wall

Pattern: exit the source box horizontally into the corridor, travel vertically in the corridor, re-enter horizontally at the target.

### 3. All edges must be orthogonal

No diagonal lines. Use only horizontal and vertical segments with 90-degree turns.

### 4. Semantic ordering reduces crossings

Place components so that primary data flow goes **top-to-bottom** and **left-to-right**. Components that fire first (hooks, triggers) go above the components they activate. This is a structural fix that eliminates crossing problems that routing cannot solve.

### 5. Edge labels

Place labels near the midpoint of the edge, offset slightly so they don't overlap the line:

```xml
<!-- Horizontal edge label (above the line) -->
<text x="MIDPOINT_X" y="LINE_Y - 7" font-family="sans-serif" font-size="12"
      fill="#888" text-anchor="middle">label</text>

<!-- Vertical edge label (to the right of the line) -->
<text x="LINE_X + 15" y="MIDPOINT_Y" font-family="sans-serif" font-size="12"
      fill="#888" text-anchor="start">label</text>
```

## Verification Checklist

Before sending any diagram:

1. **Render to PNG** and inspect with `Read`
2. **Trace every edge path** against every box rectangle — verify no crossings
3. **Check arrowhead direction** — filled triangles should point in the data flow direction
4. **Verify labels** are inside shapes (not below), readable, and not overlapping edges
5. **Check boundary crossings** have circle markers where edges cross dashed boundaries

## Output Formats

- **PNG** at 2x resolution (width: 2400) for visual inspection
- **SVG** for HTML embedding (scales perfectly, inline-embeddable)
