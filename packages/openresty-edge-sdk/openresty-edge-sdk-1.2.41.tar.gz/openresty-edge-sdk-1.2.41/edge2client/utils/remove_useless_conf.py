import os
import sys
import re

if sys.argv[1]:
    apps_dir = sys.argv[1]

p = re.compile(r'.*\{\{.+?\}\}.*')

if os.path.isdir(apps_dir):
    for root, dirs, files in os.walk(apps_dir):
        for name in files:
            if name.endswith('.com.conf'):
                app_file = os.path.join(root, name)
                print 'include vhost/' + name + ';'
                content = None
                with open(app_file) as f:
                    content = f.read()
                    content = p.sub('', content)
                    content = content.replace('location =/', 'location = /')
                with open(app_file, 'w') as f:
                    f.write(content)
