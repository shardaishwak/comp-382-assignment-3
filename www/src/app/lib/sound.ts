""

/**
 * Simple oscillator-based sound effects using the Web Audio API
 */

let audioCtx: AudioContext | null = null;
function getAudioCtx(): AudioContext | null {
    if (typeof window === "undefined") return null;
    if (!audioCtx) audioCtx = new window.AudioContext;

    return audioCtx;
}

export function playTone(freq: number, duration: number = 0.08, type: OscillatorType = "square", volume: number = 0.85) {
    if (!audioCtx) return;
    try {
        const oscillator = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        oscillator.type = type;
        oscillator.frequency.value = freq;
        gain.gain.value = volume;
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        oscillator.connect(gain).connect(audioCtx.destination);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + duration);
        
    } catch(e) {
        console.error(e)
    }
}

// Place a domino
function playPlace() {
    getAudioCtx()
    playTone(520, 0.07, "square", 0.05);
}
// Remove a domino
function playRemove() {
    getAudioCtx()
    playTone(280, 0.1, "sawtooth", 0.04);
}
// Dominos matched
function playMatch() {
    getAudioCtx();
    [520, 650, 800, 1050].forEach((f, i) => setTimeout(() => playTone(f, 0.15, "sine", 0.08), i * 100)); // each sound distany 100ms
}
// Error
function playError() {
    getAudioCtx();
    playTone(180, 0.15, "sawtooth", 0.06);
}
// Tick
function playTick() {
    getAudioCtx()
    playTone(800, 0.03, "sine", 0.02);
}


const soundEffect = {
    place: playPlace,
    remove: playRemove,
    match: playMatch,
    error: playError,
    tick: playTick
}

export default soundEffect;