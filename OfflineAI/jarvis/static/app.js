const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const micBtn = document.getElementById("micBtn");
const listenBtn = document.getElementById("listenBtn");
const cameraBtn = document.getElementById("cameraBtn");
const cameraVideo = document.getElementById("cameraVideo");
const cameraOverlay = document.getElementById("cameraOverlay");

const modeSelect = document.getElementById("modeSelect");
const providerSelect = document.getElementById("providerSelect");
const speedProfileSelect = document.getElementById("speedProfileSelect");
const avatarSelect = document.getElementById("avatarSelect");
const speakToggle = document.getElementById("speakToggle");
const visionToggle = document.getElementById("visionToggle");

const avatarStage = document.getElementById("avatarStage");
const avatar3dHost = document.getElementById("avatar3dHost");
const avatarFallback = document.getElementById("avatarFallback");
const avatar = document.getElementById("avatar");

const intentChip = document.getElementById("intentChip");
const emotionChip = document.getElementById("emotionChip");
const visualEmotionChip = document.getElementById("visualEmotionChip");
const sourceChip = document.getElementById("sourceChip");
const modelChip = document.getElementById("modelChip");
const languageChip = document.getElementById("languageChip");
const speedChip = document.getElementById("speedChip");

const onlineBadge = document.getElementById("onlineBadge");
const visionBadge = document.getElementById("visionBadge");
const faceBadge = document.getElementById("faceBadge");
const languageBadge = document.getElementById("languageBadge");
const speedBadge = document.getElementById("speedBadge");
const assistantOrb = document.getElementById("assistantOrb");
const orbStatus = document.getElementById("orbStatus");
const quickActionButtons = Array.from(document.querySelectorAll("[data-quick-command]"));

const imagePortal = document.getElementById("imagePortal");
const portalFrame = imagePortal ? imagePortal.querySelector(".portal-frame") : null;
const parallaxBg = imagePortal ? imagePortal.querySelector(".parallax-layer.bg") : null;
const parallaxMid = imagePortal ? imagePortal.querySelector(".parallax-layer.mid") : null;
const parallaxGlow = imagePortal ? imagePortal.querySelector(".parallax-layer.glow") : null;
const heroImage = document.getElementById("heroImage");
const imageUpload = document.getElementById("imageUpload");

let cameraStream = null;
let faceDetectionTimer = null;
let visionPollingTimer = null;
let isBackendListening = false;
let latestVisualEmotion = "neutral";
let latestVisualConfidence = 0;
let visionAvailable = false;
let latestLanguage = "en";
let orbState = "idle";

let portalTiltX = 0;
let portalTiltY = 0;
let portalMoveX = 0;
let portalMoveY = 0;
let portalAudioPulse = 0;
let portalRaf = 0;

let threeAvatar = null;

const HERO_IMAGE_STORAGE_KEY = "jarvis.heroImage";
const DEFAULT_PORTAL_IMAGE = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
<defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1f6fa0"/>
        <stop offset="50%" stop-color="#105078"/>
        <stop offset="100%" stop-color="#12253a"/>
    </linearGradient>
</defs>
<rect width="1600" height="900" fill="url(#g1)"/>
<circle cx="1150" cy="180" r="140" fill="rgba(190,240,255,0.35)"/>
<circle cx="280" cy="760" r="260" fill="rgba(109,226,201,0.25)"/>
<text x="70" y="770" fill="#d8f7ff" font-size="56" font-family="Segoe UI, sans-serif">Load your character image for immersive mode</text>
</svg>
`)}`;

function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function setOrbState(state, statusText = "") {
    orbState = state;
    if (assistantOrb) {
        assistantOrb.classList.remove("idle", "listening", "thinking", "speaking");
        assistantOrb.classList.add(state || "idle");
    }
    if (orbStatus && statusText) {
        orbStatus.textContent = statusText;
    }
}

