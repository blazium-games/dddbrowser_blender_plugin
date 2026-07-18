"""
Authoring helpers: spawn, movementBounds, skybox, portals, colliders, scripts.
Custom properties on empties / objects:

  blazium_role = SPAWN | BOUNDS_MIN | BOUNDS_MAX | PORTAL | SKYBOX
  blazium_portal_url, blazium_portal_radius
  blazium_portal_trigger = AUTO | MANUAL | SCRIPT
  blazium_script_path = path to .luau (object)
  blazium_collider = NONE | BOX | SPHERE | CAPSULE | MESH
  blazium_skybox_uri (scene or empty with role SKYBOX)
"""
from __future__ import annotations

import hashlib
import os
import shutil

from . import transform_utils


def _sanitize(name: str) -> str:
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, "_")
    return name.strip(". ")


def get_spawn(objects, scene) -> dict | None:
    for obj in objects:
        if obj.get("blazium_role") == "SPAWN":
            pos, _, _ = transform_utils.get_object_transform(obj)
            return pos
    cam = scene.camera
    if cam:
        pos, _, _ = transform_utils.get_object_transform(cam)
        return pos
    return None


def get_movement_bounds(objects, scene) -> dict | None:
    mn = mx = None
    for obj in objects:
        role = obj.get("blazium_role")
        if role == "BOUNDS_MIN":
            mn, _, _ = transform_utils.get_object_transform(obj)
        elif role == "BOUNDS_MAX":
            mx, _, _ = transform_utils.get_object_transform(obj)
    if mn and mx:
        return {"min": mn, "max": mx}
    if getattr(scene, "blazium_export_bounds", False):
        return {
            "min": {
                "x": scene.blazium_bounds_min_x,
                "y": scene.blazium_bounds_min_y,
                "z": scene.blazium_bounds_min_z,
            },
            "max": {
                "x": scene.blazium_bounds_max_x,
                "y": scene.blazium_bounds_max_y,
                "z": scene.blazium_bounds_max_z,
            },
        }
    return None


def get_skybox(objects, scene, base_url: str, export_dir: str) -> dict | None:
    uri = getattr(scene, "blazium_skybox_uri", "") or ""
    for obj in objects:
        if obj.get("blazium_role") == "SKYBOX":
            uri = obj.get("blazium_skybox_uri") or uri
            faces = {}
            for face in ("px", "nx", "py", "ny", "pz", "nz"):
                key = f"blazium_skybox_{face}"
                if obj.get(key):
                    faces[face] = obj.get(key)
            if len(faces) == 6:
                return {"faces": faces}
            break
    if uri:
        return {"uri": uri}
    return None


def export_portals(objects) -> list:
    instances = []
    for obj in objects:
        if obj.get("blazium_role") != "PORTAL":
            continue
        url = obj.get("blazium_portal_url") or ""
        if not url:
            continue
        pos, rot, scale = transform_utils.get_object_transform(obj)
        trigger = (obj.get("blazium_portal_trigger") or "MANUAL").upper()
        portal = {
            "destinationUrl": url,
            "radius": float(obj.get("blazium_portal_radius") or 1.0),
            "autoTrigger": trigger == "AUTO",
            "manualTrigger": trigger == "MANUAL",
            "scriptTrigger": trigger == "SCRIPT",
        }
        instances.append(
            {
                "id": _sanitize(obj.name),
                "type": "portal",
                "position": pos,
                "rotation": rot,
                "scale": scale if all(v > 0 for v in scale.values()) else {"x": 1.0, "y": 1.0, "z": 1.0},
                "portal": portal,
            }
        )
    return instances


def collider_for_object(obj) -> dict | None:
    kind = (obj.get("blazium_collider") or "NONE").upper()
    if kind == "NONE":
        return None
    if kind == "BOX":
        dims = obj.dimensions
        return {
            "type": "box",
            "box": {"size": {"x": max(0.01, float(dims.x)), "y": max(0.01, float(dims.y)), "z": max(0.01, float(dims.z))}},
        }
    if kind == "SPHERE":
        r = max(obj.dimensions) * 0.5
        return {"type": "sphere", "sphere": {"radius": max(0.01, float(r))}}
    if kind == "CAPSULE":
        r = max(float(obj.dimensions.x), float(obj.dimensions.z)) * 0.5
        hh = max(0.01, float(obj.dimensions.y) * 0.5)
        return {"type": "capsule", "capsule": {"halfHeight": hh, "radius": max(0.01, r)}}
    if kind == "MESH":
        return {"type": "mesh"}
    return None


def export_scripts(objects, export_dir: str, base_url: str, enabled: bool):
    """Copy .luau files referenced on objects; return (assets, instance_script_map)."""
    if not enabled:
        return [], {}
    scripts_dir = os.path.join(export_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    assets = []
    instance_scripts = {}
    seen = {}

    for obj in objects:
        src = obj.get("blazium_script_path") or ""
        if not src or not os.path.isfile(src):
            continue
        name = _sanitize(os.path.splitext(os.path.basename(src))[0])
        asset_id = f"script-{name}"
        if asset_id not in seen:
            dest = os.path.join(scripts_dir, f"{name}.luau")
            shutil.copy2(src, dest)
            digest = hashlib.sha256(open(dest, "rb").read()).hexdigest()
            rel = os.path.relpath(dest, export_dir).replace("\\", "/")
            uri = f"{base_url.rstrip('/')}/{rel}" if base_url else rel
            assets.append(
                {
                    "id": asset_id,
                    "type": "script",
                    "uri": uri,
                    "mediaType": "application/x-luau",
                    "sha256": digest,
                }
            )
            seen[asset_id] = True
        instance_scripts[_sanitize(obj.name)] = {"file": asset_id}
    return assets, instance_scripts
