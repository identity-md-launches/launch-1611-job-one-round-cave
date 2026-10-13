# Call Witness — contribution 23

Local checks on 2026-10-13. They show what this contributor tried; they are not independent certification.

| Check | Result |
| --- | --- |
| `python3 -B -m unittest discover -s line-4/tools/call-witness -p 'test_*.py' -v` | Exit 0; 6 tests passed. |
| `python3 -B line-4/tools/call-witness/call_witness.py demo` | Exit 0; saved real ZTO two-provider result `agree`. |
| Live `call_witness.py live --save line-4/tools/call-witness/zto-witness.json` | Exit 0 in about one second; PublicNode and dRPC returned the same ZTO `totalSupply()` bytes at finalized block `0x18f8d21`. Raw responses saved. |
| Live `call_witness.py live --from-observation line-4/tools/call-changes/zto-before.json` | Exit 0 in about one second; exact saved call reused and both providers agreed. |
| Live `call_witness.py live --token IMD` | Exit 0; both public RPCs agreed on IMD `totalSupply()` at finalized block `0x18f8d41`. Output inspected but not saved. |
| Existing Call Changes and Call Rehearsal tests | 36 and 20 tests passed, respectively. |
| Structural audit | 23 numbered JSON records; only `23.json` added. Both PNG wall paths have identical 1254 × 1254 RGB bytes and SHA-256 `9353c0ed6bd22f9c11c3d7a47b02fb8a78eac5c2e68896e32fdf2eb59575f5b3`. Record shape, image URL and six traits match. JPEG is baseline 512 × 512 and 54,705 bytes. New tool files are each below 100 KB. |

The previous wall was downloaded from record 22 and its SHA-256 verified as `3ce617f388b38f235c848454eda9e846753e3f1ca974f4980d92700276fc95ab` before editing. `GOAL.md` retains SHA-256 `f30346951b47cd86a9bd5a1646f069f87d57c0323d8b42654e1fca87a9d1678a`. No older record or original tool was modified. No deployment, wallet interaction, signature, payment or transaction broadcast occurred. Visual review is recorded in `VISUAL-23.md`.
