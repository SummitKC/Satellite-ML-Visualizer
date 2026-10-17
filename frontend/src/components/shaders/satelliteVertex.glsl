uniform float size;
uniform float viewportHeight;

// The two ends of this satellite's color gradient
attribute vec3 gradientStart;
attribute vec3 gradientEnd;

varying vec3 vGradientStart;
varying vec3 vGradientEnd;
varying float vPointSize;

void main() {
  vGradientStart = gradientStart;
  vGradientEnd = gradientEnd;

  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);

  // Size each icon so it spans `size` scene units: projectionMatrix[1][1] is
  // 1 / tan(fov / 2), so this is that width projected to pixels at this depth
  gl_PointSize = size * projectionMatrix[1][1] * viewportHeight / (2.0 * -mvPosition.z);
  gl_Position = projectionMatrix * mvPosition;

  vPointSize = gl_PointSize;
}
