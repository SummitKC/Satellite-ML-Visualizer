// Touch-first devices (phones, tablets) have much weaker GPUs and less memory
// than desktops, so the scene uses lighter settings on them
export const isMobileDevice = window.matchMedia("(pointer: coarse)").matches;
