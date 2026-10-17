uniform sampler2D icon;
uniform float minIconSize;

varying vec3 vGradientStart;
varying vec3 vGradientEnd;
varying float vPointSize;

// Radius of the fallback dot as a fraction of the icon's width (about the size of the old dots)
const float DOT_RADIUS = 0.35;

// How much the icon's black outlines and white highlights scale the gradient color
const float SHADOW = 0.1;
const float HIGHLIGHT = 1.2;

void main() {
  // The icon is grayscale: its alpha is the shape and its gray level the shading.
  // gl_PointCoord's y runs downwards, so flip it to read the image upright
  vec4 iconTexel = texture2D(icon, vec2(gl_PointCoord.x, 1.0 - gl_PointCoord.y));

  // Blend from the gradient's start color at the top-left to its end color at the bottom-right
  vec3 color = mix(vGradientStart, vGradientEnd, (gl_PointCoord.x + gl_PointCoord.y) * 0.5);

  if (vPointSize < minIconSize) {
    // Too small on screen to make out the satellite shape, so draw a plain round dot
    if (length(gl_PointCoord - 0.5) > DOT_RADIUS) discard;
  } else {
    if (iconTexel.a < 0.5) discard;
    color *= mix(SHADOW, HIGHLIGHT, iconTexel.r);
  }

  gl_FragColor = vec4(color, 1.0);

  // Apply the renderer's tone mapping and color space like three's built-in
  // materials do, so the colors match the cluster colors elsewhere
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
