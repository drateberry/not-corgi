# mobile/

React Native / Expo client for Not Corgi.

| Path | Purpose |
|---|---|
| `App.js` | Entry point and navigation |
| `src/screens/CameraScreen.js` | Capture or pick a photo, upload it |
| `src/screens/ResultScreen.js` | Verdict, probabilities, Grad-CAM toggle |
| `src/api/client.js` | All HTTP access, timeouts, error handling |
| `src/constants.js` | Class ordering and API config |
| `src/components/` | Shared UI pieces |
| `assets/` | Icons and splash |

## Setup

This directory currently holds hand-written stubs. Scaffold the real Expo
project over it rather than hand-maintaining `package.json`:

```
npx create-expo-app .
npx expo install expo-camera expo-image-picker
npm start
```

Then open the project in Expo Go on a physical phone — the camera and the
cellular-network conditions this app is built for do not exist in a simulator.

TODO: document how to point the app at a local API vs. the deployed one.
