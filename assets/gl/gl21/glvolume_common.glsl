/*
 * This file contains the sample_volume function, shared by the different
 * glvolume fragment shaders.
 *
 * The sample_volume function looks up a specific voxel value, and applies
 * clipping and colouring.  It returns false if the fragment should be
 * discarded, otherwise it returns true.
 *
 * The voxValue output is normalised to the range [0, 1] according to the
 * current display range.
 *
 * The following jinja2 constants can be set to configure the shader:
 *
 *  - textureIs2D: If True, the shader is configured to sample from a 2D
 *                 texture. Otherwise, a 3D texture is assumed.
 *
 * Author: Paul McCarthy <pauldmccarthy@gmail.com>
 */
bool sample_volume(vec3      texCoord,
                   vec3      clipTexCoord,
                   vec3      modTexCoord,
                   out float voxValue,
                   out vec4  finalColour) {

  float clipValue;
  float modValue;
  bool  negCmap = false;

  /*
   * Look up the voxel value. If using a 2D
   * texture, we assume that the coordinates
   * are stored in the first two channels of
   * the texCoord.
   */
  {% if textureIs2D %}

  if (useSpline) voxValue = spline_interp(imageTexture,
                                          texCoord.xy,
                                          texShape.xy,
                                          0);
  else           voxValue = texture2D(imageTexture, texCoord.xy).r;

  {% else %}

  if (useSpline) voxValue = spline_interp(imageTexture,
                                          texCoord,
                                          texShape,
                                          0);
  else           voxValue = texture3D(    imageTexture, texCoord).r;

  {% endif %}

  /* Skip nan values */
  if (voxValue != voxValue) {
    return false;
  }

  /*
   * Look up the clip value
   */
  if (imageIsClip) { clipValue = voxValue; }
  /*

  * Out of bounds of the clipping texture
   */
  else if (any(lessThan(   fragClipTexCoord, vec3(0))) ||
           any(greaterThan(fragClipTexCoord, vec3(1)))) {
    clipValue = clipLow + 0.5 * (clipHigh - clipLow);
  }

  else if (useSpline)   clipValue = spline_interp(clipTexture,
                                                  clipTexCoord,
                                                  clipImageShape,
                                                  0);
  else                  clipValue = texture3D(    clipTexture,
                                                  clipTexCoord).r;

  /*
   * And the modulate value value
   */
  if (imageIsMod || !modulateAlpha) {
    modValue = voxValue;
  }
  /*
   * Out of bounds of the mod texture
   */
  else if (any(lessThan(   fragModTexCoord, vec3(0))) ||
           any(greaterThan(fragModTexCoord, vec3(1)))) {
    modValue = 1;
  }

  else if (useSpline)   modValue = spline_interp(modulateTexture,
                                                 modTexCoord,
                                                 modImageShape,
                                                 0);
  else                  modValue = texture3D(    modulateTexture,
                                                 modTexCoord).r;
  /*
   * If we are using a negative colour map,
   * and the voxel value is below the negative
   * threshold (texZero) invert the voxel
   * value, and set a flag telling the code
   * below to use the neagtive colour map.
   */
  if (useNegCmap && voxValue <= texZero) {

    negCmap  = true;
    voxValue = texZero + (texZero - voxValue);

    // Invert the clip value as well, if the
    // image and clip textures are the same
    if (imageIsClip) {
      clipValue = texZero + (texZero - clipValue);
    }
  }

  /*
   * Clip out of range voxel values
   */

  if ((!invertClip && (clipValue <= clipLow || clipValue >= clipHigh)) ||
      ( invertClip && (clipValue >= clipLow && clipValue <= clipHigh))) {
    return false;
  }

  /*
   * Transform the voxel value to a colour map texture
   * coordinate, and look up the colour for the voxel value
   */
  voxValue = (img2CmapXform * vec4(voxValue, 0, 0, 1)).x;

  if (negCmap) finalColour = texture1D(negColourTexture, voxValue);
  else         finalColour = texture1D(colourTexture,    voxValue);

  /*
   * modulate alpha by voxel value -  voxels equal to
   * low display range get alpha=0, and those equal
   * to high display range get alpha=1
   */
  if (modulateAlpha) {
      finalColour.a = modValue;
  }

  return true;
}
