# You can use this to convert a .ply file to a .splat file programmatically in python
# Alternatively you can drag and drop a .ply file into the viewer at https://antimatter15.com/splat

from plyfile import PlyData
import numpy as np
import argparse
from io import BytesIO


def process_ply_to_splat(ply_file_path):
    plydata = PlyData.read(ply_file_path)
    vert = plydata["vertex"]
    sorted_indices = np.argsort(
        -np.exp(vert["scale_0"] + vert["scale_1"] + vert["scale_2"])
        / 1 / (1 + np.exp(-vert["opacity"]))
    )
    buffer = BytesIO()
    for idx in sorted_indices:
        v = plydata["vertex"][idx]
        position = np.array([v["x"], v["y"], v["z"]], dtype=np.float32)
        scales = np.exp(
            np.array(
                [v["scale_0"], v["scale_1"], v["scale_2"]],
                dtype=np.float32,
            )
        )
        rot = np.array(
            [v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]],
            dtype=np.float32,
        )
        # print(f"position: {position}")
        # print(f"opacity: {v['opacity']}")
        # acti_opacity = 1 / (1 + np.exp(-v["opacity"]))
        SH_C0 = 0.28209479177387814
        color = np.array(
            [
                0.5 + SH_C0 * v["f_dc_0"],
                0.5 + SH_C0 * v["f_dc_1"],
                0.5 + SH_C0 * v["f_dc_2"],
                1 / (1 + np.exp(-v["opacity"])),
            ]
        )
        # print(f"color: {color}")
        # print(f"rot: {rot}")
        # rot_uint8 = ((rot / np.linalg.norm(rot)) * 128 + 128).clip(0, 255).astype(np.uint8)
        # rot_uint16 = ((rot / np.linalg.norm(rot)) * 32768 + 32768).clip(0, 65535).astype(np.uint16)
        # print(f"rot_uint8: {rot_uint8}")
        # print(f"rot_uint16: {rot_uint16}")

        # decoded_rot_uint8 = (rot_uint8.astype(np.float32) - 128) / 128
        # decoded_rot_uint16 = (rot_uint16.astype(np.float32) - 32768) / 32768
        # print(f"decoded_rot_uint8: {decoded_rot_uint8}")
        # print(f"decoded_rot_uint16: {decoded_rot_uint16}")

        buffer.write(position.tobytes())
        buffer.write(scales.tobytes())
        buffer.write((color * 255).clip(0, 255).astype(np.uint8).tobytes())
        buffer.write(
            ((rot / np.linalg.norm(rot)) * 128 + 128)
            .clip(0, 255)
            .astype(np.uint8)
            .tobytes()
        )
        # buffer.write(
        #     ((rot / np.linalg.norm(rot)) * 32768 + 32768)              # 缩放与偏移适配 uint16 范围 [0, 65535]
        #     .clip(0, 65535)                    # 限制在 uint16 范围
        #     .astype(np.uint16)                # 类型改为 uint16
        #     .tobytes()
        # )
        # buffer.write(rot.tobytes())

    return buffer.getvalue()


def save_splat_file(splat_data, output_path):
    with open(output_path, "wb") as f:
        f.write(splat_data)


def main():
    parser = argparse.ArgumentParser(description="Convert PLY files to SPLAT format.")
    parser.add_argument(
        "input_files", nargs="+", help="The input PLY files to process."
    )
    parser.add_argument(
        "--output", "-o", default="output.splat", help="The output SPLAT file."
    )
    args = parser.parse_args()
    for input_file in args.input_files:
        print(f"Processing {input_file}...")
        splat_data = process_ply_to_splat(input_file)
        output_file = (
            args.output if len(args.input_files) == 1 else input_file + ".splat"
        )
        save_splat_file(splat_data, output_file)
        print(f"Saved {output_file}")


if __name__ == "__main__":
    main()
