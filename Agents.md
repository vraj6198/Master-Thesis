# TASK: Generate a Complete Blender Add-on (LLM-Controlled LiDAR Scanner)

You are a **senior Blender add-on developer** and **Python engineer**.

Your task is to generate a **complete, installable Blender add-on** that enables **LLM-based control of an existing LiDAR scanner add-on (BLAINDER Range Scanner)**.

⚠️ IMPORTANT:
- **DO NOT reimplement LiDAR physics**
- **DO NOT modify BLAINDER code**
- This add-on is a **controller + orchestrator only**

The output must be **production-quality**, **thesis-ready**, and **fully runnable**.

---

## 1. HIGH-LEVEL FUNCTIONALITY

The add-on must implement the following workflow:

1. A Blender scene already exists
2. The **BLAINDER Range Scanner add-on is installed and enabled**
3. A scanner object exists in the scene
4. Scanner parameters are stored in a **base config file** (JSON preferred)
5. A **Large Language Model (LLM)** generates a **parameter PATCH** from a natural-language user command
6. The add-on **validates and clamps** the patch
7. The patch is applied to the existing scanner add-on
8. The add-on **triggers the BLAINDER scan operator**
9. Blender exports a point cloud
10. The add-on **analyzes the point cloud**
11. Results are saved as JSON next to the scan output

---

## 2. STRICT SCOPE RULES

### Allowed
- Controlling scanner pose, resolution, FOV, range, noise
- Triggering scan execution
- Reading exported point clouds
- Computing basic statistics
- Using LLMs for parameter control

### Forbidden
- Implementing ray casting or LiDAR simulation
- Replacing or copying BLAINDER code
- Hardcoding BLAINDER operator names without fallback
- Writing files outside user-selected output directory

---

## 3. TARGET BLENDER VERSION

- Blender **4.5 LTS**
- Compatible with Blender **4.x** if possible
- Python only (no compiled extensions)

---

## 4. ADD-ON STRUCTURE (MANDATORY)

Generate the following add-on structure:

