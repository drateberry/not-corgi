"""Tests for the prediction endpoint.

Worth covering, roughly in order of how likely each is to bite during the demo:

  - A known Pembroke image returns Pembroke as the top class.
  - A known Cardigan image returns Cardigan as the top class.
  - A non-dog image returns Not_Corgi.
  - Probabilities are returned for all three classes and sum to ~1.0.
  - Class names in the response map to the right indices (spec §5.2) — this is
    the failure that produces confidently wrong answers with no error anywhere.
  - Missing file, unsupported format, and corrupt image all return a clean error
    rather than a 500.

TODO: implement.
"""
