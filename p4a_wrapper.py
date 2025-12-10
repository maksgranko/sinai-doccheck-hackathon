#!/usr/bin/env python3
"""
Wrapper для python-for-android, который патчит загрузку рецептов ДО их использования
"""
import sys
import os

# Добавляем пути к python-for-android
possible_paths = [
    '/app/.buildozer/android/platform/python-for-android',
    '/root/.buildozer/android/platform/python-for-android',
    os.path.join(os.path.expanduser('~'), '.buildozer', 'android', 'platform', 'python-for-android'),
]

p4a_path = None
for path in possible_paths:
    if os.path.exists(path):
        if path not in sys.path:
            sys.path.insert(0, path)
        p4a_path = path
        break

if p4a_path:
    # Патчим модуль recipe.py ДО его импорта
    recipe_module_file = os.path.join(p4a_path, 'pythonforandroid', 'recipe.py')
    
    if os.path.exists(recipe_module_file):
        try:
            with open(recipe_module_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Если патч еще не применен, применяем его
            if '# PATCHED: Auto-fix missing recipe attribute' not in content:
                lines = content.split('\n')
                patched_lines = []
                patched = False
                
                for line in lines:
                    if 'recipe' in line and 'mod.recipe' in line and '=' in line and not patched:
                        indent = len(line) - len(line.lstrip())
                        patch_code = [
                            ' ' * indent + '# PATCHED: Auto-fix missing recipe attribute',
                            ' ' * indent + 'try:',
                            ' ' * indent + '    recipe = mod.recipe',
                            ' ' * indent + 'except AttributeError:',
                            ' ' * indent + '    import inspect',
                            ' ' * indent + '    recipe = None',
                            ' ' * indent + '    for name, obj in inspect.getmembers(mod):',
                            ' ' * indent + '        if (inspect.isclass(obj) and ',
                            ' ' * indent + '            name.endswith("Recipe") and ',
                            ' ' * indent + '            name != "Recipe" and',
                            ' ' * indent + '            hasattr(obj, "name")):',
                            ' ' * indent + '            try:',
                            ' ' * indent + '                recipe = obj()',
                            ' ' * indent + '                mod.recipe = recipe',
                            ' ' * indent + '                break',
                            ' ' * indent + '            except Exception:',
                            ' ' * indent + '                continue',
                            ' ' * indent + '    if recipe is None:',
                            ' ' * indent + '        raise AttributeError(f"module \'{mod.__name__}\' has no attribute \'recipe\' and could not auto-create it")',
                        ]
                        patched_lines.extend(patch_code)
                        patched = True
                        continue
                    patched_lines.append(line)
                
                if patched:
                    patched_content = '\n'.join(patched_lines)
                    with open(recipe_module_file, 'w', encoding='utf-8') as f:
                        f.write(patched_content)
        
        except Exception:
            pass
    
    # Патчим файл рецепта cryptography
    recipe_file = os.path.join(p4a_path, 'pythonforandroid', 'recipes', 'cryptography', '__init__.py')
    
    if os.path.exists(recipe_file):
        try:
            import re
            with open(recipe_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'recipe = ' not in content and 'recipe=' not in content:
                class_match = re.search(r'class\s+(\w+Recipe)\s*\([^)]+\):', content)
                if class_match:
                    class_name = class_match.group(1)
                    recipe_export = f"\n\n# Экспорт экземпляра рецепта\nrecipe = {class_name}()\n"
                    new_content = content.rstrip() + recipe_export
                    with open(recipe_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
        except Exception:
            pass

# Теперь запускаем оригинальный python-for-android
if __name__ == '__main__':
    # Импортируем и запускаем python-for-android
    from pythonforandroid.toolchain import main
    sys.exit(main())

