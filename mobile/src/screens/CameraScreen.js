/**
 * Camera capture screen.
 *
 * Per specifications.md section 4.3: photo capture, plus the option to select
 * an existing photo from the library.
 *
 * TODO:
 *   - Request and handle camera + photo library permissions, including denial.
 *   - Capture a photo (expo-camera) or pick one (expo-image-picker).
 *   - Downscale before upload — full-resolution phone photos are slow to send
 *     on cellular and the model input is small anyway.
 *   - Show a loading state during the request; the round trip is not instant.
 *   - Surface network errors from api/client.js with a retry affordance.
 */

export default function CameraScreen() {
  // TODO: implement.
  return null;
}
