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
export const COLORS = {
  bg: "#f3f2f2",
  surface: "#eae9e9",
  ink: "#201e1d",
  accent: "#ec3013",
  accent2: "#e15b47",
  accent300: "#ffc4b8",
  accent500: "#ff563c",
  neutral300: "#d7d3d3",
  neutral500: "#9b9797",
  neutral700: "#605d5d",
  viewfinder: "#161413",
  white: "#ffffff",
};

export const FONTS = {
  body: "Archivo_400Regular",
  medium: "Archivo_600SemiBold",
  heading: "Archivo_800ExtraBold",
};

export const SPACE = { 1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 8: 32 };

export const RADIUS = 0;

export const CLASS_NAMES = ["Cardigan", "Not_Corgi", "Pembroke"];

// Labels for the results screen.
export const DISPLAY_NAMES = {
    Cardigan: "Cardigan Welsh Corgi",
    Not_Corgi: "Not a Corgi",
    Pembroke: "Pembroke Welsh Corgi",
};

// These are just for fun to show on the results screen
export const BREED_BLURBS = {
    Pembroke: "The one without the tail. Favorite of a certain late queen.",
    Cardigan: "The older breed, larger, and the one that (almost) always has a tail.",
};

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:5001";

// short enough time out so that a weak signal or server error fails fast
export const REQUEST_TIMEOUT_MS = 15000;
