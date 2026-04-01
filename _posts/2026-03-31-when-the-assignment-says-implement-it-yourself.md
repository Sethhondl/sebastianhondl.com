---
layout: post
title: "When the Assignment Says Implement It Yourself"
date: 2026-03-31
categories: [development, ai]
tags: [claude-code, python, api, debugging]
read_time: 4
word_count: 976
---

The first function in the computer vision homework is `image_properties()`. It loads an image, loops through every pixel, and computes the average intensity. One line of NumPy — `img.mean()` — does the same thing. But ME5286 Vision HW1 says to use nested loops and accumulate manually, so that's what you do. Forty seconds of Python churning through 3000 by 2436 pixels on Alma Thomas's *The Eclipse*, and the first number comes back wrong.

Not obviously wrong. Just low — suspiciously low for a painting full of bright reds, oranges, and blues. The bug was silent: `uint8` arithmetic wraps at 255, so adding two pixel values like 200 and 180 doesn't give you 380. It gives you 124. Every addition that crossed 255 quietly folded back to zero, dragging the running sum downward without raising an error. The fix was casting each pixel to Python's `int()` before accumulating — arbitrary-precision integers that don't wrap. In NumPy you'd use `.astype(np.int32)` or `np.float64`, but with pure Python loops, `int()` was the natural choice.

That was the first ten minutes. The rest of the evening was more of the same: reimplementing things the slow way and discovering why the fast way exists.

## The Sobel Pipeline

Problem 2 asks you to implement Sobel edge detection by hand. Define the 3x3 kernels, pad the image, slide them across every pixel with nested loops, and produce gradient images. OpenCV's `cv2.Sobel()` does this in one call. The manual version has three places to go wrong, and they're all connected.

**Padding.** The image needs a one-pixel border so the 3x3 kernel has neighbors to read at the edges. Zero-padding — surrounding the image with black pixels — creates a steep intensity cliff at every border. The Sobel kernel reads that cliff as a strong edge, so you get bright lines around the entire image that have nothing to do with the actual content. Padding with 127 instead — the midpoint of the 0–255 range — keeps the border at a neutral intensity. When the kernel subtracts neighboring values across the boundary, the differences land near zero. No false edges.

**Signed intermediates.** The Sobel kernel has negative coefficients. A region where intensity decreases left-to-right produces a negative convolution result. `uint8` can't represent negative numbers — it clips to zero, and you lose half your edge information. The fix is computing everything in `float64` and only clipping to `[0, 255]` at the end, when you need a displayable image.

**Magnitude from the right source.** This is where the first two decisions become one pipeline. Problem 2B asks for edge magnitude: `sqrt(Gx² + Gy²)`, where `Gx` and `Gy` are the horizontal and vertical gradients. If you compute magnitude from the clipped `uint8` display images, every negative gradient has already been zeroed out. An edge that shows up as -180 in the x-gradient and +50 in the y-gradient has a true magnitude of 187 — well above the detection threshold of 100. But if you clipped first, the -180 became 0, and the magnitude drops to 50. The edge vanishes. The function has to return both the clipped display images *and* the raw float arrays, and magnitude has to come from the floats.

Once the pipeline was correct, the thresholded output showed 23,693 edge pixels out of 269,735 total — clean outlines of the Rubik's cube against a black background, grid lines between the colored squares, sharp transitions at the beveled edges between faces. When I'd had the magnitude pipeline wrong earlier, those grid lines were patchy and the cube silhouette had gaps where strong horizontal edges had been clipped to nothing.

## The Corner Shape Trap

Problem 3 switches to ArUco marker detection and pose estimation. OpenCV handles the heavy lifting here, but two things bite you on the way in.

First, the API split. OpenCV 4.7 moved marker detection from `cv2.aruco.detectMarkers()` to `cv2.aruco.ArucoDetector().detectMarkers()`. The old function still exists in some builds but throws deprecation warnings or fails outright in others. A `try/except` that attempts the new API first and falls back to the old one covers both cases. The same version split affects `estimatePoseSingleMarkers()`, which in newer builds requires a `solvePnP` fallback with manually defined 3D corner points.

Second, the corner array shape. `detectMarkers()` returns a list of arrays, one per detected marker. Each array has shape `(1, 4, 2)` — one marker, four corners, two coordinates. That leading dimension of 1 serves no obvious purpose, but if you index `corners[i]` expecting `(4, 2)`, you get `(1, 4, 2)` and your coordinate extraction is off by a dimension. The fix is `corners[i][0]` to peel off that outer layer. Marker 5's top-right corner landed at pixel (759, 446). Marker 7's pose matrix put it roughly 609mm from the camera, rotated about 20 degrees off-axis.

## What the Slow Way Teaches

Every one of these traps has a one-line library call that handles it correctly. `np.mean()` doesn't overflow. `cv2.Sobel()` uses signed intermediates internally. `cv2.magnitude()` computes from raw gradients. The ArUco high-level API hides the corner array shape entirely.

But after spending an evening watching Sobel edges vanish when I clipped too early, I understand something about those library calls I didn't before. `cv2.Sobel()` returns `CV_64F` by default for a reason — not because the developers were being cautious with types, but because the entire downstream pipeline depends on preserving sign. The padding choice, the intermediate data type, and the magnitude computation aren't three independent decisions. They're one pipeline where each stage constrains the next.

The assignment knows this. Implementing it manually is the calibration step — not for the code, but for your intuition about what the optimized version does and why it makes the choices it makes. The next time I reach for `cv2.Sobel()` with `ddepth=cv2.CV_64F`, I won't just know it's correct. I'll know what breaks if I don't.