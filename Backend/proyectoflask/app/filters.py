import os
from PIL import Image
import numpy as np
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

def apply_sepia(input_image, intensity=2.0, add_noise=True, vignette=True):
    input_array = np.array(input_image).astype(np.float32) / 255.0
    output_array = np.zeros_like(input_array)

    cuda.init()
    device = cuda.Device(0)
    context = device.make_context()

    try:
        mod = SourceModule("""
        __global__ void sepia_kernel(float *d_image, float *d_result, int width, int height, float intensity) {
            int x = threadIdx.x + blockIdx.x * blockDim.x;
            int y = threadIdx.y + blockIdx.y * blockDim.y;
            int idx = (y * width + x) * 3;
            if (x < width && y < height) {
                float r = d_image[idx];
                float g = d_image[idx + 1];
                float b = d_image[idx + 2];
                float new_r = min(intensity * (0.393f * r + 0.769f * g + 0.189f * b), 1.0f);
                float new_g = min(intensity * (0.349f * r + 0.686f * g + 0.168f * b), 1.0f);
                float new_b = min(intensity * (0.272f * r + 0.534f * g + 0.131f * b), 1.0f);
                d_result[idx] = new_r;
                d_result[idx + 1] = new_g;
                d_result[idx + 2] = new_b;
            }
        }
        """)
        sepia_kernel = mod.get_function("sepia_kernel")
        sepia_kernel(
            cuda.In(input_array), cuda.Out(output_array),
            np.int32(input_image.width), np.int32(input_image.height), np.float32(intensity),
            block=(16, 16, 1), grid=(int((input_image.width + 15) // 16), int((input_image.height + 15) // 16))
        )

        if add_noise:
            noise = np.random.normal(loc=0.0, scale=0.05, size=output_array.shape).astype(np.float32)
            output_array += noise

        if vignette:
            center_x, center_y = input_image.width / 2, input_image.height / 2
            max_radius = np.sqrt(center_x**2 + center_y**2)
            for y in range(input_image.height):
                for x in range(input_image.width):
                    radius = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    scale = radius / max_radius
                    output_array[y, x] *= (1 - scale * 0.5)

        output_image = Image.fromarray(np.uint8(output_array * 255))
        return output_image
    finally:
        context.pop()

def apply_anamorphic(input_image):
    input_array = np.array(input_image).astype(np.float32) / 255.0
    output_array = np.zeros_like(input_array)

    cuda.init()
    device = cuda.Device(0)
    context = device.make_context()

    try:
        mod = SourceModule("""
        __global__ void anamorphic_kernel(float *d_image, float *d_result, int width, int height) {
            int x = threadIdx.x + blockIdx.x * blockDim.x;
            int y = threadIdx.y + blockIdx.y * blockDim.y;
            int idx = (y * width + x) * 3;
            float brightness = 0.299f * d_image[idx] + 0.587f * d_image[idx + 1] + 0.114f * d_image[idx + 2];
            if (brightness > 0.55) {  // Only apply effect to bright areas
                float effect_strength = 1.5;
                int spread = 25;  // Spread effect to 25 pixels on either side
                for (int i = -spread; i <= spread; i++) {
                    int new_x = x + i;
                    if (new_x >= 0 && new_x < width) {
                        int new_idx = (y * width + new_x) * 3;
                        atomicAdd(&d_result[new_idx], d_image[idx] * effect_strength / (spread * 2));
                        atomicAdd(&d_result[new_idx + 1], d_image[idx + 1] * effect_strength / (spread * 2));
                        atomicAdd(&d_result[new_idx + 2], d_image[idx + 2] * effect_strength / (spread * 2));
                    }
                }
            } else {
                d_result[idx] = d_image[idx];
                d_result[idx + 1] = d_image[idx + 1];
                d_result[idx + 2] = d_image[idx + 2];
            }
        }
        """)
        anamorphic_kernel = mod.get_function("anamorphic_kernel")
        anamorphic_kernel(
            cuda.In(input_array), cuda.Out(output_array),
            np.int32(input_image.width), np.int32(input_image.height),
            block=(16, 16, 1), grid=(int((input_image.width + 15) // 16), int((input_image.height + 15) // 16))
        )
        output_image = Image.fromarray(np.uint8(output_array * 255))
        return output_image
    finally:
        context.pop()

import pycuda.autoinit
import pycuda.driver as cuda
import numpy as np
from pycuda.compiler import SourceModule
from PIL import Image
import os

def apply_logo(input_image):
    input_array = np.array(input_image).astype(np.float32) / 255.0
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'logoups.jpeg')
    logo_image = Image.open(logo_path).convert('RGBA').resize((150, 150))
    logo_array = np.array(logo_image).astype(np.float32) / 255.0

    output_array = np.zeros_like(input_array)

    cuda.init()
    device = cuda.Device(0)
    context = device.make_context()

    try:
        mod = SourceModule("""
        __global__ void logo_kernel(float *d_image, float *d_logo, float *d_result, int img_width, int img_height, int logo_width, int logo_height) {
            int x = threadIdx.x + blockIdx.x * blockDim.x;
            int y = threadIdx.y + blockIdx.y * blockDim.y;

            if (x < img_width && y < img_height) {
                int idx = (y * img_width + x) * 3;
                d_result[idx] = d_image[idx];  // Copy RGB directly
                d_result[idx + 1] = d_image[idx + 1];
                d_result[idx + 2] = d_image[idx + 2];

                // Coordinates to center the logo
                int cx = (img_width - logo_width) / 2;
                int cy = (img_height - logo_height) / 2;

                if (x >= cx && x < (cx + logo_width) && y >= cy && y < (cy + logo_height)) {
                    int logo_idx = ((y - cy) * logo_width + (x - cx)) * 4;  // Logo has alpha channel
                    float alpha = d_logo[logo_idx + 3];
                    // Blend with alpha
                    d_result[idx] = alpha * d_logo[logo_idx] + (1 - alpha) * d_result[idx];
                    d_result[idx + 1] = alpha * d_logo[logo_idx + 1] + (1 - alpha) * d_result[idx + 1];
                    d_result[idx + 2] = alpha * d_logo[logo_idx + 2] + (1 - alpha) * d_result[idx + 2];
                }
            }
        }
        """)
        logo_kernel = mod.get_function("logo_kernel")
        logo_kernel(
            cuda.In(input_array), cuda.In(logo_array), cuda.Out(output_array),
            np.int32(input_image.width), np.int32(input_image.height),
            np.int32(logo_image.width), np.int32(logo_image.height),
            block=(16, 16, 1), grid=(int((input_image.width + 15) // 16), int((input_image.height + 15) // 16))
        )
        output_image = Image.fromarray(np.uint8(output_array * 255))
        return output_image
    finally:
        context.pop()


def apply_filter(image, filter_type):
    if filter_type == 'sepia':
        return apply_sepia(image)
    elif filter_type == 'anamorphic':
        return apply_anamorphic(image)
    elif filter_type == 'logo':
        return apply_logo(image)
    else:
        raise ValueError("Unknown filter type")
