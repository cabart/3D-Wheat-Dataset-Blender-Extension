import os

print("Updating Blender manifest with wheels...", end="")
manifest_path = "blender_manifest.toml"

# Wheels list
directory = "wheels"
wheels = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

output = []
in_wheels_section = False
with open(manifest_path, "r") as f:
    lines = f.readlines()

    for line in lines:
        if not in_wheels_section:
            if line.startswith("wheels = ["):
                in_wheels_section = True
            else:
                output.append(line)
        else:
            if line.startswith("]"):
                in_wheels_section = False
                output.append("wheels = [\n")
                for wheel in wheels:
                    output.append(f'    "./wheels/{wheel}",\n')
                output[-1] = output[-1].rstrip(",\n") + "\n"
                output.append("]\n")

with open(manifest_path, "w") as f:
    f.writelines(output)

print(" Done.")