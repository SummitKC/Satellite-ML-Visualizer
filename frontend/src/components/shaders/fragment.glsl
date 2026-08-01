uniform sampler2D dayTexture;
uniform sampler2D nightTexture;
uniform vec3 lightDirection;

varying vec2 vUv;
varying vec3 vNormal;

void main() {

  //Get color values from the current day and night textures based on the UV position
  vec3 dayColor = texture2D(dayTexture, vUv).rgb;
  vec3 nightColor = texture2D(nightTexture, vUv).rgb;

  // Calculate the normal vector and light direction
  vec3 normal = normalize(vNormal);
  vec3 lightDir = normalize(lightDirection);

  //Get the dor product
  float dotNL = dot(normal, lightDir);
  float transitionFactor = smoothstep(-0.15, 0.15, dotNL);

  vec3 finalColor = mix(nightColor, dayColor, transitionFactor);


  gl_FragColor = vec4(finalColor, 1.0);
}