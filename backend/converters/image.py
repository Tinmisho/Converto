"""
Image conversion and resizing via libvips (pyvips).
libvips is significantly faster than Pillow/ImageMagick for large images
and handles HEIC, AVIF, WEBP natively.
"""
import pyvips


def convert_image(
    input_path: str,
    output_path: str,
    target_ext: str,
    resize_opts: dict | None = None,
):
    # Load — use sequential access for large images (lower memory)
    img = pyvips.Image.new_from_file(input_path, access="sequential")

    # Apply resize if requested
    if resize_opts:
        img = _resize(img, resize_opts)

    # Format-specific save options
    save_opts = _save_options(target_ext)

    img.write_to_file(output_path, **save_opts)


def _resize(img: pyvips.Image, opts: dict) -> pyvips.Image:
    scale = opts.get("scale")
    width = opts.get("width")
    height = opts.get("height")

    if scale:
        return img.resize(scale)

    orig_w = img.width
    orig_h = img.height

    if width and height:
        # Fit within box, preserve aspect ratio
        scale_w = width / orig_w
        scale_h = height / orig_h
        return img.resize(min(scale_w, scale_h))

    if width:
        return img.resize(width / orig_w)

    if height:
        return img.resize(height / orig_h)

    return img


def _save_options(ext: str) -> dict:
    ext = ext.lower().lstrip(".")
    options = {
        "jpg":  {"Q": 90},
        "jpeg": {"Q": 90},
        "webp": {"Q": 85, "lossless": False},
        "avif": {"Q": 80},
        "png":  {"compression": 6},
        "tiff": {"compression": "deflate"},
    }
    return options.get(ext, {})
