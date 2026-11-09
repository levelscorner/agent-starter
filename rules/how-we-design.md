---
root: false
targets: ["*"]
description: "How we design UI: the laws every screen follows, and how to check them"
globs: ["**/*.{tsx,jsx,html,css,vue,svelte}"]
---

# How we design

These laws apply to every screen we ship: product apps, marketing sites and internal tools.

## Law 0: the owner's decisions win

1. Each product keeps its own `DESIGN.md`: palette, fonts, logo, themes and every decision the owner approved.
2. Read that file before changing a screen.
3. If a law or a design skill disagrees with an owner decision, the decision wins. Write the disagreement down. Do not change it quietly.

## The laws

1. **Plain words.** Interface text says what a thing does, for the person using it. Never show internal names: field names, file names, config keys, slugs.
2. **One bright moment per screen.** The content carries the colour: a frame, a film, a chart, a product preview. The chrome stays quiet: tinted neutrals and one accent. The accent marks the main action, the selection or the one number that matters.
3. **No AI tells.** No glows, no coloured shadows, no gradient text, no colour washes or blobs behind content, no neon borders. No emoji or arrow glyphs used as icons. No loops on things that are not live.
4. **A 4 px grid.** Every margin, padding, gap and fixed height is a multiple of 4. Equal things get equal sizes. Space inside a group is smaller than space between groups.
5. **Calm type.** Use one interface family, plus at most one partner: a mono for numbers and meta, or a display face for big headings. Use weights 400 to 600. Labels are in sentence case. Uppercase tracked labels are allowed only where the product's `DESIGN.md` says so. Numbers use tabular figures and one format.
6. **Honest copy.**
   - No em dashes, no exclamation marks, no hype words, no greeting headlines.
   - Never make a claim we cannot check.
   - Use the product's current money unit and current price rules, never a retired one.
   - Never say something is free unless it is free.
7. **Every state is designed.** Loading uses a skeleton the size of the content. Empty says how to fill it. Errors are shown inline, next to the cause. Focus has a visible ring. Hover and pressed states stay inside the palette.
8. **Phones are first-class.** At 390 px wide:
   - nothing overlaps,
   - nothing scrolls sideways,
   - the brand name does not wrap,
   - no text is under 11 px.
9. **Motion explains.** Animate only transform and opacity, with one easing curve and a few durations. A hover is a colour or surface change. A press is a tiny scale-down. At most one entrance on load.
10. **One system per product.** Every page of a product shares one header, one set of tokens and one component style. A page that looks like a different app is a bug.

## How to check

1. Before you change a screen, take a screenshot on desktop (1440 x 900) and on a phone (390 x 844), in every theme the product ships.
2. Measure the tells with a script, not by eye. Count:
   - uppercase tracked labels,
   - mono text,
   - spacing values off the 4 px grid,
   - gradients, coloured shadows and infinite animations,
   - em dashes, exclamation marks and emoji,
   - retired words,
   - horizontal overflow on the phone.
3. List every finding with where it lives. Then propose a direction in five lines: product, character, world, moments, signature. Wait for the owner before editing.
4. After the change, run the same measurement again. A finding is fixed only when its number went down and the screenshots agree.

## Credits

In our own words, after [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky (CC BY 4.0) and the design-taste-frontend skill (source not recorded).
