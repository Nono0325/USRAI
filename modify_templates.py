import os
import re

template_dir = 'templates'

img_pattern = re.compile(r'(<img\s+(.*?)src="\{\{\s*([\w\.]+)\.url\s*\}\}"(.*?)/?>)')

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            # Map replacement in contact.html
            if file == 'contact.html' and 'map_iframe' not in content:
                map_html = """        </div>
        <!-- Google Map Section -->
        {% if contact_info.map_iframe %}
        <div class="row mt-5">
            <div class="col-12">
                <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
                    <div class="map-container" style="min-height: 400px;">
                        <style>.map-container iframe { width: 100% !important; height: 400px !important; border: 0 !important; }</style>
                        {{ contact_info.map_iframe|safe }}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>"""
                new_content = new_content.replace('        </div>\n    </div>', map_html)

            # Video replacement
            if re.search(img_pattern, content):
                def replace_img(match):
                    full_img = match.group(1)
                    before_src = match.group(2)
                    var_name = match.group(3)
                    after_src = match.group(4)
                    
                    video_tag = f'<video src="{{{{ {var_name}.url }}}}" autoplay loop muted playsinline {before_src}{after_src}></video>'
                    
                    return f'{{% if {var_name}|is_video %}}{video_tag}{{% else %}}{full_img}{{% endif %}}'

                new_content = re.sub(img_pattern, replace_img, new_content)

                # Inject {% load custom_filters %} after {% extends ... %}
                if '{% load custom_filters %}' not in new_content:
                    if '{% extends' in new_content:
                        new_content = re.sub(r'({% extends [^%]+%})', r'\1\n{% load custom_filters %}', new_content, count=1)
                    else:
                        new_content = '{% load custom_filters %}\n' + new_content

            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {path}")
