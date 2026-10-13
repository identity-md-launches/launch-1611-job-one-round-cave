# Two Witnesses, One Stone — visual record

The finished wall contains two short charcoal trails converging at a small chalk pebble with a worn red-ochre halo. It sits in previously open rock below the two ancestral pools. The earlier Pepe, his spread hand, feet, pool marks, tracks, dark pit and cave surroundings remain visible in their earlier positions.

| Output | Format | Dimensions | Bytes |
| --- | --- | --- | ---: |
| `artifacts/line-4/wall-v3.png` | PNG, RGB, 8-bit | 1254 × 1254 | 2,697,330 |
| `artifacts/line-4/wall.png` | Identical PNG bytes | 1254 × 1254 | 2,697,330 |
| `dist/line-4/23.jpg` | Baseline JPEG, three components | 512 × 512 | 54,705 |

The PNG SHA-256 is `9353c0ed6bd22f9c11c3d7a47b02fb8a78eac5c2e68896e32fdf2eb59575f5b3`; record 23 uses this hash in its image URL. The previous wall SHA-256 was `3ce617f388b38f235c848454eda9e846753e3f1ca974f4980d92700276fc95ab` and was verified after download, before editing.

## Chosen visual review

Inspected the restored previous wall, full finished PNG and decoded 512px JPEG. The wall remains square with the same cave framing, rock, cracks, warm color and torchlight. The new mark is uneven, worn earth pigment and leaves the rock visible. Pepe retains a wide mouth and heavy-lidded eyes. His visible spread hand has **five digits: four fingers and one thumb**. No new hand or handprint was added. No visible letters, numbers, caption, logo, watermark, border, photograph, real person, political or hateful symbol was observed. **Unmet visual requirements observed: none.** Image generation is a visual edit, so preservation is based on inspection rather than a pixel-identical guarantee outside the added mark.

## Image method

Used the built-in imagegen edit tool with the verified previous wall as the sole target. Requested only two charcoal trails meeting at one chalk pebble in empty center-right rock, with all prior marks and cave structure preserved and all text excluded. The returned PNG data URL was streamed into the authorized artifact path. The JPEG was resized and encoded by the existing standard-library thumbnail helper. No CLI image-generation fallback or installed imaging dependency was used.

Final prompt:

> Precisely edit this 1254x1254 ancestral cave painting. In the empty center-right rock at about x=760-900,y=555-645 add two short charcoal trails converging on one small chalk white pebble with a faint worn red ochre halo, like two independent witnesses agreeing on one result. Preserve all existing pigment exactly, especially Pepe frog and his five-digit hand, footprints, pit, both ochre pools and the path joining them. Keep the cave size, framing, rock, cracks, colors and torchlight unchanged. Hand-made ancient earth pigments only, stone showing through. No new hands. No letters, numbers, captions, logos, watermarks, borders, photo or 3D elements. Return the entire edited square PNG.
