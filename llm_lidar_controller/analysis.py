import csv
import os
import time

from . import utils


class RunningStats:
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.min = None
        self.max = None

    def update(self, value):
        if self.min is None or value < self.min:
            self.min = value
        if self.max is None or value > self.max:
            self.max = value
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.m2 += delta * delta2

    def finalize(self):
        if self.count < 2:
            variance = 0.0
        else:
            variance = self.m2 / (self.count - 1)
        return {
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "stdev": variance ** 0.5,
        }


def analyze_csv(path):
    stats = {
        "x": RunningStats(),
        "y": RunningStats(),
        "z": RunningStats(),
        "distance": RunningStats(),
        "intensity": RunningStats(),
    }

    count = 0
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 10:
                continue
            try:
                x = float(row[2])
                y = float(row[3])
                z = float(row[4])
                distance = float(row[5])
                intensity = float(row[6])
            except (ValueError, IndexError):
                continue

            stats["x"].update(x)
            stats["y"].update(y)
            stats["z"].update(z)
            stats["distance"].update(distance)
            stats["intensity"].update(intensity)
            count += 1

    return build_summary(path, count, stats, "csv")


def analyze_ply_ascii(path):
    stats = {
        "x": RunningStats(),
        "y": RunningStats(),
        "z": RunningStats(),
    }
    vertex_count = 0
    header_done = False
    format_ascii = False
    vertex_total = 0
    property_order = []

    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not header_done:
                if line.startswith("format "):
                    format_ascii = "ascii" in line
                elif line.startswith("element vertex"):
                    parts = line.split()
                    if len(parts) == 3:
                        vertex_total = int(parts[2])
                elif line.startswith("property "):
                    parts = line.split()
                    if len(parts) == 3:
                        property_order.append(parts[2])
                elif line == "end_header":
                    header_done = True
                continue

            if not format_ascii:
                break
            if not line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                values = [float(parts[i]) for i in range(3)]
            except ValueError:
                continue
            stats["x"].update(values[0])
            stats["y"].update(values[1])
            stats["z"].update(values[2])
            vertex_count += 1
            if vertex_total and vertex_count >= vertex_total:
                break

    if not format_ascii:
        raise ValueError("PLY file is binary; enable CSV export for analysis.")

    return build_summary(path, vertex_count, stats, "ply_ascii")


def build_summary(path, count, stats, fmt):
    summary = {
        "file": path,
        "format": fmt,
        "points": count,
        "timestamp": time.time(),
        "bounds": {
            "min": [stats["x"].min, stats["y"].min, stats["z"].min],
            "max": [stats["x"].max, stats["y"].max, stats["z"].max],
        },
        "centroid": [stats["x"].mean, stats["y"].mean, stats["z"].mean],
    }

    if "distance" in stats:
        summary["distance"] = stats["distance"].finalize()
    if "intensity" in stats:
        summary["intensity"] = stats["intensity"].finalize()

    summary["xyz"] = {
        "x": stats["x"].finalize(),
        "y": stats["y"].finalize(),
        "z": stats["z"].finalize(),
    }
    return summary


def analyze_point_cloud(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return analyze_csv(path)
    if ext == ".ply":
        return analyze_ply_ascii(path)
    raise ValueError(f"Unsupported point cloud format '{ext}'.")


def find_latest_export(output_dir, base_name, extensions):
    candidates = []
    for filename in os.listdir(output_dir):
        if not filename.startswith(base_name):
            continue
        for ext in extensions:
            if filename.endswith(ext):
                path = os.path.join(output_dir, filename)
                try:
                    mtime = os.path.getmtime(path)
                except OSError:
                    continue
                candidates.append((mtime, path))
                break

    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def resolve_expected_basename(props):
    cleaned = utils.remove_invalid_filename_chars(props.dataFileName or "scan")
    if props.enableAnimation and not props.exportSingleFrames:
        return f"{cleaned}_frames_{props.frameStart}_to_{props.frameEnd}"
    return cleaned
