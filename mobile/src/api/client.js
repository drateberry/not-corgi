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
import * as FileSystem from "expo-file-system/legacy";

import { API_BASE_URL, REQUEST_TIMEOUT_MS } from "../constants";

const TIMED_OUT = { timedOut: true };
const ok = (data) => ({ ok: true, data });
const fail = (code, message, retryable) => ({ ok: false, code, message, retryable });

/*
* fetch with a timeout. Timeout means either a connection or server issue.
*/
async function fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch (url, {...options, signal: controller.signal });
    } finally {
        clearTimeout(timer);
    }
}

export async function predict(imageUri) {
    let res;
    try {
        res = await Promise.race([ 
            FileSystem.uploadAsync(`${API_BASE_URL}/predict`, imageUri, {
                httpMethod: "POST",
                uploadType: FileSystem.FileSystemUploadType.MULTIPART,
                fieldName: "image",
                mimeType: "image/jpeg",
            }),
            new Promise((resolve) => setTimeout(() => resolve(TIMED_OUT), REQUEST_TIMEOUT_MS)),
        ]);
    } catch (e) {
        console.log("upload error:", e?.name, e?.message, JSON.stringify(e));
        return fail(
            "unreachable",
            `Can't reach the server at ${API_BASE_URL}. Check the API is running and the address is right.`,
            false
        );
    }

    if (res === TIMED_OUT) {
        return fail("timeout", "The server took too long. Try again.", true);
    }

    let body;
    try {
        body = JSON.parse(res.body);        
    } catch (e) {
        return fail("bad_response", "The server sent something unreadable.", false);
    }

    if (res.status >= 400) {
        return fail(
            body.code ?? "http_error",
            body.error ?? `Server returned ${res.status}.`,
            res.status >= 500
        );
    }

    return ok(body);
}

export async function checkHealth() {
    try {
        const res = await fetchWithTimeout(`${API_BASE_URL}/health`);
        const body = await res.json();
        return body.model_loaded ? ok(body) : fail("no_model", "API is up but no AI model is reachable.", false);
    } catch (e) {
        return fail("unreachable", `No answer from ${API_BASE_URL}.`, false);
    }
}