function setAvatarEmotion(emotion) {
    const emotions = ["neutral", "happy", "sad", "angry", "fear"];
    const normalized = emotion && emotions.includes(emotion) ? emotion : "neutral";

    if (avatar) {
        emotions.forEach((name) => avatar.classList.remove(name));
        avatar.classList.add(normalized);
    }

    if (threeAvatar) {
        threeAvatar.setEmotion(normalized);
    }
}

function setAvatarSpeaking(active) {
    if (active) {
        if (avatar) {
            avatar.classList.add("speaking");
        }
        setOrbState("speaking", "Speaking...");
    } else {
        if (avatar) {
            avatar.classList.remove("speaking");
        }
        if (isBackendListening) {
            setOrbState("listening", "Listening...");
        } else {
            setOrbState("idle", "Ready. Tap mic or type a message.");
        }
    }

    if (threeAvatar) {
        threeAvatar.setSpeaking(active);
    }
}

function setAvatarGender(gender) {
    if (avatar) {
        avatar.classList.remove("male", "female");
        avatar.classList.add(gender === "female" ? "female" : "male");
    }

    if (threeAvatar) {
        threeAvatar.setGender(gender === "female" ? "female" : "male");
    }
}

function pulseSpeakingByText(text) {
    const approxMs = Math.max(900, Math.min(7000, String(text || "").length * 26));
    kickPortalPulse(clamp(approxMs / 5200, 0.2, 1.1));
    setAvatarSpeaking(true);
    window.setTimeout(() => setAvatarSpeaking(false), approxMs);
}

function setOnlineBadge(status) {
    const hasOnline = Boolean(status.openai) || Boolean(status.ollama);
    if (hasOnline) {
        onlineBadge.className = "pill ok";
        const billionHint = status.prefer_billion_model && status.billion_model
            ? `, Billion: ${status.billion_model}`
            : "";
        onlineBadge.textContent = `Online model: ready (OpenAI: ${status.openai ? "on" : "off"}, Ollama: ${status.ollama ? "on" : "off"}${billionHint})`;
        return;
    }
    onlineBadge.className = "pill danger";
    onlineBadge.textContent = "Online model: unavailable (offline still works)";
}

function setVisionBadge(status) {
    visionAvailable = Boolean(status && status.available);

    if (!status || !visionAvailable) {
        visionBadge.className = "pill danger";
        visionBadge.textContent = "Vision: unavailable";
        return;
    }

    if (status.fer_enabled) {
        visionBadge.className = "pill ok";
        visionBadge.textContent = `Vision: ${status.backend}`;
        return;
    }

    visionBadge.className = "pill warn";
    visionBadge.textContent = "Vision: OpenCV fallback";
}

function setLanguageUI(language) {
    const value = String(language || "en").toLowerCase();
    latestLanguage = value;
    const label = value === "ta" ? "Tamil" : value === "mix" ? "Tamil + English" : "English";

    languageChip.textContent = `Language: ${value}`;
    languageBadge.className = "pill neutral";
    languageBadge.textContent = `Language: ${label}`;
}

function setSpeedUI(profile) {
    const value = String(profile || "balanced").toLowerCase();
    speedChip.textContent = `Speed: ${value}`;
    speedBadge.className = value === "turbo" ? "pill ok" : "pill neutral";
    speedBadge.textContent = `Speed: ${value}`;
}

function setPortalMood(emotion) {
    if (!portalFrame) {
        return;
    }

    const mood = String(emotion || "neutral").toLowerCase();
    if (mood === "happy") {
        portalFrame.style.boxShadow = "0 18px 40px rgba(121, 252, 197, 0.24)";
    } else if (mood === "sad") {
        portalFrame.style.boxShadow = "0 18px 40px rgba(134, 184, 255, 0.22)";
    } else if (mood === "angry") {
        portalFrame.style.boxShadow = "0 18px 40px rgba(255, 132, 132, 0.22)";
    } else if (mood === "fear") {
        portalFrame.style.boxShadow = "0 18px 40px rgba(255, 208, 133, 0.2)";
    } else {
        portalFrame.style.boxShadow = "0 14px 34px rgba(101, 207, 255, 0.16)";
    }
}

