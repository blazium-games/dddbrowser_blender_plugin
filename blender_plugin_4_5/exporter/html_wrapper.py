"""
HTML wrapper generation for embedding scene JSON.
"""
import os
import json

def generate_html_wrapper(scene_json, export_settings, output_path):
    """Generate HTML wrapper with embedded scene JSON.
    
    Args:
        scene_json: dict - Scene JSON dict
        export_settings: dict - Export settings including metadata
        output_path: str - Path to output HTML file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract metadata
        scene_name = scene_json.get('name', 'Exported Scene')
        scene_id = scene_json.get('id', scene_name.lower().replace(' ', '_'))
        scene_author = scene_json.get('author', export_settings.get('scene_author', ''))
        scene_rating = scene_json.get('rating', export_settings.get('scene_rating', 'GENERAL'))
        scene_description = scene_json.get('description', export_settings.get('scene_description', ''))
        thumbnail_url = scene_json.get('thumbnail', export_settings.get('thumbnail_url', ''))
        
        # Convert JSON to string for embedding in HTML
        # JSON in script tags doesn't need HTML escaping - the browser will parse it correctly
        scene_json_str = json.dumps(scene_json, indent=2, ensure_ascii=False)
        
        # Generate HTML using list join (more efficient than string concatenation)
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "    <meta charset=\"utf-8\">",
            f"    <title>{scene_name}</title>",
            "",
            f"    <meta name=\"scene:id\" content=\"{scene_id}\">",
            f"    <meta name=\"scene:name\" content=\"{scene_name}\">",
            f"    <meta name=\"scene:author\" content=\"{scene_author}\">",
            f"    <meta name=\"scene:rating\" content=\"{scene_rating}\">",
        ]
        
        if thumbnail_url:
            html_parts.append(f"    <meta name=\"scene:thumbnail\" content=\"{thumbnail_url}\">")
        
        html_parts.extend([
            "",
            "    <script id=\"blazium-scene\" type=\"application/vnd.blazium.scene+json\">",
            f"    {scene_json_str}",
            "    </script>",
            "</head>",
            "<body>",
            f"    <h1>{scene_name}</h1>",
        ])
        
        if scene_description:
            html_parts.append(f"    <p>{scene_description}</p>")
        
        html_parts.extend([
            "</body>",
            "</html>",
        ])
        
        html_content = "\n".join(html_parts)
        
        # Write HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True
    except Exception:
        return False

