uniform sampler2D dayTexture;
varying vec2 vUv;

void main() {
  gl_FragColor = texture2D(dayTexture, vUv);
}