function updateChips(meta) {
    const intentLabel = meta.intent && meta.intent.tag ? meta.intent.tag : "unknown";
    const emotionLabel = meta.emotion && meta.emotion.label ? meta.emotion.label : "neutral";
    const sourceLabel = meta.source || "offline";
    const modelLabel = meta.model || "-";
    const languageLabel = meta.language || latestLanguage || "en";
    const speedLabel = meta.speed_profile || speedProfileSelect.value || "balanced";

    intentChip.textContent = `Intent: ${intentLabel}`;
    emotionChip.textContent = `Emotion: ${emotionLabel}`;
    sourceChip.textContent = `Source: ${sourceLabel}`;
    modelChip.textContent = `Model: ${modelLabel}`;
    setLanguageUI(languageLabel);
    setSpeedUI(speedLabel);

    setAvatarEmotion(emotionLabel);
    setPortalMood(emotionLabel);
    if (meta.online) {
        setOnlineBadge(meta.online);
    }
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function setPortalPointer(nx, ny) {
    if (!portalFrame) {
        return;
    }

    const x = clamp(nx, -1, 1);
    const y = clamp(ny, -1, 1);

    portalTiltY = x * 8.5;
    portalTiltX = -y * 6.5;
    portalMoveX = x * 12;
    portalMoveY = y * 10;

    portalFrame.style.setProperty("--pointer-x", `${(x * 0.5 + 0.5) * 100}%`);
    portalFrame.style.setProperty("--pointer-y", `${(y * 0.5 + 0.5) * 100}%`);

    if (threeAvatar) {
        threeAvatar.setTracking(x, y);
    }
}

function animatePortal() {
    if (!portalFrame) {
        return;
    }

    const pulseScale = 1.045 + portalAudioPulse * 0.02;
    portalFrame.style.transform = `perspective(1280px) rotateX(${portalTiltX.toFixed(2)}deg) rotateY(${portalTiltY.toFixed(2)}deg) translate3d(${portalMoveX.toFixed(2)}px, ${portalMoveY.toFixed(2)}px, 0)`;

    if (parallaxBg) {
        parallaxBg.style.transform = `translate3d(${(-portalMoveX * 0.32).toFixed(2)}px, ${(-portalMoveY * 0.32).toFixed(2)}px, 0)`;
    }
    if (parallaxMid) {
        parallaxMid.style.transform = `translate3d(${(-portalMoveX * 0.52).toFixed(2)}px, ${(-portalMoveY * 0.52).toFixed(2)}px, 0)`;
    }
    if (parallaxGlow) {
        parallaxGlow.style.transform = `translate3d(${(portalMoveX * 0.2).toFixed(2)}px, ${(portalMoveY * 0.2).toFixed(2)}px, 0)`;
    }
    if (heroImage) {
        heroImage.style.transform = `translate3d(${(portalMoveX * -0.62).toFixed(2)}px, ${(portalMoveY * -0.62).toFixed(2)}px, 0) scale(${pulseScale.toFixed(3)})`;
    }

    portalAudioPulse = Math.max(0, portalAudioPulse - 0.025);
    portalRaf = window.requestAnimationFrame(animatePortal);
}

function kickPortalPulse(strength = 0.65) {
    portalAudioPulse = Math.min(1.6, portalAudioPulse + strength);
}

function setPortalImage(source, persist = true) {
    if (!heroImage || !imagePortal) {
        return;
    }

    heroImage.src = source;
    imagePortal.classList.add("has-image");
    if (persist) {
        try {
            localStorage.setItem(HERO_IMAGE_STORAGE_KEY, source);
        } catch {
            // Ignore localStorage quota/privacy restrictions.
        }
    }
}

function initImagePortal() {
    if (!imagePortal || !portalFrame) {
        return;
    }

    let loaded = false;
    try {
        const stored = localStorage.getItem(HERO_IMAGE_STORAGE_KEY);
        if (stored) {
            setPortalImage(stored, false);
            loaded = true;
        }
    } catch {
        // Continue with default image.
    }

    if (!loaded) {
        setPortalImage(DEFAULT_PORTAL_IMAGE, false);
    }

    portalFrame.addEventListener("pointermove", (event) => {
        const rect = portalFrame.getBoundingClientRect();
        const nx = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
        const ny = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
        setPortalPointer(nx, ny);
    });

    portalFrame.addEventListener("pointerleave", () => {
        setPortalPointer(0, 0);
    });

    if (imageUpload) {
        imageUpload.addEventListener("change", () => {
            const file = imageUpload.files && imageUpload.files[0];
            if (!file) {
                return;
            }

            const reader = new FileReader();
            reader.onload = () => {
                const result = String(reader.result || "");
                if (!result.startsWith("data:image/")) {
                    addMessage("ai", "Please choose a valid image file.");
                    return;
                }
                setPortalImage(result, true);
                addMessage("ai", "Interactive image loaded. The visual core is now linked.");
            };
            reader.readAsDataURL(file);
        });
    }

    setPortalPointer(0, 0);
    if (!portalRaf) {
        animatePortal();
    }
}

async function sendMessage(text) {
    const userText = String(text || "").trim();
    if (!userText) {
        return;
    }

    addMessage("user", userText);
    messageInput.value = "";
    setOrbState("thinking", "Thinking...");

    try {
        const payload = {
            message: userText,
            mode: modeSelect.value,
            provider: providerSelect.value,
            speed_profile: speedProfileSelect.value,
            persona: "JARVIS",
            avatar: avatarSelect.value,
            visual_emotion: latestVisualConfidence >= 0.45 ? latestVisualEmotion : "",
            speak: speakToggle.checked,
        };

        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.detail || "Failed to get assistant response");
        }

        const data = await res.json();
        const reply = data.reply || "I could not produce a response.";

        addMessage("ai", reply);
        updateChips(data);
        pulseSpeakingByText(reply);
    } catch (error) {
        addMessage("ai", `Error: ${error.message}`);
        setOrbState("idle", "Ready. Tap mic or type a message.");
    }
}

