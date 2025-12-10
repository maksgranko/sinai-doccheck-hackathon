"""
Кастомный рецепт для cryptography с поддержкой setuptools_rust
Полностью переопределяет стандартный рецепт для установки setuptools_rust в hostpython3
"""
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import shprint, info, warning
import sh
import os


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    """
    Рецепт для cryptography с установкой setuptools_rust в hostpython3
    """
    name = 'cryptography'
    version = '41.0.7'  # Используем версию, совместимую с setuptools 51.3.3
    url = 'https://pypi.python.org/packages/source/c/cryptography/cryptography-{version}.tar.gz'
    
    depends = ['setuptools', 'cffi']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    
    def build_compiled_components(self, arch):
        """Переопределяем для установки setuptools_rust перед сборкой"""
        # КРИТИЧНО: Устанавливаем OPENSSL_VENDORED СРАЗУ в os.environ
        # Это должно быть установлено ДО того, как openssl-sys build script запустится
        os.environ['OPENSSL_VENDORED'] = '1'
        info("[CryptographyRecipe] Set OPENSSL_VENDORED=1 in os.environ (VERY EARLY)")
        
        # КРИТИЧНО: Сохраняем оригинальный CC и переопределяем на системный компилятор
        # Rust build script компилирует для хост-платформы (x86_64-unknown-linux-gnu), 
        # а не для Android, поэтому нужен системный компилятор, а не Android NDK
        original_cc_global = os.environ.get('CC', '')
        if original_cc_global:
            os.environ['_ORIGINAL_CC_GLOBAL'] = original_cc_global
        
        # КРИТИЧНО: Устанавливаем системный компилятор в os.environ ДО всего остального
        # Это гарантирует, что Rust build script получит правильный компилятор
        os.environ['CC'] = '/usr/bin/cc'
        os.environ['CC_x86_64-unknown-linux-gnu'] = '/usr/bin/cc'
        os.environ['HOST_CC'] = '/usr/bin/cc'
        os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC'] = '/usr/bin/cc'
        
        # Очищаем CFLAGS от Android-специфичных флагов
        original_cflags_global = os.environ.get('CFLAGS', '')
        if original_cflags_global:
            os.environ['_ORIGINAL_CFLAGS_GLOBAL'] = original_cflags_global
        os.environ['CFLAGS'] = ''
        os.environ['CFLAGS_x86_64-unknown-linux-gnu'] = ''
        os.environ['HOST_CFLAGS'] = ''
        os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS'] = ''
        
        # Отключаем ccache для Rust build script (но не глобально)
        os.environ['CCACHE_DISABLE'] = '1'
        
        info(f"[CryptographyRecipe] Overrode CC to /usr/bin/cc (was: {original_cc_global})")
        info("[CryptographyRecipe] Set CC_x86_64-unknown-linux-gnu = /usr/bin/cc")
        info("[CryptographyRecipe] Set HOST_CC = /usr/bin/cc")
        info("[CryptographyRecipe] Set CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC = /usr/bin/cc")
        info("[CryptographyRecipe] Disabled ccache for Rust build script (CCACHE_DISABLE=1)")
        
        # Получаем hostpython
        try:
            if hasattr(self.ctx, 'hostpython') and self.ctx.hostpython:
                hostpython = self.ctx.hostpython
            elif hasattr(self.ctx, 'python_recipe') and hasattr(self.ctx.python_recipe, 'hostpython_location'):
                hostpython = self.ctx.python_recipe.hostpython_location
            else:
                hostpython = sh.which('python3')
                warning("[CryptographyRecipe] Using system python3 as fallback")
            
            info(f"[CryptographyRecipe] Installing setuptools_rust in: {hostpython}")
        except Exception as e:
            warning(f"[CryptographyRecipe] Error getting hostpython: {e}")
            hostpython = sh.which('python3')
        
        # Настраиваем окружение для Rust
        env = os.environ.copy()
        cargo_path = "/root/.cargo/bin"
        if 'PATH' in env:
            if cargo_path not in env['PATH']:
                env['PATH'] = f"{cargo_path}:{env['PATH']}"
        else:
            env['PATH'] = f"{cargo_path}:/usr/local/bin:/usr/bin:/bin"
        
        env['CARGO_HOME'] = '/root/.cargo'
        env['RUSTUP_HOME'] = '/root/.rustup'
        
        # КРИТИЧНО: Устанавливаем OPENSSL_VENDORED в env (os.environ уже установлен выше)
        # Это должно быть установлено ДО того, как openssl-sys build script запустится
        env['OPENSSL_VENDORED'] = '1'
        info("[CryptographyRecipe] Set OPENSSL_VENDORED=1 in env (for Rust build script)")
        
        # CCACHE_DISABLE уже установлен в os.environ выше
        env['CCACHE_DISABLE'] = '1'
        info("[CryptographyRecipe] CCACHE_DISABLE=1 already set in os.environ, also set in env")
        
        # КРИТИЧНО: Настраиваем OpenSSL для Rust (cryptography требует OpenSSL для компиляции)
        # Ищем собранный OpenSSL в python-for-android
        openssl_build_dir = None
        try:
            # Путь к собранному OpenSSL обычно в build/other_builds/openssl/<arch>__ndk_target_<api>/openssl1.1
            storage_dir = self.ctx.storage_dir if hasattr(self.ctx, 'storage_dir') else None
            if not storage_dir:
                # Fallback: используем путь из build_dir
                build_dir = self.get_build_dir(arch.arch)
                storage_dir = os.path.dirname(os.path.dirname(build_dir))
            
            if storage_dir:
                openssl_patterns = [
                    os.path.join(storage_dir, 'build', 'other_builds', 'openssl', f'{arch.arch}__ndk_target_21', 'openssl1.1'),
                    os.path.join(storage_dir, 'build', 'other_builds', 'openssl', f'{arch.arch}__ndk_target_21', 'openssl'),
                ]
                for pattern in openssl_patterns:
                    if os.path.exists(pattern):
                        openssl_build_dir = pattern
                        break
            
            if openssl_build_dir:
                # Устанавливаем переменные окружения для Rust
                openssl_include = os.path.join(openssl_build_dir, 'include')
                openssl_lib = os.path.join(openssl_build_dir, '.libs') if os.path.exists(os.path.join(openssl_build_dir, '.libs')) else openssl_build_dir
                
                if os.path.exists(openssl_include):
                    env['OPENSSL_DIR'] = openssl_build_dir
                    env['OPENSSL_INCLUDE_DIR'] = openssl_include
                    env['OPENSSL_LIB_DIR'] = openssl_lib
                    info(f"[CryptographyRecipe] Set OPENSSL_DIR to: {openssl_build_dir}")
                    info(f"[CryptographyRecipe] Set OPENSSL_INCLUDE_DIR to: {openssl_include}")
                    info(f"[CryptographyRecipe] Set OPENSSL_LIB_DIR to: {openssl_lib}")
                else:
                    warning(f"[CryptographyRecipe] OpenSSL include directory not found: {openssl_include}")
                    # Пробуем использовать системный OpenSSL как fallback
                    if os.path.exists('/usr/include/openssl'):
                        env['OPENSSL_DIR'] = '/usr'
                        env['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                        env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                        warning("[CryptographyRecipe] Using system OpenSSL as fallback (may cause issues)")
            else:
                warning("[CryptographyRecipe] Could not find OpenSSL build directory, using system OpenSSL")
                # Используем системный OpenSSL как fallback
                if os.path.exists('/usr/include/openssl'):
                    env['OPENSSL_DIR'] = '/usr'
                    env['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                    env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
        except Exception as e:
            warning(f"[CryptographyRecipe] Failed to configure OpenSSL for Rust: {e}")
            # Используем системный OpenSSL как fallback
            if os.path.exists('/usr/include/openssl'):
                env['OPENSSL_DIR'] = '/usr'
                env['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
        
        # КРИТИЧНО: Rust компилирует для хост-платформы (x86_64-unknown-linux-gnu), а не для Android
        # Поэтому нужно использовать системный OpenSSL и системный компилятор для Rust
        # Сохраняем оригинальные CC и CFLAGS
        original_cc = env.get('CC')
        original_cflags = env.get('CFLAGS')
        
        # Для Rust-компиляции используем системный OpenSSL (не Android OpenSSL)
        # Убеждаемся, что OPENSSL_DIR указывает на системный OpenSSL
        if not env.get('OPENSSL_DIR') or 'android' in str(env.get('OPENSSL_DIR', '')):
            # Используем системный OpenSSL для Rust
            if os.path.exists('/usr/include/openssl'):
                env['OPENSSL_DIR'] = '/usr'
                env['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                info("[CryptographyRecipe] Using system OpenSSL for Rust host compilation")
        
        # Для Rust-компиляции нужно использовать системный компилятор, а не Android NDK
        # Устанавливаем переменные для Rust, чтобы он использовал системный компилятор
        if original_cc and ('android-ndk' in original_cc or 'clang' in original_cc):
            # Сохраняем оригинальные значения для восстановления после Rust-компиляции
            env['_ORIGINAL_CC'] = original_cc
            env['_ORIGINAL_CFLAGS'] = original_cflags or ''
            
            # КРИТИЧНО: Устанавливаем переменные в os.environ ДО вызова super().build_compiled_components(arch)
            # Rust запускается через setuptools_rust, который использует os.environ
            if 'CC' in os.environ:
                os.environ['_ORIGINAL_CC'] = os.environ['CC']
            if 'CFLAGS' in os.environ:
                os.environ['_ORIGINAL_CFLAGS'] = os.environ['CFLAGS']
            
            # КРИТИЧНО: Временно переопределяем глобальный CC для Rust build script
            # openssl-sys build script использует cc crate, который читает CC напрямую
            os.environ['_ORIGINAL_CC_GLOBAL'] = os.environ.get('CC', '')
            os.environ['CC'] = '/usr/bin/cc'
            os.environ['CFLAGS'] = ''
            
            # Устанавливаем переменные для Rust в os.environ
            os.environ['CC_x86_64-unknown-linux-gnu'] = '/usr/bin/cc'
            os.environ['CFLAGS_x86_64-unknown-linux-gnu'] = ''
            os.environ['HOST_CC'] = '/usr/bin/cc'
            os.environ['HOST_CFLAGS'] = ''
            os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC'] = '/usr/bin/cc'
            os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS'] = ''
            
            # Также устанавливаем в локальный env
            env['CC'] = '/usr/bin/cc'
            env['CFLAGS'] = ''
            
            # Также устанавливаем в локальный env для совместимости
            env['CC_x86_64-unknown-linux-gnu'] = '/usr/bin/cc'
            env['CFLAGS_x86_64-unknown-linux-gnu'] = ''
            env['HOST_CC'] = '/usr/bin/cc'
            env['HOST_CFLAGS'] = ''
            env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC'] = '/usr/bin/cc'
            env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS'] = ''
            
            info("[CryptographyRecipe] Set system compiler for Rust host compilation (x86_64-unknown-linux-gnu)")
            info("[CryptographyRecipe] CC_x86_64-unknown-linux-gnu = /usr/bin/cc (in os.environ and env)")
            info("[CryptographyRecipe] CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC = /usr/bin/cc")
            info("[CryptographyRecipe] HOST_CC = /usr/bin/cc")
            
            # КРИТИЧНО: Устанавливаем OPENSSL_DIR для Rust в os.environ
            # Ищем opensslconf.h в различных местах
            opensslconf_paths = [
                '/usr/include/openssl/opensslconf.h',
                '/usr/include/x86_64-linux-gnu/openssl/opensslconf.h',
                '/usr/lib/x86_64-linux-gnu/openssl/opensslconf.h',
            ]
            opensslconf_found = None
            for path in opensslconf_paths:
                if os.path.exists(path):
                    opensslconf_found = path
                    break
            
            if opensslconf_found:
                openssl_include_dir = os.path.dirname(os.path.dirname(opensslconf_found))
                os.environ['OPENSSL_DIR'] = openssl_include_dir
                os.environ['OPENSSL_INCLUDE_DIR'] = openssl_include_dir
                os.environ['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                # Также устанавливаем в локальный env
                env['OPENSSL_DIR'] = openssl_include_dir
                env['OPENSSL_INCLUDE_DIR'] = openssl_include_dir
                env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                # Также устанавливаем для x86_64-unknown-linux-gnu
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR'] = openssl_include_dir
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR'] = openssl_include_dir
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                info(f"[CryptographyRecipe] Found opensslconf.h at: {opensslconf_found}")
                info(f"[CryptographyRecipe] Set OPENSSL_DIR = {openssl_include_dir} (in os.environ and env)")
            elif os.path.exists('/usr/include/openssl'):
                os.environ['OPENSSL_DIR'] = '/usr'
                os.environ['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                os.environ['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                # Также устанавливаем в локальный env
                env['OPENSSL_DIR'] = '/usr'
                env['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                env['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                # Также устанавливаем для x86_64-unknown-linux-gnu
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR'] = '/usr'
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR'] = '/usr/include'
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                warning("[CryptographyRecipe] opensslconf.h not found, using standard paths")
                info("[CryptographyRecipe] Set system OpenSSL for Rust (OPENSSL_DIR=/usr in os.environ and env)")
            else:
                warning("[CryptographyRecipe] Could not find OpenSSL headers, Rust build may fail")
        
        # КРИТИЧНО: Получаем путь к site-packages hostpython3 для установки пакетов
        # НЕ устанавливаем PYTHONPATH до установки пакетов, чтобы pip мог установить в правильное место
        hostpython_site_packages = None
        try:
            # Вычисляем путь вручную, так как site.getsitepackages() может вернуть системный путь
            if 'native-build' in str(hostpython):
                # Путь к hostpython3 site-packages обычно в native-build/Lib/site-packages
                hostpython_dir = os.path.dirname(os.path.dirname(str(hostpython)))
                potential_site_packages = os.path.join(hostpython_dir, 'native-build', 'Lib', 'site-packages')
                if os.path.exists(potential_site_packages):
                    hostpython_site_packages = potential_site_packages
                    info(f"[CryptographyRecipe] Using hostpython site-packages: {hostpython_site_packages}")
                else:
                    # Альтернативный путь: native-build/build/lib.linux-x86_64-3.11
                    alt_site_packages = os.path.join(hostpython_dir, 'native-build', 'build', 'lib.linux-x86_64-3.11')
                    if os.path.exists(alt_site_packages):
                        hostpython_site_packages = alt_site_packages
                        info(f"[CryptographyRecipe] Using alternative hostpython site-packages: {hostpython_site_packages}")
                    else:
                        # Пробуем через site.getsitepackages, но проверяем, что это не системный путь
                        temp_env = env.copy()
                        if 'PYTHONPATH' in temp_env:
                            del temp_env['PYTHONPATH']
                        result = shprint(sh.Command(hostpython), '-c', 'import site; print(site.getsitepackages()[0])', _env=temp_env)
                        candidate_path = str(result).strip()
                        # Проверяем, что это не системный путь
                        if '/usr/local/lib/python3' not in candidate_path and '/usr/lib/python3' not in candidate_path:
                            if os.path.exists(candidate_path):
                                hostpython_site_packages = candidate_path
                                info(f"[CryptographyRecipe] Using site.getsitepackages() result: {hostpython_site_packages}")
        except Exception as e:
            warning(f"[CryptographyRecipe] Could not get hostpython site-packages: {e}")
        
        # Устанавливаем setuptools_rust ПЕРЕД вызовом build_ext
        try:
            info("[CryptographyRecipe] Installing setuptools_rust before build_ext...")
            
            # Сначала устанавливаем pip в hostpython, если его нет
            try:
                shprint(sh.Command(hostpython), '-m', 'pip', '--version', _env=env)
                info("[CryptographyRecipe] hostpython has pip")
            except Exception:
                info("[CryptographyRecipe] Installing pip in hostpython using ensurepip...")
                try:
                    shprint(sh.Command(hostpython), '-m', 'ensurepip', '--upgrade', _env=env)
                except Exception:
                    warning("[CryptographyRecipe] ensurepip failed, pip may not be available")
            
            # КРИТИЧНО: Обновляем setuptools в hostpython до версии >=65.0.0 (нужно для CompileError)
            try:
                info("[CryptographyRecipe] Upgrading setuptools in hostpython to >=65.0.0...")
                # Устанавливаем setuptools в site-packages hostpython3 с --target
                if hostpython_site_packages:
                    info(f"[CryptographyRecipe] Installing setuptools to hostpython site-packages: {hostpython_site_packages}")
                    shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '--target', hostpython_site_packages, 'setuptools>=65.0.0', _env=env)
                else:
                    # Fallback: обычная установка
                    shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'setuptools>=65.0.0', _env=env)
                # Проверяем версию и наличие CompileError
                try:
                    # Используем временный env с PYTHONPATH для проверки
                    check_env = env.copy()
                    if hostpython_site_packages:
                        check_env['PYTHONPATH'] = hostpython_site_packages
                    result = shprint(sh.Command(hostpython), '-c', 'import setuptools; print(setuptools.__version__)', _env=check_env)
                    info(f"[CryptographyRecipe] setuptools version in hostpython: {result}")
                    # Проверяем наличие CompileError в hostpython3
                    try:
                        check_script = '''
import sys
import setuptools
print(f"setuptools version: {setuptools.__version__}")
print(f"setuptools location: {setuptools.__file__}")
from setuptools.errors import CompileError
print("CompileError found")
print(f"setuptools.errors location: {sys.modules['setuptools.errors'].__file__}")
'''
                        shprint(sh.Command(hostpython), '-c', check_script, _env=check_env)
                        info("[CryptographyRecipe] CompileError is available in setuptools.errors")
                    except Exception as e:
                        warning(f"[CryptographyRecipe] CompileError NOT found in setuptools.errors: {e}")
                        # Пробуем установить setuptools еще раз в hostpython site-packages
                        info("[CryptographyRecipe] Retrying setuptools installation...")
                        if hostpython_site_packages:
                            shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '--no-cache-dir', '--target', hostpython_site_packages, 'setuptools>=65.0.0', _env=env)
                        else:
                            shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '--no-cache-dir', 'setuptools>=65.0.0', _env=env)
                except Exception as e:
                    warning(f"[CryptographyRecipe] Could not verify setuptools version: {e}")
            except Exception as e:
                warning(f"[CryptographyRecipe] Failed to upgrade setuptools: {e}")
                import traceback
                traceback.print_exc()
            
            # Устанавливаем setuptools_rust в hostpython
            try:
                info("[CryptographyRecipe] Installing setuptools_rust in hostpython...")
                shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--upgrade', 'pip', 'wheel', _env=env)
                
                # КРИТИЧНО: Устанавливаем setuptools_rust в site-packages hostpython3, а не в системный python3
                # Используем --target для явного указания пути установки
                if hostpython_site_packages:
                    info(f"[CryptographyRecipe] Installing setuptools_rust to hostpython site-packages: {hostpython_site_packages}")
                    shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--force-reinstall', '--target', hostpython_site_packages, 'setuptools_rust', _env=env)
                else:
                    # Fallback: обычная установка
                    warning("[CryptographyRecipe] Could not determine hostpython site-packages, using default installation")
                    shprint(sh.Command(hostpython), '-m', 'pip', 'install', '--force-reinstall', 'setuptools_rust', _env=env)
                
                # Проверяем, что setuptools_rust установлен в hostpython и использует правильный setuptools
                try:
                    # Используем временный env с PYTHONPATH для проверки
                    check_env = env.copy()
                    if hostpython_site_packages:
                        check_env['PYTHONPATH'] = hostpython_site_packages
                    # Проверяем путь к setuptools_rust - должен быть в hostpython, а не в системном python
                    check_script = '''
import sys
import setuptools_rust
print(f"setuptools_rust location: {setuptools_rust.__file__}")
print(f"sys.path: {sys.path}")
# Проверяем, что setuptools_rust использует правильный setuptools
import setuptools
print(f"setuptools location: {setuptools.__file__}")
from setuptools.errors import CompileError
print("CompileError imported successfully")
'''
                    result = shprint(sh.Command(hostpython), '-c', check_script, _env=check_env)
                    info(f"[CryptographyRecipe] Verification result: {result}")
                    info("[CryptographyRecipe] setuptools_rust can successfully import CompileError")
                except Exception as e:
                    warning(f"[CryptographyRecipe] Verification failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                info("[CryptographyRecipe] setuptools_rust installed in hostpython")
            except Exception as e:
                warning(f"[CryptographyRecipe] Failed to install setuptools_rust in hostpython: {e}")
                import traceback
                traceback.print_exc()
            
            info("[CryptographyRecipe] setuptools_rust ready for build")
        except Exception as e:
            warning(f"[CryptographyRecipe] CRITICAL: Failed to install setuptools_rust: {e}")
            import traceback
            traceback.print_exc()
        
        # КРИТИЧНО: Устанавливаем PYTHONPATH так, чтобы hostpython3 использовал только свои пакеты
        # Делаем это ПОСЛЕ установки пакетов, чтобы pip мог установить в правильное место
        if hostpython_site_packages:
            env['PYTHONPATH'] = hostpython_site_packages
            info(f"[CryptographyRecipe] Set PYTHONPATH to hostpython site-packages: {env['PYTHONPATH']}")
        else:
            # Если не удалось получить путь, очищаем PYTHONPATH от системных путей
            if 'PYTHONPATH' in env:
                pythonpath_parts = env['PYTHONPATH'].split(':')
                filtered_parts = [p for p in pythonpath_parts if '/usr/local/lib/python3' not in p and '/usr/lib/python3' not in p]
                if filtered_parts:
                    env['PYTHONPATH'] = ':'.join(filtered_parts)
                else:
                    del env['PYTHONPATH']
                info(f"[CryptographyRecipe] Cleaned PYTHONPATH, remaining: {env.get('PYTHONPATH', 'None')}")
        
        # КРИТИЧНО: Исправляем поврежденный setup.py от предыдущих патчей
        # Если файл поврежден, восстанавливаем его из исходников cryptography
        build_dir = self.get_build_dir(arch.arch)
        setup_py_path = os.path.join(build_dir, 'setup.py')
        
        if os.path.exists(setup_py_path):
            try:
                info("[CryptographyRecipe] Checking setup.py for previous patch damage...")
                with open(setup_py_path, 'r') as f:
                    content = f.read()
                
                # Проверяем наличие патча
                has_patch = '# PATCHED: Remove system paths from sys.path' in content
                
                # Проверяем синтаксис файла
                syntax_valid = True
                syntax_error = None
                try:
                    compile(content, setup_py_path, 'exec')
                except SyntaxError as e:
                    syntax_valid = False
                    syntax_error = str(e)
                    warning(f"[CryptographyRecipe] setup.py has syntax error: {syntax_error}")
                
                # Если есть патч или синтаксическая ошибка - восстанавливаем из исходников
                if has_patch or not syntax_valid:
                    info("[CryptographyRecipe] Found damaged setup.py, restoring from source...")
                    restored = False
                    try:
                        # Ищем setup.py в различных возможных местах
                        possible_locations = [
                            # В build_dir (может быть распакован там)
                            build_dir,
                            # В родительской директории
                            os.path.dirname(build_dir),
                            # В директории с исходниками cryptography
                            os.path.join(os.path.dirname(build_dir), 'cryptography'),
                            # В директории рецепта
                            self.get_recipe_dir() if hasattr(self, 'get_recipe_dir') else None,
                        ]
                        
                        source_setup = None
                        for location in possible_locations:
                            if location and os.path.exists(location):
                                potential_setup = os.path.join(location, 'setup.py')
                                if os.path.exists(potential_setup):
                                    # Проверяем, что это не поврежденный файл
                                    try:
                                        with open(potential_setup, 'r') as f:
                                            test_content = f.read()
                                        compile(test_content, potential_setup, 'exec')
                                        source_setup = potential_setup
                                        break
                                    except (SyntaxError, Exception):
                                        continue
                        
                        if source_setup:
                            # Копируем setup.py из исходников
                            import shutil
                            shutil.copy2(source_setup, setup_py_path)
                            info(f"[CryptographyRecipe] Restored setup.py from {source_setup}")
                            restored = True
                        else:
                            # Если не нашли исходники, пробуем восстановить из backup
                            backup_path = setup_py_path + '.backup'
                            if os.path.exists(backup_path):
                                try:
                                    with open(backup_path, 'r') as f:
                                        backup_content = f.read()
                                    # Проверяем, что backup не поврежден
                                    if '# PATCHED' not in backup_content:
                                        try:
                                            compile(backup_content, backup_path, 'exec')
                                            import shutil
                                            shutil.copy2(backup_path, setup_py_path)
                                            info("[CryptographyRecipe] Restored setup.py from backup")
                                            restored = True
                                        except SyntaxError:
                                            pass
                                except Exception:
                                    pass
                            
                            if not restored:
                                # Если не удалось восстановить, просто удаляем поврежденный файл
                                # python-for-android должен пересобрать его из архива
                                import shutil
                                backup_path = setup_py_path + '.backup'
                                if os.path.exists(setup_py_path):
                                    shutil.move(setup_py_path, backup_path)
                                    info(f"[CryptographyRecipe] Could not find source, removed damaged setup.py (moved to {backup_path})")
                                    info("[CryptographyRecipe] setup.py will be regenerated from archive during build")
                    except Exception as e2:
                        warning(f"[CryptographyRecipe] Failed to restore setup.py: {e2}")
                        # Если не удалось восстановить, удаляем файл
                        if not restored:
                            try:
                                import shutil
                                backup_path = setup_py_path + '.backup'
                                if os.path.exists(setup_py_path):
                                    shutil.move(setup_py_path, backup_path)
                                    info(f"[CryptographyRecipe] Removed damaged setup.py (moved to {backup_path})")
                            except Exception as e3:
                                warning(f"[CryptographyRecipe] Could not remove setup.py: {e3}")
                else:
                    info("[CryptographyRecipe] setup.py is clean, no issues found")
            except Exception as e:
                warning(f"[CryptographyRecipe] Failed to check setup.py: {e}")
        
        # КРИТИЧНО: Убеждаемся, что setup.py существует перед вызовом build_compiled_components
        # Если файл был удален и не восстановлен, python-for-android должен распаковать его из архива
        if not os.path.exists(setup_py_path):
            info("[CryptographyRecipe] setup.py is missing, will be extracted from archive during build")
            # Пробуем найти архив cryptography и распаковать setup.py
            try:
                # Ищем архив в директории пакетов
                packages_dir = os.path.join(self.ctx.packages_path, 'cryptography')
                if os.path.exists(packages_dir):
                    # Ищем tar.gz или zip файл
                    import glob
                    archive_patterns = [
                        os.path.join(packages_dir, 'cryptography-*.tar.gz'),
                        os.path.join(packages_dir, 'cryptography-*.zip'),
                    ]
                    
                    for pattern in archive_patterns:
                        archives = glob.glob(pattern)
                        if archives:
                            archive_path = archives[0]
                            info(f"[CryptographyRecipe] Found cryptography archive: {archive_path}")
                            # Распаковываем только setup.py из архива
                            try:
                                import tarfile
                                if archive_path.endswith('.tar.gz'):
                                    with tarfile.open(archive_path, 'r:gz') as tar:
                                        # Ищем setup.py в архиве
                                        for member in tar.getmembers():
                                            if member.name.endswith('setup.py'):
                                                # Извлекаем setup.py
                                                tar.extract(member, build_dir)
                                                # Перемещаем в правильное место
                                                extracted_path = os.path.join(build_dir, member.name)
                                                if os.path.exists(extracted_path) and extracted_path != setup_py_path:
                                                    import shutil
                                                    shutil.move(extracted_path, setup_py_path)
                                                    info("[CryptographyRecipe] Extracted setup.py from archive")
                                                    break
                            except Exception as e:
                                warning(f"[CryptographyRecipe] Failed to extract setup.py from archive: {e}")
                            break
            except Exception as e:
                warning(f"[CryptographyRecipe] Could not find/extract setup.py from archive: {e}")
        
        # КРИТИЧНО: Переменные окружения уже установлены в начале функции
        # Убеждаемся, что они также установлены в локальном env
        env['CC'] = '/usr/bin/cc'
        env['CC_x86_64-unknown-linux-gnu'] = '/usr/bin/cc'
        env['HOST_CC'] = '/usr/bin/cc'
        env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC'] = '/usr/bin/cc'
        env['CFLAGS'] = ''
        env['CFLAGS_x86_64-unknown-linux-gnu'] = ''
        env['HOST_CFLAGS'] = ''
        env['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS'] = ''
        
        info("[CryptographyRecipe] All Rust environment variables set in both os.environ and env")
        
        # Устанавливаем OPENSSL_DIR для Rust (если еще не установлен) - но это не нужно при OPENSSL_VENDORED=1
        if 'OPENSSL_DIR' not in os.environ:
            # Ищем opensslconf.h в различных местах
            opensslconf_paths = [
                '/usr/include/openssl/opensslconf.h',
                '/usr/include/x86_64-linux-gnu/openssl/opensslconf.h',
            ]
            opensslconf_found = None
            for path in opensslconf_paths:
                if os.path.exists(path):
                    opensslconf_found = path
                    break
            
            if opensslconf_found:
                openssl_include_dir = os.path.dirname(os.path.dirname(opensslconf_found))
                os.environ['OPENSSL_DIR'] = openssl_include_dir
                os.environ['OPENSSL_INCLUDE_DIR'] = openssl_include_dir
                os.environ['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                info(f"[CryptographyRecipe] Found opensslconf.h at {opensslconf_found}, set OPENSSL_DIR = {openssl_include_dir}")
            elif os.path.exists('/usr/include/openssl'):
                os.environ['OPENSSL_DIR'] = '/usr'
                os.environ['OPENSSL_INCLUDE_DIR'] = '/usr/include'
                os.environ['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
                info("[CryptographyRecipe] Set OPENSSL_DIR in os.environ before build: /usr")
            else:
                warning("[CryptographyRecipe] Could not find OpenSSL headers, Rust build may fail")
        
        # КРИТИЧНО: Создаем симлинк для openssl/configuration.h если его нет
        # openssl-sys 0.9.96 требует configuration.h
        openssl_include = os.environ.get('OPENSSL_INCLUDE_DIR', '/usr/include')
        openssl_dir = os.path.join(openssl_include, 'openssl')
        openssl_config_h = os.path.join(openssl_dir, 'configuration.h')
        opensslconf_h = os.path.join(openssl_dir, 'opensslconf.h')
        
        if not os.path.exists(openssl_config_h):
            info("[CryptographyRecipe] openssl/configuration.h not found, creating symlink...")
            opensslconf_found = None
            
            # Пробуем найти opensslconf.h в различных местах
            for path in [opensslconf_h, '/usr/include/openssl/opensslconf.h', '/usr/include/x86_64-linux-gnu/openssl/opensslconf.h']:
                if os.path.exists(path):
                    opensslconf_found = path
                    info(f"[CryptographyRecipe] Found opensslconf.h at: {path}")
                    break
            
            if opensslconf_found:
                try:
                    os.makedirs(openssl_dir, exist_ok=True)
                    # Используем относительный путь если в той же директории
                    if opensslconf_found == opensslconf_h:
                        symlink_target = 'opensslconf.h'
                    else:
                        symlink_target = opensslconf_found
                    
                    # Удаляем старый симлинк если есть
                    if os.path.exists(openssl_config_h) or os.path.islink(openssl_config_h):
                        try:
                            os.remove(openssl_config_h)
                        except:
                            pass
                    
                    os.symlink(symlink_target, openssl_config_h)
                    info(f"[CryptographyRecipe] Created symlink: {openssl_config_h} -> {symlink_target}")
                    
                    # Проверяем, что симлинк работает
                    if os.path.exists(openssl_config_h):
                        info("[CryptographyRecipe] Symlink verified successfully")
                    else:
                        warning("[CryptographyRecipe] Symlink created but file not accessible")
                except Exception as e:
                    warning(f"[CryptographyRecipe] Could not create configuration.h symlink: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                warning("[CryptographyRecipe] opensslconf.h not found, cannot create configuration.h symlink")
        
        # OPENSSL_VENDORED уже установлен выше
        
        # КРИТИЧНО: Также устанавливаем переменные для x86_64-unknown-linux-gnu
        if 'OPENSSL_DIR' in os.environ:
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR'] = os.environ['OPENSSL_DIR']
            if 'OPENSSL_INCLUDE_DIR' in os.environ:
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR'] = os.environ['OPENSSL_INCLUDE_DIR']
            if 'OPENSSL_LIB_DIR' in os.environ:
                os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR'] = os.environ['OPENSSL_LIB_DIR']
            
        # Проверяем, что все критические переменные установлены перед вызовом super()
        info("[CryptographyRecipe] Final check before build:")
        info(f"[CryptographyRecipe] OPENSSL_VENDORED = {os.environ.get('OPENSSL_VENDORED', 'NOT SET')}")
        info(f"[CryptographyRecipe] CC = {os.environ.get('CC', 'NOT SET')}")
        info(f"[CryptographyRecipe] CC_x86_64-unknown-linux-gnu = {os.environ.get('CC_x86_64-unknown-linux-gnu', 'NOT SET')}")
        info(f"[CryptographyRecipe] HOST_CC = {os.environ.get('HOST_CC', 'NOT SET')}")
        info(f"[CryptographyRecipe] CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC = {os.environ.get('CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC', 'NOT SET')}")
        info(f"[CryptographyRecipe] CCACHE_DISABLE = {os.environ.get('CCACHE_DISABLE', 'NOT SET')}")
        info(f"[CryptographyRecipe] CFLAGS = {os.environ.get('CFLAGS', 'NOT SET')}")
        
        # Вызываем стандартную сборку
        try:
            super().build_compiled_components(arch)
        finally:
            # Восстанавливаем оригинальные CC и CFLAGS в os.environ после Rust-компиляции
            if '_ORIGINAL_CC_GLOBAL' in os.environ:
                os.environ['CC'] = os.environ['_ORIGINAL_CC_GLOBAL']
                del os.environ['_ORIGINAL_CC_GLOBAL']
            elif '_ORIGINAL_CC' in os.environ:
                os.environ['CC'] = os.environ['_ORIGINAL_CC']
                del os.environ['_ORIGINAL_CC']
            if '_ORIGINAL_CFLAGS_GLOBAL' in os.environ:
                os.environ['CFLAGS'] = os.environ['_ORIGINAL_CFLAGS_GLOBAL']
                del os.environ['_ORIGINAL_CFLAGS_GLOBAL']
            elif '_ORIGINAL_CFLAGS' in os.environ:
                os.environ['CFLAGS'] = os.environ['_ORIGINAL_CFLAGS']
                del os.environ['_ORIGINAL_CFLAGS']
            # Восстанавливаем ccache
            if 'CCACHE_DISABLE' in os.environ:
                del os.environ['CCACHE_DISABLE']
            # Очищаем Rust-специфичные переменные
            for var in ['CC_x86_64-unknown-linux-gnu', 'CFLAGS_x86_64-unknown-linux-gnu', 
                       'HOST_CC', 'HOST_CFLAGS', 'CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC', 
                       'CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS']:
                if var in os.environ:
                    del os.environ[var]


# КРИТИЧНО: Экспорт экземпляра рецепта (обязательно для python-for-android)
recipe = CryptographyRecipe()
