# Hermes Model Adapter Contract

Kubrick adapters translate validated private graph and storyboard state into provider-facing prompt packets. They do not generate media and do not mutate symbolic intent.

## Sequence

1. Compile a valid private motif graph.
2. For multi-frame work, propagate and compare storyboard state.
3. Build a provider-neutral adapter packet.
4. Translate that packet with a provider adapter.
5. Send only the provider-facing packet to the generation system.
6. Preserve all receipts for later visual QA.

## Commands

```bash
python scripts/build_model_adapter_packet.py \
  --graph out/kubrick/motif-graph.private.yaml \
  --storyboard out/kubrick/storyboard-symbolic-state.yaml \
  --provider grok-imagine \
  --output out/kubrick/model-adapter-packet.yaml

python scripts/adapt_grok_imagine.py \
  --packet out/kubrick/model-adapter-packet.yaml \
  --output out/kubrick/grok-imagine-prompt-packet.yaml
```

## Invariants

- `source_graph_id` is immutable.
- Provider adapters may change syntax, ordering, emphasis, and supported generation parameters only.
- Provider adapters may not add new motifs, alter ownership, remove residue, or reset state.
- Pattern links and lexicon links remain private.
- Named esoterica stays out of provider prompts unless explicitly requested by the operator.
- A provider adapter must fail closed when its neutral input packet is invalid.
- External generation APIs are optional and outside the adapter runtime.

## Grok Imagine adapter

The first adapter emits one prompt packet per frame with:

- observable prompt text,
- continuity locks from the previous frame,
- declared state constraints,
- negative constraints,
- aspect ratio and restrained style defaults,
- a variation policy that allows only declared frame-state changes.

The adapter does not call Grok or require credentials.
