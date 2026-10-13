# Gathering 03

This round tried every tool from all four lines, retained fresh read-only ZTO observations, and added [Witness Context](../shared/witness-context/README.md). It connects both providers' code/proxy evidence and call results at exactly one block. The wall adds two watching eyes around one stone in a previously bare patch.

- [REPORT.md](REPORT.md): per-line results, PublicNode's archive failure and successful dRPC fallback, coverage limits, overlap and scope.
- [COINS.md](COINS.md): none; existing ZTO and IMD cover all needs.
- [VISUAL.md](VISUAL.md): wall/thumbnail formats, preservation and visual review.
- [IMAGE-PROMPT.md](IMAGE-PROMPT.md): final generation prompt and compositing method.
- [Gallery](../dist/index.html): all records by wall, painted rounds newest first.

Repeat all 235 offline tests and each tool demonstration:

```sh
python3 -B gathering/check_tools.py
```

Try the new shared piece without network or installation:

```sh
python3 -B shared/witness-context/witness_context.py demo
```

Rebuild the single-page gallery and four-goal JSON with `python3 -B gathering/build_gallery.py`. Existing future placeholders are retained; this is the third gathering, so initialization is not repeated. Delivery checks are local contributor checks, not independent certifications. Nothing was sent on-chain.

Check PNG/JPEG bytes, record/gallery consistency, file sizes and scope with `python3 -B gathering/check_delivery.py`.
