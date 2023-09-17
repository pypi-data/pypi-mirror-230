import os
import sys
import winreg

SUB_KEY = "Software\\Microsoft\\Command Processor"
HOME_PATH = os.path.expanduser('~')


def setup():

    with open(f'{HOME_PATH}\\.macros.doskey', 'w') as f:
        print(
            'ls=python -m win_basic_tools $*',
            'll=python -m win_basic_tools -cilm $*',
            'la=python -m win_basic_tools -acilmhAH $*',
            'touch=echo off $T for %x in ($*) do type nul > %x $T echo on',
            'cat=type $1',
            'pwd=cd',
            'mv=move $1 $2',
            'rm=del $*',
            sep='\n',
            file=f
        )

    key_handle = winreg.OpenKeyEx(
        winreg.HKEY_CURRENT_USER, SUB_KEY, 0, winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(
        key_handle,
        'Autorun',
        0,
        winreg.REG_SZ,
        f'doskey /macrofile="{HOME_PATH}\\.macros.doskey"'
    )
    winreg.CloseKey(key_handle)

    print('Refresh your cmd.exe for complete install.')


def uninstall():
    key_handle = winreg.OpenKeyEx(
        winreg.HKEY_CURRENT_USER, SUB_KEY, 0, winreg.KEY_SET_VALUE
    )
    try:
        winreg.DeleteValue(key_handle, 'Autorun')
    except FileNotFoundError:
        print("Registry key wasn't found.")

    winreg.CloseKey(key_handle)

    try:
        os.remove(HOME_PATH + '\\.macros.doskey')
    except FileNotFoundError:
        print("Macros file wasn't found.")

    print('Refresh your cmd.exe for complete uninstall.')


def main():
    if sys.platform != 'win32':
        print('This is intended for Windows OS.')
        return 1

    if len(sys.argv) < 2:
        pass
    elif sys.argv[1] == 'uninstall':
        uninstall()
        return 0
    elif sys.argv[1] == 'setup':
        setup()
        return 0

    print(
        'This script does the setup and the uninstall of win_basic_tools.',
        'Run:',
        '> win-basic-tools setup',
        'Or:',
        '> win-basic-tools uninstall',
        'Then refresh your cmd.exe',
        sep='\n'
    )
    return 1


if __name__ == '__main__':
    sys.exit(main())
