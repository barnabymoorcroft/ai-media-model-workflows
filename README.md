# AI media model workflows

A source-linked catalog and offline-tested async video example for developers comparing image and video APIs. The catalog is a dated snapshot of models that are present in the live model directory; it is not a popularity ranking and it does not claim that one provider owns every listed model.

[Open the current model directory](https://argolink.io/en/models) and inspect the individual model page before copying a request. ArgoLink is one callable API host. It is named in the source field and the runnable example; vendor ownership remains in each row. Last checked: 2026-10-07.

## What is verified

catalog/models.json was generated from the live catalog endpoint on 2026-10-07. Each row records model ID, display name, provider family, modality, endpoint, effective service tiers, official catalog tiers, a primary model page and model-specific limits. Empty data is omitted rather than replaced with zero.

The current verified rows include:

| Family | Live IDs in this snapshot | Modality |
| --- | --- | --- |
| ByteDance Seed | seedance-2.5, seedance-2.0, seedance-2.0-fast, seedance-2.0-mini | video |
| Alibaba Wan | wan-3, wan-3-prime | video |
| MiniMax | minimax-h3 | video |
| xAI | grok-imagine-video-1.5 | video |
| OpenAI | gpt-image-2 | image |
| Google | nano-banana-2 | image |

Kling, Veo and Sora are listed in the catalog's omitted_models section with an explicit reason: they were not present in this live ArgoLink snapshot, so this repository makes no price, limits or availability claim for them. A later update must reread their primary provider pages and the current catalog instead of guessing.

## Read model-specific facts

Do not use a common video schema:

- Seedance 2.5 is 4–30 seconds, 480p/720p/1080p, and its frame and edit modes use adaptive ratio. It accepts up to 30 images, 10 videos and 10 audio tracks, 50 total.
- Seedance 2.0 is 4–15 seconds and publishes 480p, 720p, 1080p and 4k; its frame modes can use adaptive or a fixed ratio. Mini and Fast publish 480p and 720p only.
- Wan 3 is 2–30 seconds with 480p/720p/1080p in the current catalog. Wan 3 Prime is a separate ID; do not copy frame support from Wan 3 into it.
- MiniMax H3 lists 768p and 2k, not 720p. Its reference audio rules are model-specific.
- Image rows have image-size, quality and reference fields, not video duration fields.

Open the row's source URL, then inspect limits, accepted fields, input lifetime and billing mode. Effective tiers are service prices; official tiers are the catalog's official-price reference where supplied. Neither is a competitor quote.

## Prices in this snapshot

The verified effective video rows are:

| Model | Published effective rates |
| --- | --- |
| seedance-2.5 | 0.0874 / 0.196 / 0.483 USD per second at 480p / 720p / 1080p |
| seedance-2.0 | 0.053 / 0.11 / 0.28 / 0.58 USD per second at 480p / 720p / 1080p / 4k |
| seedance-2.0-fast | 0.042 / 0.091 USD per second at 480p / 720p |
| seedance-2.0-mini | 0.026 / 0.057 USD per second at 480p / 720p |
| wan-3 | 0.038 / 0.075 / 0.15 USD per second at 480p / 720p / 1080p |
| wan-3-prime | 0.051 / 0.11 / 0.21 USD per second at 480p / 720p / 1080p |
| minimax-h3 | 0.039 at 768p; 0.064 at 2k |
| grok-imagine-video-1.5 | 0.064 / 0.112 / 0.2 USD per second at 480p / 720p / 1080p |

Image price tiers and official values stay in catalog/models.json because their units and size/quality rules differ from video. For example, GPT Image 2 and Nano Banana 2 do not use output-seconds billing. Do not compare the numbers without carrying the unit and input rules along.

## Runnable asynchronous workflow

The example uses only the Python standard library. It performs one POST, then explicit status GETs, then one content GET after done. It never resubmits an ambiguous POST and never treats an unknown status as success.

~~~sh
export VIDEO_API_KEY='from-a-secret-manager'
python examples/async_video.py
~~~

For a five-second 720p Seedance 2.5 call the example's output-only estimate is 0.98 USD at the checked effective rate. The function returns resume when its local deadline ends, retaining request_id in the caller's record. Failed and expired jobs are returned with their provider error object. A production worker should persist request_id before its first status poll and keep the response body for support.

The same lifecycle in cURL:

~~~sh
BASE=https://argolink.io/v1
AUTH="Authorization: Bearer $VIDEO_API_KEY"
JOB=$(curl --fail-with-body -sS "$BASE/videos/generations" \
  -H "$AUTH" -H 'User-Agent: ai-media-model-workflows/1.0' \
  -H 'Content-Type: application/json' \
  -d '{"model":"seedance-2.5","prompt":"A sunrise over a quiet harbor","duration":5,"resolution":"720p","aspect_ratio":"16:9","generate_audio":true}')
ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$JOB")
curl --fail-with-body -sS "$BASE/videos/$ID" \
  -H "$AUTH" -H 'User-Agent: ai-media-model-workflows/1.0'
curl --fail-with-body -sS "$BASE/videos/$ID/content" \
  -H "$AUTH" -H 'User-Agent: ai-media-model-workflows/1.0' -o harbor.mp4
~~~

The third command is valid only after status reports done. Production API routes are POST /v1/videos/generations, GET /v1/videos/{request_id}, and GET /v1/videos/{request_id}/content. The only statuses accepted by this example are pending, done, failed and expired.

## Provider comparison discipline

A model can be inexpensive for prompt-only video and more expensive when reference-video seconds are billed. Compare:

1. model ID and output format;
2. duration and resolution tiers;
3. reference count, media duration and upload lifetime;
4. whether reference video seconds add to billing;
5. failed, rejected and expired job rules;
6. base URL, authentication and endpoint shape.

Do not transfer a Seedance field to Wan, MiniMax or an image endpoint. Do not publish latency, throughput, stars or a “best” badge unless a dated primary source and a reproducible method are included. This catalog deliberately avoids unverified Kling, Veo and Sora assertions.

## Operational checklist

Keep one manifest per request with model ID, prompt digest, reference URLs, request ID, latest status, output path and cost estimate. Store keys outside the repository. Apply a semaphore before a batch; a local worker cap does not override provider account limits. Honor Retry-After for 429 and 503. A content request before done returns 409; a failed task can return 424. Preserve those bodies and do not hide them behind a generic retry.

## FAQ

**Why is a model absent?** Its ID was not in the checked catalog or its primary facts were not reread, so omission is safer than a stale claim. **Can I copy a row into another provider?** No; use that provider's primary page and record a new date. **Does every video model accept uploads?** No; upload fields and media URL lifetime are model-specific. **Why are image prices not shown beside video seconds?** Their units differ; the JSON preserves the correct tier labels. **Can this example generate images?** No. Image requests need their own endpoint and body validation. **Can I poll forever?** No; the example has a bounded timeout and returns resume.

## Tests

~~~sh
python -m unittest discover -s tests -v
python -m py_compile examples/async_video.py
~~~

Tests use a fake local opener. They check source links, authorization and User-Agent headers, submit → status → download order, non-production output, and rejection of unknown statuses. No key is required and no production or billable request is made.