async function loadConfigAndHistory() {
    try {
        const [cfgRes, historyRes] = await Promise.all([
            fetch("/api/config"),
            fetch("/api/history?limit=8"),
        ]);

        if (cfgRes.ok) {
            const cfg = await cfgRes.json();
            if (cfg.online) {
                setOnlineBadge(cfg.online);
            }
            if (cfg.vision) {
                setVisionBadge(cfg.vision);
            }
            if (Array.isArray(cfg.speed_profiles) && speedProfileSelect) {
                const desired = cfg.default_speed_profile || "balanced";
                const exists = cfg.speed_profiles.some((item) => item === desired);
                speedProfileSelect.value = exists ? desired : "balanced";
                setSpeedUI(speedProfileSelect.value);
            } else {
                setSpeedUI(speedProfileSelect.value || "balanced");
            }

            setLanguageUI("en");

            const welcome = cfg.user_name
                ? `Hi ${cfg.user_name}. I am JARVIS, your voice assistant. What should we do first?`
                : "Hi, I am JARVIS. I am ready to assist you in Tamil or English.";
            addMessage("ai", welcome);
            pulseSpeakingByText(welcome);
            setOrbState("idle", "Ready. Tap mic or type a message.");
        }

        if (historyRes.ok) {
            const history = await historyRes.json();
            const turns = Array.isArray(history.history) ? history.history.slice(-4) : [];
            turns.forEach((turn) => {
                if (turn.user) {
                    addMessage("user", turn.user);
                }
                if (turn.ai) {
                    addMessage("ai", turn.ai);
                }
            });
        }
    } catch (error) {
        addMessage("ai", `Startup warning: ${error.message}`);
    }
}

