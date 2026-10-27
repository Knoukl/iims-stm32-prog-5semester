#!/usr/bin/env python3
"""
Simple and reliable build script for STM32F107 on EasyMx PRO v7.
Supports build, clean, and flash with auto-detection of toolchain and OpenOCD.
"""

import sys
import os
import subprocess
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_DIR, "build")


def get_toolchain_bin():
    """Locate arm-none-eabi-gcc directory automatically."""
    env = os.environ.get("ARM_TOOLCHAIN_BIN")
    if env and os.path.isfile(os.path.join(env, "arm-none-eabi-gcc.exe")):
        return env

    gcc = shutil.which("arm-none-eabi-gcc")
    if gcc:
        return os.path.dirname(gcc)

    home = os.path.expanduser("~")
    candidates = [
        r"C:\ST\STM32CubeIDE_1.10.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.10.3-2021.10.win32_1.0.0.202111181127\tools\bin",
        os.path.join(home, r"AppData\Local\stm32cube\bundles\gnu-tools-for-stm32\14.3.1+st.2\bin"),
        r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin",
        r"C:\Program Files\Arm GNU Toolchain\bin",
    ]
    for c in candidates:
        if os.path.isfile(os.path.join(c, "arm-none-eabi-gcc.exe")):
            return c

    if os.path.exists(r"C:\ST"):
        for root, dirs, files in os.walk(r"C:\ST"):
            if "arm-none-eabi-gcc.exe" in files:
                return root

    cube_local = os.path.join(home, r"AppData\Local\stm32cube")
    if os.path.exists(cube_local):
        for root, dirs, files in os.walk(cube_local):
            if "arm-none-eabi-gcc.exe" in files:
                return root

    return None


def get_openocd_exe():
    """Locate openocd executable automatically."""
    ocd = shutil.which("openocd")
    if ocd:
        return ocd

    home = os.path.expanduser("~")
    winget_root = os.path.join(home, r"AppData\Local\Microsoft\WinGet\Packages")
    if os.path.exists(winget_root):
        for root, dirs, files in os.walk(winget_root):
            if "openocd.exe" in files:
                return os.path.join(root, "openocd.exe")

    fallback = r"C:\xpack-openocd\bin\openocd.exe"
    if os.path.isfile(fallback):
        return fallback

    return None


CFLAGS = [
    "-mcpu=cortex-m3",
    "-mthumb",
    "-O2",
    "-g3",
    "-Wall",
    "-fdata-sections",
    "-ffunction-sections",
    "-fno-lto",
    "-DSTM32F107xC",
    "-DUSE_HAL_DRIVER",
    f"-I{os.path.join(PROJECT_DIR, 'Core', 'Inc')}",
    f"-I{os.path.join(PROJECT_DIR, 'Drivers', 'STM32F1xx_HAL_Driver', 'Inc')}",
    f"-I{os.path.join(PROJECT_DIR, 'Drivers', 'STM32F1xx_HAL_Driver', 'Inc', 'Legacy')}",
    f"-I{os.path.join(PROJECT_DIR, 'Drivers', 'CMSIS', 'Include')}",
    f"-I{os.path.join(PROJECT_DIR, 'Drivers', 'CMSIS', 'Device', 'ST', 'STM32F1xx', 'Include')}",
]

LDFLAGS = [
    "-mcpu=cortex-m3",
    "-mthumb",
    "-fno-lto",
    "--specs=nano.specs",
    "-T", os.path.join(PROJECT_DIR, "STM32F107VCTX_FLASH.ld"),
    f"-Wl,-Map={os.path.join(BUILD_DIR, 'firmware.map')},--cref",
    "-Wl,--gc-sections",
]

SOURCES_C = [
    # Application & System
    os.path.join(PROJECT_DIR, "Core", "Src", "main.c"),
    os.path.join(PROJECT_DIR, "Core", "Src", "stm32f1xx_it.c"),
    os.path.join(PROJECT_DIR, "Core", "Src", "system_stm32f1xx.c"),
    os.path.join(PROJECT_DIR, "Core", "Src", "syscalls.c"),
    os.path.join(PROJECT_DIR, "Core", "Src", "sysmem.c"),
    # HAL Drivers
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_rcc.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_rcc_ex.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_gpio.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_dma.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_cortex.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_pwr.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_flash.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_flash_ex.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_exti.c"),
    os.path.join(PROJECT_DIR, "Drivers", "STM32F1xx_HAL_Driver", "Src", "stm32f1xx_hal_uart.c"),
]

