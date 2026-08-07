/**
 * Camera capture screen.
 *
 * Per specifications.md section 4.3: photo capture, plus the option to select
 * an existing photo from the library.
 *
 **/

import { useRef, useState } from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import { manipulateAsync, SaveFormat } from "expo-image-manipulator";

import { predict } from "../api/client";
import { COLORS, FONTS, SPACE } from "../constants";

/**
 * Noralise before upload, specifically to account for HEIC coming from iOS
 */
async function normalize(uri) {
    const out = await manipulateAsync(
        uri,
        [{ resize: {width: 1024 } }],
        { format: SaveFormat.JPEG, compress: 0.8 }
    );
    return out.uri;
}

export default function CameraScreen({ navigation }) {
    const cameraRef = useRef(null);
    const [permission, requestPermission] = useCameraPermissions();
    const [busy, setBusy] = useState(false);
    const [shot, setShot] = useState(null);
    const [error, setError] = useState(null);

    async function send(rawUri) {
        setError(null);
        setShot(rawUri);
        setBusy(true);
        try {
            const uri = await normalize(rawUri);
            const result = await predict(uri);
            if (!result.ok) {
                setError(result);
                return;
            }
            navigation.navigate("Result", { result: result.data, photoUri: uri });
        } finally {
            setBusy(false);
            setShot(null);
        }
    }

    async function onShutter() {
        if (busy || !cameraRef.current) return;
        const photo = await cameraRef.current.takePictureAsync({ quality: 1 });
        await send(photo.uri);
    }

    async function onLibrary() {
        if (busy) return;
        const res = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ["images"],
            quality: 1,
        });
        if (!res.canceled) await send(res.assets[0].uri);
    }

    if (!permission) return <View style={styles.screen} />;

    if (!permission.granted) {
        return (
            <View style={[styles.screen, styles.center]}>
                <Text style={styles.permTitle}>CAMERA ACCESS</Text>
                <Text style={styles.permBody}>Not Corgi needs the camera to look at dogs.</Text>
                <Pressable style={styles.primaryBtn} onPress={requestPermission}>
                    <Text style={styles.primaryBtnText}>GRANT ACCESS</Text>
                </Pressable>
            </View>
        );
    }

    return (
        <View style={styles.screen}>
            <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="back" />
            {/* rule-of-thirds grid */}
            <View style={StyleSheet.absoluteFill} pointerEvents="none">
                <View style={[styles.gridV, { left: "33.3%" }]} />
                <View style={[styles.gridV, { left: "66.6%" }]} />
                <View style={[styles.gridH, { top: "33.3%" }]} />
                <View style={[styles.gridH, { top: "66.6%" }]} />
            </View>

            {/* wordmark */}
            <View style={styles.topBar} pointerEvents="none">
                <View style={styles.row}>
                    <View style={styles.mark} />
                    <Text style={styles.wordmark}>NOT CORGI</Text>
                </View>
                <Text style={styles.version}>v1.0</Text>
            </View>

            {/* controls */}
            <View style={styles.bottomBar}>
                <Text style={styles.hint}>POINT IT AT A MAYBE-CORGI</Text>
                <View style={styles.controls}>
                    <View style={styles.side}>
                        <Pressable style={styles.squareBtn} onPress={onLibrary}>
                            <View style={styles.squareBtnInner} />
                        </Pressable>
                        <Text style={styles.sideLabel}>LIBRARY</Text>
                    </View>

                    <Pressable style={styles.shutter} onPress={onShutter}>
                        <View style={styles.shutterInner} />
                    </Pressable>

                    <View style={styles.side}>
                        <View style={styles.zoomBtn}>
                            <Text style={styles.zoomText}>1x</Text>
                        </View>
                        <Text style={styles.sideLabel}>ZOOM</Text>
                    </View>
                </View>
            </View>

            {/* sniffing overlay */}
            {busy && (
                <View style={styles.overlay}>
                {shot && <Image source={{ uri: shot }} style={StyleSheet.absoluteFill} />}
                <View style={styles.scrim} />
                <View style={styles.overlayText}>
                    <Text style={styles.sniffing}>SNIFFING...</Text>
                    <Text style={styles.sniffingSub}>Consulting the corgi council.</Text>
                </View>
                </View>
            )}

            {/* error */}
            {error && !busy && (
                <View style={styles.errorBox}>
                    <Text style={styles.errorTitle}>
                        {error.retryable ? "TRY THAT AGAIN" : "SOMETHING'S OFF"}
                    </Text>
                    <Text style={styles.errorBody}>{error.message}</Text>
                    <Pressable onPress={() => setError(null)}>
                        <Text style={styles.errorDismiss}>DISMISS</Text>
                    </Pressable>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    screen: { flex: 1, backgroundColor: COLORS.viewfinder },
    center: { alignItems: "center", justifyContent: "center", padding: SPACE[6] },
    permTitle: { fontFamily: FONTS.heading, fontSize: 22, letterSpacing: 2, color: COLORS.white },
    permBody: { fontFamily: FONTS.body, fontSize: 14, color: COLORS.neutral300, textAlign: "center", marginTop: SPACE[2] },
    primaryBtn: { backgroundColor: COLORS.accent, paddingVertical: SPACE[3], paddingHorizontal: SPACE[6], marginTop: SPACE[6] },
    primaryBtnText: { fontFamily: FONTS.heading, fontSize: 13, letterSpacing: 1.5, color: COLORS.white },
    gridV: { position: "absolute", top: 0, bottom: 0, width: 1, backgroundColor: "rgba(255,255,255,0.12)" },
    gridH: { position: "absolute", left: 0, right: 0, height: 1, backgroundColor: "rgba(255,255,255,0.12)" },
    topBar: { position: "absolute", top: 64, left: 20, right: 20, flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
    row: { flexDirection: "row", alignItems: "center", gap: 7 },
    mark: { width: 10, height: 10, backgroundColor: COLORS.accent },
    wordmark: { fontFamily: FONTS.heading, fontSize: 12, letterSpacing: 2.2, color: COLORS.white },
    version: { fontFamily: FONTS.medium, fontSize: 10, letterSpacing: 1.4, color: "rgba(255,255,255,0.65)" },
    bottomBar: { position: "absolute", left: 0, right: 0, bottom: 0, paddingHorizontal: 26, paddingTop: 22, paddingBottom: 52, gap: 18, backgroundColor: "rgba(10,9,9,0.55)" },
    hint: { fontFamily: FONTS.medium, fontSize: 11, letterSpacing: 1.8, color: "rgba(255,255,255,0.85)", textAlign: "center" },
    controls: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
    side: { alignItems: "center", gap: 5, width: 46 },
    sideLabel: { fontFamily: FONTS.medium, fontSize: 9, letterSpacing: 1.3, color: "rgba(255,255,255,0.7)" },
    squareBtn: { width: 46, height: 46, borderWidth: 2, borderColor: COLORS.white, justifyContent: "flex-end", padding: 5 },
    squareBtnInner: { width: 14, height: 14, backgroundColor: COLORS.white },
    zoomBtn: { width: 46, height: 46, borderWidth: 2, borderColor: "rgba(255,255,255,0.55)", alignItems: "center", justifyContent: "center" },
    zoomText: { fontFamily: FONTS.heading, fontSize: 13, color: COLORS.white },
    shutter: { width: 78, height: 78, borderRadius: 39, borderWidth: 4, borderColor: COLORS.white, padding: 5 },
    shutterInner: { flex: 1, borderRadius: 30, backgroundColor: COLORS.accent },
    overlay: { ...StyleSheet.absoluteFillObject, justifyContent: "center", paddingHorizontal: 30 },
    scrim: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(16,14,13,0.72)" },
    overlayText: { gap: SPACE[3] },
    sniffing: { fontFamily: FONTS.heading, fontSize: 46, color: COLORS.white, letterSpacing: -0.5 },
    sniffingSub: { fontFamily: FONTS.body, fontSize: 14, color: "rgba(255,255,255,0.85)" },
    errorBox: { position: "absolute", left: 20, right: 20, bottom: 200, backgroundColor: COLORS.ink, padding: SPACE[4], gap: SPACE[2] },
    errorTitle: { fontFamily: FONTS.heading, fontSize: 13, letterSpacing: 1.5, color: COLORS.accent500 },
    errorBody: { fontFamily: FONTS.body, fontSize: 13, color: COLORS.white },
    errorDismiss: { fontFamily: FONTS.heading, fontSize: 12, letterSpacing: 1.2, color: COLORS.neutral500, marginTop: SPACE[1] },
});