function stopFaceDetection() {
    if (faceDetectionTimer) {
        window.clearInterval(faceDetectionTimer);
        faceDetectionTimer = null;
    }
}

function setFaceBadge(found, detailText = "") {
    if (found) {
        faceBadge.className = "pill ok";
        faceBadge.textContent = detailText ? `Face: detected (${detailText})` : "Face: detected";
        kickPortalPulse(0.12);
        return;
    }
    faceBadge.className = "pill neutral";
    faceBadge.textContent = detailText || "Face: searching";
}

function startFaceDetection() {
    stopFaceDetection();

    if (!("FaceDetector" in window)) {
        faceBadge.className = "pill neutral";
        faceBadge.textContent = "Face: API unavailable";
        return;
    }

    const detector = new window.FaceDetector({
        fastMode: true,
        maxDetectedFaces: 1,
    });

    faceDetectionTimer = window.setInterval(async () => {
        if (!cameraStream || cameraVideo.readyState < 2) {
            return;
        }

        try {
            const faces = await detector.detect(cameraVideo);
            const hasFace = Array.isArray(faces) && faces.length > 0;
            setFaceBadge(hasFace);

            if (hasFace && faces[0] && portalFrame) {
                const frameW = cameraVideo.videoWidth || 1;
                const frameH = cameraVideo.videoHeight || 1;
                const face = faces[0].boundingBox;
                const cx = (face.x + face.width * 0.5) / frameW;
                const cy = (face.y + face.height * 0.5) / frameH;
                setPortalPointer((cx - 0.5) * 1.6, (cy - 0.5) * 1.6);
            }
        } catch {
            setFaceBadge(false);
        }
    }, 1200);
}

function stopVisionPolling() {
    if (visionPollingTimer) {
        window.clearInterval(visionPollingTimer);
        visionPollingTimer = null;
    }
}

function captureFrameDataUrl() {
    if (!cameraStream || cameraVideo.readyState < 2) {
        return "";
    }

    const canvas = document.createElement("canvas");
    const w = cameraVideo.videoWidth || 640;
    const h = cameraVideo.videoHeight || 360;
    canvas.width = Math.min(640, w);
    canvas.height = Math.round((canvas.width / w) * h);

    const ctx = canvas.getContext("2d");
    if (!ctx) {
        return "";
    }

    ctx.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.72);
}

async function pollVisionEmotion() {
    if (!visionToggle.checked || !visionAvailable || !cameraStream) {
        return;
    }

    const frame = captureFrameDataUrl();
    if (!frame) {
        return;
    }

    try {
        const res = await fetch("/api/vision/emotion", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ frame, source: "camera" }),
        });

        if (!res.ok) {
            return;
        }

        const data = await res.json();
        const emotion = data.emotion || "neutral";
        const confidence = Number(data.confidence || 0);
        const faceCount = Number(data.face_count || 0);

        latestVisualEmotion = emotion;
        latestVisualConfidence = confidence;

        visualEmotionChip.textContent = `Vision Emotion: ${emotion} (${(confidence * 100).toFixed(0)}%)`;

        if (faceCount > 0) {
            setFaceBadge(true, `${faceCount}`);
        } else {
            setFaceBadge(false, "Face: not detected");
        }

        if (confidence >= 0.55) {
            setAvatarEmotion(emotion);
            setPortalMood(emotion);
        }
    } catch {
        // Keep current UI state if a single frame request fails.
    }
}

function startVisionPolling() {
    stopVisionPolling();
    if (!visionToggle.checked || !visionAvailable) {
        return;
    }

    visionPollingTimer = window.setInterval(() => {
        pollVisionEmotion();
    }, 3200);
}