SOURCES_ASM = [
    os.path.join(PROJECT_DIR, "Startup", "startup_stm32f107vctx.s"),
]


def clean():
    if os.path.exists(BUILD_DIR):
        print(f"Cleaning {BUILD_DIR}...")
        shutil.rmtree(BUILD_DIR)
    print("Clean finished.")


def build():
    toolchain_bin = get_toolchain_bin()
    if not toolchain_bin:
        print("[ERROR] Arm GNU Toolchain (arm-none-eabi-gcc) not found!")
        print("Please install Arm GNU Toolchain or set ARM_TOOLCHAIN_BIN environment variable.")
        sys.exit(1)

    cc = os.path.join(toolchain_bin, "arm-none-eabi-gcc.exe")
    objcopy = os.path.join(toolchain_bin, "arm-none-eabi-objcopy.exe")
    size = os.path.join(toolchain_bin, "arm-none-eabi-size.exe")

    os.makedirs(BUILD_DIR, exist_ok=True)
    objects = []

    # Compile C sources
    for src in SOURCES_C:
        base = os.path.splitext(os.path.basename(src))[0]
        obj = os.path.join(BUILD_DIR, f"{base}.o")
        objects.append(obj)
        print(f"[CC] {os.path.basename(src)}")
        cmd = [cc, "-c"] + CFLAGS + [src, "-o", obj]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"Compilation failed for {src}")
            sys.exit(res.returncode)

    # Compile ASM sources
    for src in SOURCES_ASM:
        base = os.path.splitext(os.path.basename(src))[0]
        obj = os.path.join(BUILD_DIR, f"{base}.o")
        objects.append(obj)
        print(f"[AS] {os.path.basename(src)}")
        cmd = [cc, "-c", "-mcpu=cortex-m3", "-mthumb", "-x", "assembler-with-cpp", src, "-o", obj]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"Assembly failed for {src}")
            sys.exit(res.returncode)

    # Link ELF
    elf = os.path.join(BUILD_DIR, "firmware.elf")
    bin_file = os.path.join(BUILD_DIR, "firmware.bin")
    hex_file = os.path.join(BUILD_DIR, "firmware.hex")

    print(f"[LD] {os.path.basename(elf)}")
    cmd = [cc] + objects + LDFLAGS + ["-o", elf]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("Linking failed.")
        sys.exit(res.returncode)

    # Generate BIN & HEX
    print(f"[CP] {os.path.basename(bin_file)}")
    subprocess.run([objcopy, "-O", "binary", elf, bin_file], check=True)

    print(f"[CP] {os.path.basename(hex_file)}")
    subprocess.run([objcopy, "-O", "ihex", elf, hex_file], check=True)

    # Size
    print("\n--- Memory Size ---")
    subprocess.run([size, elf], check=True)
    print("-------------------")
    print("Build successful!")


def flash():
    build()
    openocd_exe = get_openocd_exe()
    if not openocd_exe:
        print("[ERROR] OpenOCD executable not found!")
        print("Please install OpenOCD via winget install --id xpack-dev-tools.openocd-xpack -e or add to PATH.")
        sys.exit(1)

    elf = os.path.join(BUILD_DIR, "firmware.elf").replace("\\", "/")
    cfg = os.path.join(PROJECT_DIR, "openocd.cfg").replace("\\", "/")

    print(f"\n[FLASH] Programming target via OpenOCD ({openocd_exe})...")
    cmd = [
        openocd_exe,
        "-f", cfg,
        "-c", f"program {{{elf}}} verify reset exit"
    ]
    res = subprocess.run(cmd, cwd=PROJECT_DIR)
    if res.returncode != 0:
        print("Flashing failed.")
        sys.exit(res.returncode)
    print("\nFlashing successful! Microcontroller is running.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "build"
    if action == "clean":
        clean()
    elif action == "build":
        build()
    elif action == "flash":
        flash()
    else:
        print(f"Unknown action: {action}. Use 'build', 'clean', or 'flash'.")
        sys.exit(1)
