"""
Хук для установки setuptools_rust и настройки переменных окружения для Rust перед сборкой cryptography
"""
import os
import sh
import glob
from pythonforandroid.logger import info, warning

def pre_build_dist(ctx):
    """Установка setuptools_rust перед сборкой"""
    info("[Hook] Pre-build-dist hook: Installing setuptools_rust")
    
    hostpython = sh.which('python3') or '/usr/bin/python3'
    env = os.environ.copy()
    cargo_path = "/root/.cargo/bin"
    if 'PATH' in env:
        if cargo_path not in env['PATH']:
            env['PATH'] = f"{cargo_path}:{env['PATH']}"
    env['CARGO_HOME'] = '/root/.cargo'
    env['RUSTUP_HOME'] = '/root/.rustup'
    
    try:
        info("[Hook] Installing setuptools_rust globally...")
        sh.Command(hostpython)('-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel', _env=env)
        sh.Command(hostpython)('-m', 'pip', 'install', 'setuptools_rust', 'cffi', _env=env)
        info("[Hook] setuptools_rust installed successfully")
    except Exception as e:
        warning(f"[Hook] Failed to install setuptools_rust: {e}")

def pre_build_arch(ctx, arch):
    """Дополнительная установка setuptools_rust и настройка переменных окружения перед сборкой архитектуры"""
    info("[Hook] Pre-build-arch hook: Ensuring setuptools_rust is available and setting Rust environment")
    
    hostpython = sh.which('python3') or '/usr/bin/python3'
    env = os.environ.copy()
    cargo_path = "/root/.cargo/bin"
    if 'PATH' in env:
        if cargo_path not in env['PATH']:
            env['PATH'] = f"{cargo_path}:{env['PATH']}"
    env['CARGO_HOME'] = '/root/.cargo'
    env['RUSTUP_HOME'] = '/root/.rustup'
    
    try:
        sh.Command(hostpython)('-m', 'pip', 'install', '--quiet', 'setuptools_rust', 'cffi', _env=env)
    except Exception as e:
        warning(f"[Hook] Failed to install setuptools_rust: {e}")
    
    # КРИТИЧНО: Устанавливаем переменные окружения для Rust в os.environ
    # Это гарантирует, что они будут доступны когда Rust запустится
    info("[Hook] Setting Rust environment variables in os.environ")
    
    # КРИТИЧНО: Сохраняем оригинальные CC и CFLAGS, если они установлены для Android
    original_cc = os.environ.get('CC', '')
    original_cflags = os.environ.get('CFLAGS', '')
    
    # Если CC указывает на Android NDK, сохраняем его для восстановления
    if 'android-ndk' in original_cc or 'clang' in original_cc:
        os.environ['_ORIGINAL_CC'] = original_cc
        os.environ['_ORIGINAL_CFLAGS'] = original_cflags
        info(f"[Hook] Saved original CC: {original_cc}")
    
    # Устанавливаем переменные для системного компилятора (для Rust host compilation)
    # Rust компилирует для x86_64-unknown-linux-gnu, а не для Android
    os.environ['CC_x86_64-unknown-linux-gnu'] = '/usr/bin/cc'
    os.environ['CFLAGS_x86_64-unknown-linux-gnu'] = ''
    os.environ['HOST_CC'] = '/usr/bin/cc'
    os.environ['HOST_CFLAGS'] = ''
    os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC'] = '/usr/bin/cc'
    os.environ['CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CFLAGS'] = ''
    
    # КРИТИЧНО: Временно переопределяем CC для Rust, чтобы он не использовал Android NDK компилятор
    # Это нужно только для Rust build script, который компилирует для хост-платформы
    os.environ['_RUST_CC'] = '/usr/bin/cc'
    os.environ['_RUST_CFLAGS'] = ''
    
    info("[Hook] Set CC_x86_64-unknown-linux-gnu = /usr/bin/cc")
    info("[Hook] Set HOST_CC = /usr/bin/cc")
    info("[Hook] Set CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_CC = /usr/bin/cc")
    
    # Ищем OpenSSL и устанавливаем переменные
    openssl_paths = [
        '/usr/include/openssl',
        '/usr/include/x86_64-linux-gnu/openssl',
        '/usr/local/include/openssl',
    ]
    
    openssl_dir = None
    openssl_include_dir = None
    openssl_lib_dir = None
    
    # Проверяем наличие opensslconf.h
    opensslconf_paths = [
        '/usr/include/openssl/opensslconf.h',
        '/usr/include/x86_64-linux-gnu/openssl/opensslconf.h',
        '/usr/lib/x86_64-linux-gnu/openssl/opensslconf.h',
    ]
    
    opensslconf_found = None
    for path in opensslconf_paths:
        if os.path.exists(path):
            opensslconf_found = path
            info(f"[Hook] Found opensslconf.h at: {path}")
            openssl_include_dir = os.path.dirname(os.path.dirname(path))
            openssl_dir = openssl_include_dir
            break
    
    if not opensslconf_found:
        # Пробуем найти через pkg-config
        try:
            pkg_config = sh.which('pkg-config') or '/usr/bin/pkg-config'
            openssl_prefix = sh.Command(pkg_config)('--variable=prefix', 'openssl', _env=env).strip()
            openssl_include = sh.Command(pkg_config)('--variable=includedir', 'openssl', _env=env).strip()
            openssl_lib = sh.Command(pkg_config)('--variable=libdir', 'openssl', _env=env).strip()
            
            if os.path.exists(openssl_include):
                openssl_dir = openssl_prefix
                openssl_include_dir = openssl_include
                openssl_lib_dir = openssl_lib
                info(f"[Hook] Found OpenSSL via pkg-config: prefix={openssl_prefix}, include={openssl_include}, lib={openssl_lib}")
        except Exception as e:
            warning(f"[Hook] Failed to find OpenSSL via pkg-config: {e}")
    
    # Если не нашли через pkg-config, пробуем стандартные пути
    if not openssl_dir:
        for path in openssl_paths:
            if os.path.exists(path):
                openssl_dir = '/usr'
                openssl_include_dir = '/usr/include'
                openssl_lib_dir = '/usr/lib/x86_64-linux-gnu'
                info(f"[Hook] Using standard OpenSSL path: {openssl_dir}")
                break
    
    # Устанавливаем переменные окружения для OpenSSL
    if openssl_dir:
        os.environ['OPENSSL_DIR'] = openssl_dir
        if openssl_include_dir:
            os.environ['OPENSSL_INCLUDE_DIR'] = openssl_include_dir
        if openssl_lib_dir:
            os.environ['OPENSSL_LIB_DIR'] = openssl_lib_dir
        
        # Также устанавливаем для x86_64-unknown-linux-gnu
        os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR'] = openssl_dir
        if openssl_include_dir:
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR'] = openssl_include_dir
        if openssl_lib_dir:
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR'] = openssl_lib_dir
        
        info(f"[Hook] Set OPENSSL_DIR = {openssl_dir}")
        if openssl_include_dir:
            info(f"[Hook] Set OPENSSL_INCLUDE_DIR = {openssl_include_dir}")
        if openssl_lib_dir:
            info(f"[Hook] Set OPENSSL_LIB_DIR = {openssl_lib_dir}")
    else:
        # Fallback: используем стандартные пути
        if os.path.exists('/usr/include/openssl'):
            os.environ['OPENSSL_DIR'] = '/usr'
            os.environ['OPENSSL_INCLUDE_DIR'] = '/usr/include'
            os.environ['OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR'] = '/usr'
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR'] = '/usr/include'
            os.environ['X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR'] = '/usr/lib/x86_64-linux-gnu'
            info("[Hook] Set OPENSSL_DIR to /usr (fallback)")
        else:
            warning("[Hook] Could not find OpenSSL installation, Rust build may fail")
    
    # КРИТИЧНО: Проверяем наличие openssl/configuration.h и создаем симлинк если нужно
    # openssl-sys 0.9.96 требует configuration.h, но в Ubuntu 22.04 его может не быть
    openssl_include = os.environ.get('OPENSSL_INCLUDE_DIR', '/usr/include')
    openssl_dir = os.path.join(openssl_include, 'openssl')
    openssl_config_h = os.path.join(openssl_dir, 'configuration.h')
    opensslconf_h = os.path.join(openssl_dir, 'opensslconf.h')
    
    if not os.path.exists(openssl_config_h):
        info("[Hook] openssl/configuration.h not found, attempting to create symlink...")
        
        # Пробуем найти opensslconf.h в различных местах
        possible_opensslconf_locations = [
            opensslconf_h,
            '/usr/include/openssl/opensslconf.h',
            '/usr/include/x86_64-linux-gnu/openssl/opensslconf.h',
        ]
        
        opensslconf_found = None
        for loc in possible_opensslconf_locations:
            if os.path.exists(loc):
                opensslconf_found = loc
                info(f"[Hook] Found opensslconf.h at: {loc}")
                break
        
        if opensslconf_found:
            try:
                # Создаем директорию если нужно
                os.makedirs(openssl_dir, exist_ok=True)
                
                # Создаем симлинк
                if opensslconf_found == opensslconf_h:
                    # Если opensslconf.h в той же директории, используем относительный путь
                    symlink_target = 'opensslconf.h'
                else:
                    # Используем абсолютный путь
                    symlink_target = opensslconf_found
                
                if not os.path.exists(openssl_config_h):
                    os.symlink(symlink_target, openssl_config_h)
                    info(f"[Hook] Created symlink: {openssl_config_h} -> {symlink_target}")
                else:
                    info(f"[Hook] configuration.h already exists at {openssl_config_h}")
            except Exception as e:
                warning(f"[Hook] Could not create symlink for configuration.h: {e}")
                import traceback
                traceback.print_exc()
        else:
            warning("[Hook] opensslconf.h not found, cannot create configuration.h symlink")
            warning("[Hook] This may cause openssl-sys build to fail")
    
    # КРИТИЧНО: Используем vendored OpenSSL для openssl-sys
    # Это избавит нас от проблем с системным OpenSSL
    os.environ['OPENSSL_VENDORED'] = '1'
    os.environ['OPENSSL_STATIC'] = '1'  # Статическая линковка
    # НЕ отключаем ccache глобально - только для Rust build script через локальный env
    info("[Hook] Using vendored OpenSSL for openssl-sys (OPENSSL_VENDORED=1, OPENSSL_STATIC=1)")
    info("[Hook] This will compile OpenSSL from source, avoiding system OpenSSL issues")
    info("[Hook] Note: ccache remains enabled for faster builds")
    
    # Проверяем, что переменные установлены
    info("[Hook] Final environment check:")
    info(f"[Hook] CC_x86_64-unknown-linux-gnu = {os.environ.get('CC_x86_64-unknown-linux-gnu', 'NOT SET')}")
    info(f"[Hook] HOST_CC = {os.environ.get('HOST_CC', 'NOT SET')}")
    info(f"[Hook] OPENSSL_VENDORED = {os.environ.get('OPENSSL_VENDORED', 'NOT SET')}")
    info(f"[Hook] OPENSSL_DIR = {os.environ.get('OPENSSL_DIR', 'NOT SET')}")
    info(f"[Hook] OPENSSL_INCLUDE_DIR = {os.environ.get('OPENSSL_INCLUDE_DIR', 'NOT SET')}")
    info(f"[Hook] openssl/configuration.h exists: {os.path.exists(openssl_config_h) if 'openssl_config_h' in locals() else 'N/A'}")