async function toggleCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
        cameraStream = null;
        cameraVideo.srcObject = null;
        cameraVideo.classList.remove("active");
        cameraOverlay.classList.remove("hidden");
        cameraOverlay.textContent = "Camera is off";
        cameraBtn.textContent = "Start Camera";
        stopFaceDetection();
        stopVisionPolling();
        faceBadge.className = "pill neutral";
        faceBadge.textContent = "Face: not detected";
        setPortalPointer(0, 0);
        return;
    }

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: "user",
            },
            audio: false,
        });

        cameraVideo.srcObject = cameraStream;
        cameraVideo.classList.add("active");
        cameraOverlay.classList.add("hidden");
        cameraBtn.textContent = "Stop Camera";

        startFaceDetection();
        startVisionPolling();
    } catch (error) {
        cameraOverlay.classList.remove("hidden");
        cameraOverlay.textContent = `Camera error: ${error.message}`;
    }
}

async function backendListen() {
    if (isBackendListening) {
        return;
    }

    isBackendListening = true;
    listenBtn.textContent = "Listening...";

    try {
        const res = await fetch("/api/listen", {
            method: "POST",
        });

        const data = await res.json();
        if (res.ok && data.ok && data.transcript) {
            messageInput.value = data.transcript;
            kickPortalPulse(0.24);
            await sendMessage(data.transcript);
        } else {
            addMessage("ai", data.message || "No speech captured.");
        }
    } catch (error) {
        addMessage("ai", `Listen error: ${error.message}`);
    } finally {
        listenBtn.textContent = "Listen (Backend Mic)";
        isBackendListening = false;
    }
}

function browserMicListen() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        addMessage("ai", "Browser speech recognition is unavailable. Try backend Listen button.");
        return;
    }

    const recognition = new Recognition();
    recognition.lang = latestLanguage === "ta" ? "ta-IN" : "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    micBtn.textContent = "Mic...";

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        messageInput.value = transcript;
        micBtn.textContent = "Mic";
        await sendMessage(transcript);
    };

    recognition.onerror = (event) => {
        micBtn.textContent = "Mic";
        addMessage("ai", `Mic error: ${event.error}`);
    };

    recognition.onend = () => {
        micBtn.textContent = "Mic";
    };

    recognition.start();
}

class ThreeAvatar {
    constructor(host) {
        this.host = host;
        this.THREE = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.root = null;
        this.clock = null;
        this.speaking = false;
        this.emotion = "neutral";
        this.trackX = 0;
        this.trackY = 0;

        this.leftBrow = null;
        this.rightBrow = null;
        this.leftEye = null;
        this.rightEye = null;
        this.mouth = null;
        this.hair = null;
        this.rings = [];

        this._raf = 0;
        this._resizeHandler = () => this.resize();
    }

