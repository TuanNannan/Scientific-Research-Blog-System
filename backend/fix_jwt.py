import os

files_to_update = [
    'app/api/experiments.py',
    'app/api/todos.py',
    'app/api/audio_files.py',
    'app/api/metrics.py',
    'app/api/posts.py'
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('user_id = get_jwt_identity()', 'user_id = int(get_jwt_identity())')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {file_path}')

print('Done!')
