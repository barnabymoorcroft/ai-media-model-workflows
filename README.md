# AI media model workflows

This is a source-linked catalog and a small asynchronous example for developers comparing video and image APIs. **ArgoLink is one listed endpoint; it is not the owner of every model named here.** Vendor availability, model IDs, pricing, and limits change. Every catalog row therefore carries a checked date and a source URL. Last checked: 2026-10-07.

## How to use the catalog

Read catalog/models.json before copying a request. The file intentionally includes only a few rows with verified facts: Seedance 2.5, Wan 3.0, MiniMax H3, gpt-image-2, and Nano Banana 2. The words in facts are not a universal schema. For example, MiniMax H3 has 768p and 2k entries; writing 720p for it would be an error. Seedance 2.5 frame modes have a separate adaptive-ratio rule. Resolve any unknown field on the model's own primary page, then record the date and URL.

The catalog is not a ranking of providers. It does not contain invented latency, star counts, or “best model” labels. A provider can be cheap for text-to-video and expensive when reference video seconds are billed. Compare the billing formula, accepted inputs, output duration, and failure/refund rule together.

## Async example

examples/async_video.py uses Python's standard library and a neutral VIDEO_API_KEY. It sends one POST to /v1/videos/generations, saves the request ID, polls GET /v1/videos/{id}, and stops on pending, done, failed, or expired. It does not retry an ambiguous POST. Add content download only after done. Each request includes a User-Agent. Tests are offline and do not require a key.

## Provider verification table

| Family | What to verify before using | Why a single row is insufficient |
|---|---|---|
| Seedance | model variant, duration, ratio, reference role, output tier | frame and reference billing differ |
| Wan | version, audio, input type, duration, resolution | variants do not share every field |
| MiniMax | 768p versus 2k, audio requirement, reference counts | 720p is not a safe alias |
| gpt-image | size, quality, output encoding, reference limits | image tokens and output tiers differ |
| Nano Banana | live model ID, reference count, pricing | names and aliases change |

Prices are omitted when a primary page was not re-read for this repository. The checked ArgoLink Seedance 2.5 rates are $0.0874/s at 480p, $0.196/s at 720p, and $0.483/s at 1080p; use the live page for current values. A five-second 720p estimate is $0.98, not a guarantee.

## Workflow checklist

Keep one manifest per request with model ID, prompt digest, references, request ID, status, output path, and cost estimate. Put media URLs and keys in a secret-aware store. Apply a semaphore before concurrent submissions. On 429/503, respect Retry-After. On failed or expired jobs, preserve the response. On a local timeout, resume the existing ID. Test a small sample before a batch.

## FAQ

**Can I copy a row to another provider?** No; use the source page and update the row. **Does a video model always support upload?** No; the upload contract and media URL lifetime are model/service-specific. **Are prices official?** Only when the row links the primary pricing page; ArgoLink values are service rates. **Why no Kling, Veo, Sora, or Grok rows?** They were not verified in this catalog snapshot, so omission is safer than a stale assertion. **Can the example generate an image?** It is intentionally video-only; image requests need their own endpoint and body validation.
