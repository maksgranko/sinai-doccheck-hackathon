"""
Кастомный рецепт для numpy с исправлением проблемы distutils.msvccompiler
"""
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import info, warning, shprint
import sh
import os
import glob
import shutil


class NumpyRecipe(CompiledComponentsPythonRecipe):
    """
    Рецепт для numpy с исправлением проблемы distutils.msvccompiler
    Используем версию 1.21.6, которая совместима с Python 3.11
    """
    name = 'numpy'
    version = '1.21.6'  # Версия, совместимая с Python 3.11 и не требующая distutils.msvccompiler
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.zip'
    
    depends = ['setuptools']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    
    def build_compiled_components(self, arch):
        """Переопределяем для обработки проблемы с setup.py clean"""
        # numpy 1.21.6 не поддерживает setup.py clean --all
        # Вместо этого очищаем build директорию вручную
        build_dir = self.get_build_dir(arch.arch)
        build_subdir = os.path.join(build_dir, 'build')
        if os.path.exists(build_subdir):
            try:
                shutil.rmtree(build_subdir)
                info("[NumpyRecipe] Очистка build директории выполнена вручную")
            except Exception as e:
                warning(f"[NumpyRecipe] Не удалось очистить build: {e}")
        
        # Вызываем стандартную сборку без команды clean
        # Используем метод родительского класса, но пропускаем clean
        hostpython = self.ctx.hostpython
        build_cmd = self.build_cmd
        
        # Выполняем сборку напрямую без clean
        info("[NumpyRecipe] Начало сборки numpy без команды clean")
        shprint(hostpython, 'setup.py', build_cmd, '-v',
                _env=self.get_recipe_env(arch),
                _tail=20, _critical=True)
        
        return True
    
    def prebuild_arch(self, arch):
        """Исправление проблемы с distutils.msvccompiler перед сборкой"""
        super().prebuild_arch(arch)
        
        build_dir = self.get_build_dir(arch.arch)
        
        # Исправляем файл mingw32ccompiler.py, который вызывает проблему
        mingw_file = os.path.join(build_dir, 'numpy', 'distutils', 'mingw32ccompiler.py')
        
        if os.path.exists(mingw_file):
            try:
                info("[NumpyRecipe] Исправление проблемы с distutils.msvccompiler в mingw32ccompiler.py")
                
                # Читаем файл
                with open(mingw_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Заменяем проблемный импорт
                old_import = 'from distutils.msvccompiler import get_build_version as get_build_msvc_version'
                new_code = '''try:
    from distutils.msvccompiler import get_build_version as get_build_msvc_version
except ImportError:
    def get_build_msvc_version():
        return None'''
                
                if old_import in content:
                    content = content.replace(old_import, new_code)
                    
                    # Сохраняем исправленный файл
                    with open(mingw_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    info("[NumpyRecipe] mingw32ccompiler.py исправлен")
            except Exception as e:
                warning(f"[NumpyRecipe] Не удалось исправить mingw32ccompiler.py: {e}")


# КРИТИЧНО: Экспорт экземпляра рецепта
recipe = NumpyRecipe()

