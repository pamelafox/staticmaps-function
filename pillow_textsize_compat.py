"""
Pillow 10.x compatibility patch for py-staticmaps.

This module provides a monkey patch to restore the textsize() method
that was removed in Pillow 10.0.0 and replaced with textbbox().

This ensures compatibility with py-staticmaps 0.4.0 while maintaining
the security benefits of Pillow 10.3.0.
"""

from PIL import ImageDraw


def textsize(self, text, font=None, *args, **kwargs):
    """
    Compatibility method for Pillow 10.x that provides the old textsize() behavior.

    This method uses the new textbbox() method and converts the result to the
    (width, height) tuple that textsize() used to return.

    Args:
        text: The text to measure
        font: The font to use (optional)
        *args, **kwargs: Additional arguments passed to textbbox

    Returns:
        tuple: (width, height) of the text
    """
    # Use textbbox with anchor point (0, 0) and convert to size
    bbox = self.textbbox((0, 0), text, font=font, *args, **kwargs)
    # bbox is (left, top, right, bottom), so width = right - left, height = bottom - top
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


# Only patch if textsize doesn't exist (i.e., Pillow 10.x)
if not hasattr(ImageDraw.ImageDraw, "textsize"):
    ImageDraw.ImageDraw.textsize = textsize