    async init() {
        try {
            this.THREE = await import("https://unpkg.com/three@0.165.0/build/three.module.js");
        } catch {
            return false;
        }

        const THREE = this.THREE;
        this.scene = new THREE.Scene();
        this.clock = new THREE.Clock();

        this.camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
        this.camera.position.set(0, 1.45, 3.25);

        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.host.appendChild(this.renderer.domElement);

        const ambient = new THREE.AmbientLight(0x8ad9ff, 0.7);
        this.scene.add(ambient);

        const key = new THREE.DirectionalLight(0xbbe8ff, 1.2);
        key.position.set(2, 3, 3);
        this.scene.add(key);

        const rim = new THREE.DirectionalLight(0x64caff, 0.7);
        rim.position.set(-2, 2, -2);
        this.scene.add(rim);

        const root = new THREE.Group();
        this.root = root;
        this.scene.add(root);

        const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1f607a, metalness: 0.35, roughness: 0.42 });
        const skinMat = new THREE.MeshStandardMaterial({ color: 0xe3aa82, roughness: 0.58 });
        const darkMat = new THREE.MeshStandardMaterial({ color: 0x2e3138, roughness: 0.55 });

        const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.54, 1.1, 8, 16), bodyMat);
        torso.position.set(0, -0.3, 0);
        root.add(torso);

        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.18, 0.2, 20), skinMat);
        neck.position.set(0, 0.58, 0.02);
        root.add(neck);

        const head = new THREE.Mesh(new THREE.SphereGeometry(0.5, 40, 32), skinMat);
        head.position.set(0, 1.1, 0.03);
        root.add(head);

        this.hair = new THREE.Mesh(new THREE.SphereGeometry(0.53, 36, 26), darkMat.clone());
        this.hair.position.set(0, 1.22, -0.01);
        this.hair.scale.set(1.03, 0.72, 1.02);
        root.add(this.hair);

        this.leftEye = new THREE.Mesh(new THREE.SphereGeometry(0.058, 16, 16), new THREE.MeshStandardMaterial({ color: 0x132f3c }));
        this.rightEye = this.leftEye.clone();
        this.leftEye.position.set(-0.16, 1.12, 0.42);
        this.rightEye.position.set(0.16, 1.12, 0.42);
        root.add(this.leftEye);
        root.add(this.rightEye);

        this.leftBrow = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.022, 0.03), new THREE.MeshStandardMaterial({ color: 0x422f20 }));
        this.rightBrow = this.leftBrow.clone();
        this.leftBrow.position.set(-0.16, 1.22, 0.39);
        this.rightBrow.position.set(0.16, 1.22, 0.39);
        root.add(this.leftBrow);
        root.add(this.rightBrow);

        this.mouth = new THREE.Mesh(
            new THREE.TorusGeometry(0.078, 0.018, 12, 36, Math.PI),
            new THREE.MeshStandardMaterial({ color: 0x8f3441, roughness: 0.45 })
        );
        this.mouth.position.set(0, 0.93, 0.43);
        this.mouth.rotation.x = Math.PI;
        root.add(this.mouth);

        const ringMat = new THREE.MeshStandardMaterial({ color: 0x5de5ff, emissive: 0x2a7ca5, metalness: 0.35, roughness: 0.35 });
        for (let i = 0; i < 3; i += 1) {
            const ring = new THREE.Mesh(new THREE.TorusGeometry(0.92 + i * 0.18, 0.006, 12, 80), ringMat.clone());
            ring.position.set(0, 1.03, -0.14);
            ring.rotation.x = 1.24;
            this.rings.push(ring);
            root.add(ring);
        }

        this.setGender("male");
        this.setEmotion("neutral");
        this.resize();
        this.animate();

        window.addEventListener("resize", this._resizeHandler);
        return true;
    }

    setGender(gender) {
        if (!this.hair) {
            return;
        }
        if (gender === "female") {
            this.hair.material.color.set(0x5b4539);
            this.hair.scale.set(1.08, 0.85, 1.08);
            this.hair.position.set(0, 1.2, 0.0);
        } else {
            this.hair.material.color.set(0x2e3138);
            this.hair.scale.set(1.03, 0.72, 1.02);
            this.hair.position.set(0, 1.22, -0.01);
        }
    }

    setEmotion(emotion) {
        this.emotion = emotion || "neutral";
    }

    setSpeaking(active) {
        this.speaking = Boolean(active);
    }

    setTracking(x, y) {
        this.trackX = clamp(Number(x || 0), -1, 1);
        this.trackY = clamp(Number(y || 0), -1, 1);
    }

    resize() {
        if (!this.renderer || !this.camera) {
            return;
        }
        const rect = this.host.getBoundingClientRect();
        const width = Math.max(10, rect.width);
        const height = Math.max(10, rect.height);
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height, false);
    }

    animate() {
        if (!this.renderer || !this.scene || !this.camera || !this.root || !this.clock) {
            return;
        }

        const t = this.clock.getElapsedTime();
        this.root.position.y = Math.sin(t * 1.15) * 0.04;
        this.root.rotation.y = Math.sin(t * 0.5) * 0.12 + this.trackX * 0.2;
        this.root.rotation.x = this.trackY * 0.08;

        if (this.leftEye && this.rightEye) {
            this.leftEye.position.x = -0.16 + this.trackX * 0.015;
            this.leftEye.position.y = 1.12 - this.trackY * 0.01;
            this.rightEye.position.x = 0.16 + this.trackX * 0.015;
            this.rightEye.position.y = 1.12 - this.trackY * 0.01;
        }

        if (this.leftBrow && this.rightBrow && this.leftEye && this.rightEye && this.mouth) {
            this.leftBrow.rotation.z = 0;
            this.rightBrow.rotation.z = 0;
            this.leftEye.scale.y = 1;
            this.rightEye.scale.y = 1;
            this.mouth.scale.set(1, 1, 1);
            this.mouth.position.y = 0.93;

            if (this.emotion === "happy") {
                this.mouth.scale.x = 1.22;
                this.mouth.scale.y = 1.2;
                this.leftBrow.rotation.z = -0.06;
                this.rightBrow.rotation.z = 0.06;
            } else if (this.emotion === "sad") {
                this.mouth.scale.x = 0.86;
                this.mouth.scale.y = -0.95;
                this.mouth.position.y = 0.9;
                this.leftBrow.rotation.z = 0.13;
                this.rightBrow.rotation.z = -0.13;
            } else if (this.emotion === "angry") {
                this.leftBrow.rotation.z = 0.2;
                this.rightBrow.rotation.z = -0.2;
                this.mouth.scale.x = 0.9;
                this.mouth.scale.y = 0.78;
            } else if (this.emotion === "fear") {
                this.leftEye.scale.y = 1.4;
                this.rightEye.scale.y = 1.4;
                this.mouth.scale.x = 0.8;
                this.mouth.scale.y = 1.35;
            }

            if (this.speaking) {
                this.mouth.scale.y *= 0.9 + Math.abs(Math.sin(t * 11.5)) * 0.9;
            }
        }

        this.rings.forEach((ring, idx) => {
            ring.rotation.z += 0.0018 + idx * 0.0007;
            const pulse = this.speaking ? (0.25 + Math.abs(Math.sin(t * 5 + idx))) : 0.08;
            ring.material.emissiveIntensity = pulse;
        });

        this.renderer.render(this.scene, this.camera);
        this._raf = window.requestAnimationFrame(() => this.animate());
    }

    dispose() {
        if (this._raf) {
            window.cancelAnimationFrame(this._raf);
        }
        window.removeEventListener("resize", this._resizeHandler);
    }
}

