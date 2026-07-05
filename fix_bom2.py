import os
files = ['docker-compose.yml', 'deploy/docker-compose.prod.yml']
for f in files:
    data = open(f, 'rb').read()
    clean = data.lstrip(b'\xef\xbb\xbf')
    if clean != data:
        open(f, 'wb').write(clean)
        print('Fixed:', f)
    else:
        print('Clean:', f)
print('Done')
