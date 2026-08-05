/**
 * Shared constants for the mobile app.
 *
 * CLASS_NAMES must stay in the same order as model/src/constants.py. Per
 * specifications.md section 5.2 the mapping is Cardigan=0, Not_Corgi=1,
 * Pembroke=2, and a mismatch between training, API, and app scrambles labels
 * silently with no error.
 *
 * Safer still: have the API return class names alongside probabilities and key
 * off those, so this array is a display-order preference rather than a second
 * source of truth that can drift.
 */

export const CLASS_NAMES = ["Cardigan", "Not_Corgi", "Pembroke"];

// Human-readable labels for the results screen.
// TODO: fill in (e.g. Cardigan -> "Cardigan Welsh Corgi").
export const DISPLAY_NAMES = {};

// TODO: API base URL. Read from an Expo config/env value rather than hardcoding,
// so switching between a laptop on the local network and the deployed host does
// not require a code edit mid-demo.
export const API_BASE_URL = null;

// TODO: request timeout. Keep it short enough that a dead cellular connection
// surfaces an error quickly instead of hanging on camera (spec section 9).
export const REQUEST_TIMEOUT_MS = null;