async function init3DAvatar() {
    if (!avatar3dHost) {
        return;
    }

    const engine = new ThreeAvatar(avatar3dHost);
    const ok = await engine.init();
    if (!ok) {
        return;
    }

    threeAvatar = engine;
    avatarStage.classList.add("three-ready");
    setAvatarGender(avatarSelect.value);
    setAvatarEmotion("neutral");
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendMessage(messageInput.value);
});

micBtn.addEventListener("click", browserMicListen);
listenBtn.addEventListener("click", backendListen);
cameraBtn.addEventListener("click", toggleCamera);

avatarSelect.addEventListener("change", () => {
    setAvatarGender(avatarSelect.value);
});

speedProfileSelect.addEventListener("change", () => {
    setSpeedUI(speedProfileSelect.value);
});

visionToggle.addEventListener("change", () => {
    if (!visionToggle.checked) {
        stopVisionPolling();
        visualEmotionChip.textContent = "Vision Emotion: off";
        return;
    }

    visualEmotionChip.textContent = "Vision Emotion: neutral";
    if (cameraStream) {
        startVisionPolling();
    }
});

window.addEventListener("beforeunload", () => {
    stopFaceDetection();
    stopVisionPolling();
    if (portalRaf) {
        window.cancelAnimationFrame(portalRaf);
        portalRaf = 0;
    }
    if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
    }
    if (threeAvatar) {
        threeAvatar.dispose();
    }
});

(async () => {
    await Promise.all([
        loadConfigAndHistory(),
        init3DAvatar(),
    ]);
    initImagePortal();
})();
