/**
 * Results screen.
 *
 * Per specifications.md section 4.3, this must show:
 *   - a prominent verdict (Corgi / Not Corgi) — the "Not Hotdog" homage lands here
 *   - the specific breed determination
 *   - all three class probabilities
 *   - a toggleable Grad-CAM heatmap overlay
 *
 */
import { useState } from "react";
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { COLORS, FONTS, SPACE, DISPLAY_NAMES, BREED_BLURBS } from "../constants";

export default function ResultScreen({ navigation, route }) {
    const { result, photoUri } = route.params;
    const [showHeatmap, setShowHeatmap] = useState(false);
    const insets = useSafeAreaInsets();
    const isCorgi = result.is_corgi;
    // sort results so winning classification is on top
    const ranked = Object.entries(result.probabilities).sort((a, b) => b[1] - a[1]);

    return (
        <View style={StyleSheet.screen}>
            <ScrollView contentContainerStyle={{ paddingBottom: SPACE[8] }}>
                {/* verdict band */}
                <View style={[ styles.band, { paddingTop: insets.top + SPACE[4], backgroundColor: isCorgi ? COLORS.accent : COLORS.ink },]}>
                    <Text style={styles.bandKicker}>VERDICT</Text>
                    {isCorgi ? (
                        <Text style={styles.verdict}>CORGI!</Text>
                    ) : (
                        <Text style={styles.verdictNot}><Text style={{ color: COLORS.accent500 }}>NOT{"\n"}</Text>CORGI</Text>
                    )}
                </View>
                {/* photo/heatmap view */}
                <View style={styles.photoBox}>
                    <Image source={{ uri: showHeatmap ? `data:image/png;base64,${result.gradcam}` : photoUri }} style={StyleSheet.absoluteFill} resizeMode="cover" />
                    {showHeatmap && (
                        <>
                        <View style={styles.camTag}>
                            <Text style={styles.camTagText}>GRAD-CAM</Text>
                        </View>
                        <View style={styles.scale}>
                            <Text style={styles.scaleLabel}>COLD</Text>
                            <View style={styles.scaleBar} />
                            <Text style={styles.scaleLabel}>HOT</Text>
                        </View>
                        </>
                    )}
                </View>
                {/* toggle */}
                <View style={styles.toggleRow}>
                    <Text style={styles.toggleLabel}>WHERE IT LOOKED</Text>
                    <View style={styles.segment}>
                        <Pressable style={[styles.segBtn, !showHeatmap && styles.segBtnOn]}
                        onPress={() => setShowHeatmap(false)}>
                            <Text style={[styles.segText, !showHeatmap && styles.segTextOn]}>PHOTO</Text>
                        </Pressable>
                        <Pressable style={[styles.segBtn, showHeatmap && styles.segBtnOn]}
                        onPress={() => setShowHeatmap(true)}>
                            <Text style={[styles.segText, showHeatmap && styles.segTextOn]}>HEATMAP</Text>
                        </Pressable>
                    </View>
                </View>
                {/* breed */}
                <View style={styles.breedBox}>
                    <Text style={styles.breedName}>
                        {(DISPLAY_NAMES[result.predicted_class] ?? result.predicted_class).toUpperCase()}
                    </Text>
                    {BREED_BLURBS[result.predicted_class] && (
                        <Text style={styles.breedBlurb}>{BREED_BLURBS[result.predicted_class]}</Text>
                    )}
                </View>
                {/* probability bars */}
                <View style={styles.confBox}>
                    <Text style={styles.confLabel}>MODEL CONFIDENCE</Text>
                    {ranked.map(([name, p], i) => (
                        <View key={name} style={styles.barRow}>
                        <Text style={styles.barName}>{DISPLAY_NAMES[name] ?? name}</Text>
                        <View style={styles.barTrack}>
                            <View
                            style={[
                                styles.barFill,
                                {
                                width: `${Math.max(p * 100, 0.5)}%`,
                                backgroundColor:
                                    i === 0 ? COLORS.accent : name === "Not_Corgi" ? COLORS.neutral500 : COLORS.accent300,
                                },
                            ]}
                            />
                        </View>
                        <Text style={styles.barPct}>{(p * 100).toFixed(1)}%</Text>
                        </View>
                    ))}
                </View>
                {/* Do it again */}
                <Pressable style={styles.cta} onPress={() => navigation.goBack()}>
                    <Text style={styles.ctaText}>ANOTHER DOG</Text>
                    <Text style={styles.ctaArrow}>→</Text>
                </Pressable>
            </ScrollView>
        </View>
    )
}

