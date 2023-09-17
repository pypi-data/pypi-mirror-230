# win-basic-tools

Description:  
CLI tool for listing a directory in Windows.  
Also has config helper for cmd.exe.

## Installation

~~~
> pip install win-basic-tools
~~~

## Usage

~~~
$ win-basic-tools setup
~~~

This will create aliases like `python -m win_basic_tools -acil`, "acil" being each letter an option.  
'a' for all files, 'c' for colors, 'i' for icons and 'l' for list.  
  
It will create the `.macros.doskey` at your home directory and point it in Registry.  
After refreshing your prompt, you can use `ls`, `ll`, `touch`. See `%USERPROFILE%\.macros.doskey` for the list of aliases.  
  
Uninstall: run `win-basic-tools uninstall` before `pip uninstall` for reseting Registry.  
  
Also has further options for integrating with other programs.  

#### Image

![Aplication exmaple](./example/ll_example.png "Example")

## License

[MIT](https://choosealicense.com/licenses/mit/)
