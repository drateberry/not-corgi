/**
 * Not Corgi — React Native / Expo entry point.
 *
 * Per specifications.md section 4.3:
 *   - Camera interface for photo capture, plus selecting an existing photo.
 *   - Sends the image to the Flask API as multipart form data.
 *   - Results screen: prominent verdict (Corgi / Not Corgi), the specific breed,
 *     all three class probabilities, and a toggleable Grad-CAM overlay.
 *   - Must handle network failure gracefully — the intended demo environment is
 *     a dog park on cellular data (section 9).
 *
 * Runs on Expo Go for the server-based path. The on-device TFLite stretch goal
 * would require a development build, which is part of why it is scoped last.
 */

// TODO: imports

// TODO: navigation between CameraScreen and ResultScreen.

export default function App() {
  // TODO: implement.
  return null;
}