const styles = StyleSheet.create({
    screen: { flex: 1, backgroundColor: COLORS.bg },
    band: { paddingHorizontal: SPACE[6], paddingBottom: SPACE[4] },
    bandKicker: { fontFamily: FONTS.medium, fontSize: 10, letterSpacing: 1.8, color: "rgba(255,255,255,0.85)", marginBottom: SPACE[1] },
    verdict: { fontFamily: FONTS.heading, fontSize: 74, lineHeight: 68, letterSpacing: -1.5, color: COLORS.white },
    verdictNot: { fontFamily: FONTS.heading, fontSize: 64, lineHeight: 60, letterSpacing: -1.3, color: COLORS.white },
    bandSub: { fontFamily: FONTS.body, fontSize: 13, color: "rgba(255,255,255,0.92)", marginTop: SPACE[2] },
    photoBox: { height: 236, backgroundColor: COLORS.viewfinder },
    camTag: { position: "absolute", top: 10, right: 10, backgroundColor: COLORS.viewfinder, paddingHorizontal: 7, paddingVertical: 4 },
    camTagText: { fontFamily: FONTS.heading, fontSize: 9, letterSpacing: 1.4, color: COLORS.white },
    scale: { position: "absolute", bottom: 10, right: 10, flexDirection: "row", alignItems: "center", gap: 6 },
    scaleLabel: { fontFamily: FONTS.medium, fontSize: 9, letterSpacing: 1, color: COLORS.white },
    scaleBar: { width: 74, height: 6, backgroundColor: COLORS.accent },
    toggleRow: { flexDirection: "row", alignItems: "center", paddingHorizontal: SPACE[6], paddingVertical: SPACE[2], borderBottomWidth: 2, borderBottomColor: "rgba(32,30,29,0.4)" },
    toggleLabel: { fontFamily: FONTS.medium, fontSize: 10, letterSpacing: 1.6, color: COLORS.ink },
    segment: { marginLeft: "auto", flexDirection: "row", borderWidth: 1, borderColor: COLORS.ink },
    segBtn: { paddingHorizontal: 13, paddingVertical: 8 },
    segBtnOn: { backgroundColor: COLORS.ink },
    segText: { fontFamily: FONTS.heading, fontSize: 11, letterSpacing: 0.9, color: COLORS.ink },
    segTextOn: { color: COLORS.white },
    breedBox: { paddingHorizontal: SPACE[6], paddingTop: SPACE[4] },
    breedName: { fontFamily: FONTS.heading, fontSize: 20, letterSpacing: -0.2, color: COLORS.ink },
    breedBlurb: { fontFamily: FONTS.body, fontSize: 12.5, color: COLORS.neutral700, marginTop: SPACE[1] },
    confBox: { paddingHorizontal: SPACE[6], paddingTop: SPACE[4], gap: SPACE[2] },
    confLabel: { fontFamily: FONTS.medium, fontSize: 10, letterSpacing: 1.6, color: COLORS.ink, marginBottom: SPACE[1] },
    barRow: { flexDirection: "row", alignItems: "center", gap: SPACE[3] },
    barName: { fontFamily: FONTS.medium, fontSize: 12, color: COLORS.ink, width: 96 },
    barTrack: { flex: 1, height: 14, backgroundColor: COLORS.neutral300 },
    barFill: { height: "100%" },
    barPct: { fontFamily: FONTS.heading, fontSize: 12, color: COLORS.ink, width: 52, textAlign: "right" },
    cta: { flexDirection: "row", alignItems: "center", backgroundColor: COLORS.accent, marginHorizontal: SPACE[6], marginTop: SPACE[8], paddingVertical: 15, paddingHorizontal: 18 },
    ctaText: { fontFamily: FONTS.heading, fontSize: 14, letterSpacing: 0.8, color: COLORS.white },
    ctaArrow: { fontFamily: FONTS.heading, fontSize: 14, color: COLORS.white, marginLeft: "auto" },
});