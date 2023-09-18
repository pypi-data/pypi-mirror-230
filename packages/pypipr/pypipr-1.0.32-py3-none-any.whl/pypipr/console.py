"""
Modul untuk berinteraksi dengan program console
"""


from .lib import *


def print_colorize(
    text,
    color=colorama.Fore.GREEN,
    bright=colorama.Style.BRIGHT,
    color_end=colorama.Style.RESET_ALL,
    text_start="",
    text_end="\n",
):
    """
    Print text dengan warna untuk menunjukan text penting

    ```py
    print_colorize("Print some text")
    print_colorize("Print some text", color=colorama.Fore.RED)
    ```
    """
    print(f"{text_start}{color + bright}{text}{color_end}", end=text_end, flush=True)


def log(text=None):
    """
    Decorator untuk mempermudah pembuatan log karena tidak perlu mengubah
    fungsi yg sudah ada.
    Melakukan print ke console untuk menginformasikan proses yg sedang
    berjalan didalam program.

    ```py
    @log
    def some_function():
        pass

    @log()
    def some_function_again():
        pass

    @log("Calling some function")
    def some_function_more():
        pass

    some_function()
    some_function_again()
    some_function_more()
    ```
    """

    def inner_log(func=None):
        def callable_func(*args, **kwargs):
            main_function(text)
            result = func(*args, **kwargs)
            return result

        def main_function(param):
            print_log(param)

        if func is None:
            return main_function(text)
        return callable_func

    if text is None:
        return inner_log
    elif callable(text):
        return inner_log(text)
    else:
        # inner_log(None)
        return inner_log


def print_log(text):
    """
    Akan melakukan print ke console.
    Berguna untuk memberikan informasi proses program yg sedang berjalan.

    ```py
    print_log("Standalone Log")
    ```
    """
    print_colorize(f">>> {text}")


def console_run(info, command=None, print_info=True, capture_output=False):
    """
    Menjalankan command seperti menjalankan command di Command Terminal

    ```py
    console_run('dir')
    console_run('ls')
    ```
    """
    if command is None:
        command = info

    if print_info:
        print_log(info)

    param = dict(shell=True)
    if capture_output:
        param |= dict(capture_output=True, text=True)

    return subprocess.run(command, **param)


def input_char(
    prompt=None,
    prompt_ending="",
    newline_after_input=True,
    echo_char=True,
    default=None,
):
    """
    Meminta masukan satu huruf tanpa menekan Enter.

    ```py
    input_char("Input char : ")
    input_char("Input char : ", default='Y')
    input_char("Input Char without print : ", echo_char=False)
    ```
    """
    if prompt:
        print(prompt, end=prompt_ending, flush=True)

    if default is not None:
        a = default
    else:
        a = getch.getche() if echo_char else getch.getch()

    if newline_after_input:
        print()

    if WINDOWS:
        return a.decode()
    if LINUX:
        return a
    raise Exception("Platform tidak didukung.")


def print_dir(var, colorize=True):
    """
    Print property dan method yang tersedia pada variabel

    ```python
    p = pathlib.Path("https://www.google.com/")
    print_dir(p, colorize=False)
    ```
    """
    d = dir(var)
    m = max(len(i) for i in d)
    for i in d:
        try:
            a = getattr(var, i)
            r = a() if callable(a) else a
            if colorize:
                color = colorama.Fore.GREEN
                if is_empty(r):
                    color = colorama.Fore.LIGHTRED_EX
                if i.startswith("__"):
                    color = colorama.Fore.CYAN
                print_colorize(f"{i: >{m}}", text_end=" : ", color=color)
                print(r)
            else:
                print(f"{i: >{m}} : {r}")
        except Exception:
            pass


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
