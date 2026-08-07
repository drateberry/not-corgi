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
import { View } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { useFonts, Archivo_400Regular, Archivo_600SemiBold, Archivo_800ExtraBold,} from "@expo-google-fonts/archivo";

import CameraScreen from "./src/screens/CameraScreen";
import ResultScreen from "./src/screens/ResultScreen";
import { COLORS } from "./src/constants";

const Stack = createNativeStackNavigator();

export default function App() {
    const [fontsLoaded] = useFonts({
        Archivo_400Regular,
        Archivo_600SemiBold,
        Archivo_800ExtraBold
    });

    // Hold rendering until Google Fonts load.
    if (!fontsLoaded) {
        return <View style={{ flex: 1, backgroundColor: COLORS.viewfinder }} />;
    }

    return (
        <SafeAreaProvider>
            <StatusBar style="light" />
            <NavigationContainer>
                <Stack.Navigator screenOptions={{
                    headerShown: false,
                    contentStyle: { backgroundColor: COLORS.bg },
                }} >
                    <Stack.Screen name="Camera" component={CameraScreen} />
                    <Stack.Screen name="Result" component={ResultScreen} />
                </Stack.Navigator>
            </NavigationContainer>
        </SafeAreaProvider>
    );
}