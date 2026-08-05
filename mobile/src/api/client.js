/**
 * HTTP client for the Not Corgi API.
 *
 * All network access lives here so the screens stay unaware of transport
 * details and so retry/timeout behaviour has exactly one home.
 *
 * Network reliability is a functional requirement, not a nicety
 * (specifications.md section 9): the demo is filmed at a dog park on cellular
 * data, and weak signal is the most likely cause of a failed demo. Every path
 * out of this module should produce something the UI can show the user — never
 * an unhandled rejection.
 */

/**
 * Upload an image to POST /predict and return the parsed result.
 *
 * TODO: implement. Multipart form data. Distinguish the failure modes the UI
 * needs to tell apart — timeout, no connectivity, server error, bad response —
 * because "try again" is right for some of them and useless for others.
 */
export async function predict(imageUri) {
  throw new Error("Not implemented");
}

/**
 * Hit GET /health to confirm the API is reachable.
 *
 * TODO: implement. Worth calling before filming.
 */
export async function checkHealth() {
  throw new Error("Not implemented");
}
