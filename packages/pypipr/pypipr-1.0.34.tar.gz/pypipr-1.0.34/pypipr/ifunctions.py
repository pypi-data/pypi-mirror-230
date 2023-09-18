"""
Improved functions untuk mempermudah penggunaan
"""


from .lib import *
from .uncategorize import *


def iscandir(
    folder_name=".",
    glob_pattern="*",
    recursive=True,
    scan_file=True,
    scan_folder=True,
):
    """
    Mempermudah scandir untuk mengumpulkan folder dan file.

    ```python
    print(iscandir())
    print(list(iscandir("./", recursive=False, scan_file=False)))
    ```
    """
    path_obj = pathlib.Path(folder_name)
    if recursive:
        path_obj = path_obj.rglob(glob_pattern)
    else:
        path_obj = path_obj.glob(glob_pattern)

    for i in path_obj:
        if scan_folder and i.is_dir():
            yield i
        if scan_file and i.is_file():
            yield i


def irange(start, finish, step=1):
    """
    Meningkatkan fungsi range() dari python untuk pengulangan menggunakan huruf

    ```python
    print(irange('a', 'c'))
    print(irange('z', 'a', 10))
    print(list(irange('a', 'z', 10)))
    print(list(irange(1, '7')))
    print(list(irange(10, 5)))
    ```
    """

    def casting_class():
        start_int = isinstance(start, int)
        finish_int = isinstance(finish, int)
        start_str = isinstance(start, str)
        finish_str = isinstance(finish, str)
        start_numeric = start.isnumeric() if start_str else False
        finish_numeric = finish.isnumeric() if finish_str else False

        if start_numeric and finish_numeric:
            # irange("1", "5")
            return (int, str)

        if (start_numeric or start_int) and (finish_numeric or finish_int):
            # irange("1", "5")
            # irange("1", 5)
            # irange(1, "5")
            # irange(1, 5)
            return (int, int)

        if start_str and finish_str:
            # irange("a", "z")
            # irange("p", "g")
            return (ord, chr)

        """
        kedua if dibawah ini sudah bisa berjalan secara logika, tetapi
        perlu dimanipulasi supaya variabel start dan finish bisa diubah.
        """
        # irange(1, 'a') -> irange('1', 'a')
        # irange(1, '5') -> irange(1, 5)
        # irange('1', 5) -> irange(1, 5)
        # irange('a', 5) -> irange('a', '5')
        #
        # if start_str and finish_int:
        #     # irange("a", 5) -> irange("a", "5")
        #     finish = str(finish)
        #     return (ord, chr)
        #
        # if start_int and finish_str:
        #     # irange(1, "g") -> irange("1", "g")
        #     start = str(start)
        #     return (ord, chr)

        raise Exception(f"[{start} - {finish}] tidak dapat diidentifikasi kesamaannya")

    counter_class, converter_class = casting_class()
    start = counter_class(start)
    finish = counter_class(finish)

    step = 1 if is_empty(step) else int(step)

    faktor = 1 if finish > start else -1
    step *= faktor
    finish += faktor

    for i in range(start, finish, step):
        yield converter_class(i)


def iexec(python_syntax, import_pypipr=True):
    """
    improve exec() python function untuk mendapatkan outputnya

    ```python
    print(iexec('print(9*9)'))
    ```
    """
    if import_pypipr:
        python_syntax = f"from pypipr.pypipr import *\n\n{python_syntax}"

    stdout_backup = sys.stdout

    sys.stdout = io.StringIO()
    exec(python_syntax)
    output = sys.stdout.getvalue()

    sys.stdout = stdout_backup

    return output


def iopen(path, data=None, regex=None, css_select=None, xpath=None, file_append=False):
    """
    Membaca atau Tulis pada path yang bisa merupakan FILE maupun URL.

    Baca File :
    - Membaca seluruh file.
    - Jika berhasil content dapat diparse dengan regex.
    - Apabila File berupa html, dapat diparse dengan css atau xpath.

    Tulis File :
    - Menulis pada file.
    - Jika file tidak ada maka akan dibuat.
    - Jika file memiliki content maka akan di overwrite.

    Membaca URL :
    - Mengakses URL dan mengembalikan isi html nya berupa teks.
    - Content dapat diparse dengan regex, css atau xpath.

    Tulis URL :
    - Mengirimkan data dengan metode POST ke url.
    - Jika berhasil dan response memiliki content, maka dapat diparse
      dengan regex, css atau xpath.


    ```python
    # FILE
    print(iopen("__iopen.txt", "mana aja"))
    print(iopen("__iopen.txt", regex="(\w+)"))
    # URL
    print(iopen("https://www.google.com/", css_select="a"))
    print(iopen("https://www.google.com/", dict(coba="dulu"), xpath="//a"))
    ```
    """
    path = to_str(path)
    content = ""

    if is_valid_url(path):
        req = dict(
            url=path,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"
            },
        )

        if data:
            req["data"] = urllib.parse.urlencode(data).encode()

        req = urllib.request.Request(**req)

        # Connect to URL
        try:
            with urllib.request.urlopen(req) as url_open:
                content = url_open.read().decode()
        except Exception:
            # print(f"An error occurred: {str(e)}")
            return False

    else:
        # Write File
        if data is not None:
            mode = "a" if file_append else "w"
            with open(path, mode, encoding="utf-8") as f:
                content = f.write(data)
        # Read File
        else:
            try:
                with open(path, "r") as f:
                    content = f.read()
            except Exception:
                # print(f"An error occurred: {str(e)}")
                return False

    """ Parse """
    if regex:
        return re.findall(regex, content)
    if css_select:
        return lxml.html.fromstring(content).cssselect(css_select)
    if xpath:
        return lxml.html.fromstring(content).xpath(xpath)

    """ Return """
    return content


def isplit(text, separator="", include_separator=False):
    """
    Memecah text menjadi list berdasarkan separator.

    ```python
    t = '/ini/contoh/path/'
    print(isplit(t, separator='/'))
    ```
    """
    if include_separator:
        separator = f"({separator})"

    result = re.split(separator, text, flags=re.IGNORECASE | re.MULTILINE)

    return result


def ijoin(
    iterable,
    separator="",
    start="",
    end="",
    remove_empty=False,
    recursive=True,
    recursive_flat=False,
    str_strip=False,
):
    """
    Simplify Python join functions like PHP function.
    Iterable bisa berupa sets, tuple, list, dictionary.

    ```python
    arr = {'asd','dfs','weq','qweqw'}
    print(ijoin(arr, ', '))

    arr = '/ini/path/seperti/url/'.split('/')
    print(ijoin(arr, ','))
    print(ijoin(arr, ',', remove_empty=True))

    arr = {'a':'satu', 'b':(12, 34, 56), 'c':'tiga', 'd':'empat'}
    print(ijoin(arr, separator='</li>\\n<li>', start='<li>', end='</li>', recursive_flat=True))
    print(ijoin(arr, separator='</div>\\n<div>', start='<div>', end='</div>'))
    print(ijoin(10, ' '))
    ```
    """
    if not is_iterable(iterable):
        iterable = [iterable]

    separator = to_str(separator)

    if isinstance(iterable, dict):
        iterable = iterable.values()

    if remove_empty:
        # iterable = (i for i in filter_empty(iterable))
        iterable = filter_empty(iterable)

    if recursive:
        rec_flat = dict(start=start, end=end)
        if recursive_flat:
            rec_flat = dict(start="", end="")

        def rec(x):
            return ijoin(
                iterable=x,
                separator=separator,
                **rec_flat,
                remove_empty=remove_empty,
                recursive=recursive,
                recursive_flat=recursive_flat,
            )

        iterable = ((rec(i) if is_iterable(i) else i) for i in iterable)

    # iterable = (str(i) for i in iterable)
    iterable = map(str, iterable)

    if str_strip:
        # iterable = (i.strip() for i in iterable)
        iterable = map(str.strip, iterable)

    result = start

    for index, value in enumerate(iterable):
        if index:
            result += separator
        result += value

    result += end

    return result


def ireplace(
    string: str,
    replacements: dict,
    flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
):
    """
    STRing TRanslate mengubah string menggunakan kamus dari dict.
    Replacement dapat berupa text biasa ataupun regex pattern.
    Apabila replacement berupa regex, gunakan raw string `r"..."`
    Untuk regex capturing gunakan `(...)`, dan untuk mengaksesnya
    gunakan `\\1`, `\\2`, .., dst.

    ```python
    text = 'aku ini mau ke sini'
    replacements = {
        "sini": "situ",
        r"(ini)": r"itu dan \\1",
    }
    print(ireplace(text, replacements))
    ```
    """
    for i, v in replacements.items():
        string = re.sub(i, v, string, flags=flags)
    return string


def idumps(data, syntax="yaml", indent=4):
    """
    Mengubah variabel data menjadi string untuk yang dapat dibaca untuk disimpan.
    String yang dihasilkan berbentuk syntax YAML/JSON/HTML.

    ```python
    data = {
        'a': 123,
        't': ['disini', 'senang', 'disana', 'senang'],
        'l': (12, 23, [12, 42]),
    }
    print(idumps(data))
    print(idumps(data, syntax='html'))
    ```
    """
    if syntax == "yaml":
        return yaml.dump(data, indent=indent)
    if syntax == "json":
        return json.dumps(data, indent=indent)
    if syntax == "html":
        return idumps_html(data, indent=indent)
    raise Exception(f"Syntax tidak didukung {syntax}")


def iloads(data, syntax="yaml"):
    """
    Mengubah string data hasil dari idumps menjadi variabel.
    String data adalah berupa syntax YAML.

    ```python
    data = {
        'a': 123,
        't': ['disini', 'senang', 'disana', 'senang'],
        'l': (12, 23, [12, 42])
    }
    s = idumps(data)
    print(iloads(s))
    ```
    """
    if syntax == "yaml":
        return yaml.safe_load(data)
    if syntax == "json":
        return json.load(data)
    if syntax == "html":
        return iloads_html(data)
    raise Exception(f"Syntax tidak didukung {syntax}")


def idumps_html(data, indent=None):
    """
    Serialisasi python variabel menjadi HTML.
    ```
    List -> <ul>...</ul>
    Dict -> <table>...</table>
    ```

    ```python
    data = {
        'abc': 123,
        'list': [1, 2, 3, 4, 5],
        'dict': {'a': 1, 'b':2, 'c':3},
    }
    print(idumps_html(data))
    ```
    """

    def to_ul(data):
        ul = lxml.etree.Element("ul")
        for i in data:
            li = lxml.etree.SubElement(ul, "li")
            li.append(to_html(i))
        return ul

    def to_table(data: dict):
        table = lxml.etree.Element("table")
        tbody = lxml.etree.SubElement(table, "tbody")
        for i, v in data.items():
            tr = lxml.etree.SubElement(tbody, "tr")
            th = lxml.etree.SubElement(tr, "th")
            th.text = str(i)
            td = lxml.etree.SubElement(tr, "td")
            td.append(to_html(v))
        return table

    def to_text(data):
        span = lxml.etree.Element("span")
        span.text = str(data)
        return span

    def to_html(data):
        struct = {
            dict: to_table,
            list: to_ul,
            tuple: to_ul,
            set: to_ul,
        }
        return struct.get(type(data), to_text)(data)

    html = to_html(data)
    if indent:
        lxml.etree.indent(html, space=" " * indent)
    return lxml.etree.tostring(html, pretty_print=True, encoding="unicode")


def iloads_html(html):
    """
    Mengambil data yang berupa list `<ul>`, dan table `<table>` dari html
    dan menjadikannya data python berupa list.
    setiap data yang ditemukan akan dibungkus dengan tuple sebagai separator.
    ```
    list (<ul>)     -> list         -> list satu dimensi
    table (<table>) -> list[list]   -> list satu dimensi didalam list
    ```
    apabila data berupa ul maka dapat dicek type(data) -> html_ul
    apabila data berupa ol maka dapat dicek type(data) -> html_ol
    apabila data berupa dl maka dapat dicek type(data) -> html_dl
    apabila data berupa table maka dapat dicek type(data) -> html_table

    ```python
    pprint.pprint(iloads_html(iopen("https://harga-emas.org/")), depth=10)
    pprint.pprint(iloads_html(iopen("https://harga-emas.org/1-gram/")), depth=10)
    ```
    """

    def xpath(e, x):
        """
        Fungsi ini sangat krusial/menentukan. Fungsi ini dibuat
        supaya xpath yang diberikan diproses dari element saat ini.
        Sedangkan xpath pada element lxml akan mengecek syntax xpath dari
        root paling awal document.
        """
        if not isinstance(e, str):
            e = lxml.html.tostring(e, encoding="unicode")
        e = lxml.html.fromstring(e)
        return (e, e.xpath(x))

    def parse(e):
        parser = {
            "ul": parse_ul,
            "ol": parse_ol,
            "dl": parse_dl,
            "table": parse_table,
        }
        try:
            return parser[e.tag.lower()](e)
        except Exception:
            raise Exception("Tidak ditemukan parse fungsi untuk element : ", e)

    def parse_list(ul):
        """
        Simple parse html list.
        """
        result = []
        _, li = xpath(ul, "li")
        for i in li:
            u = iloads_html(i)
            t = i.text.strip() if i.text else ""
            if t and t != u:
                result.append({t: u})
            else:
                result.append(u)
        return result

    def parse_ul(ul):
        return html_ul(parse_list(ul))

    def parse_ol(ol):
        return html_ol(parse_list(ol))

    def parse_dl(dl):
        """
        Simple parse dl-dt-dd.
        """
        result = html_dl()
        _, di = xpath(dl, "dt|dd")
        d = iter(di)
        try:
            while True:
                i = next(d)
                k = i.tag.lower()
                v = iloads_html(i)
                if k == "dt":
                    result.append(["", []])
                    result[-1][0] = v
                elif k == "dd":
                    result[-1][-1].append(v)
        except Exception:
            pass

        return result

    def parse_table(table):
        """
        Mengambil children tr dari table.
        tr diambil dari thead atau tbody atau langsung tr.
        tr dari thead atau tbody akan dianggap sama.
        """
        result = html_table()
        _, tr = xpath(table, "//tr[not(ancestor::tr)]")
        for itr in tr:
            d = []
            _, td = xpath(itr, "th|td")
            for itd in td:
                d.append(iloads_html(itd))
            result.append(d.copy())
        return result

    def text_content(e):
        """
        mengambil semua text dalam element secara recursive.
        karena tidak ditemukan data dalam element.
        """
        return ijoin(e.itertext(), str_strip=True)

    element, childs = xpath(
        html,
        "//*[self::ul | self::ol | self::dl | self::table][not(ancestor::ul | ancestor::ol | ancestor::dl | ancestor::table)]",
    )
    if childs:
        return tuple((parse(data) for data in childs))
    else:
        return text_content(element)


class html_ul(list):
    """
    Class ini digunakan untuk idumps dan iloads html
    """

    pass


class html_ol(list):
    """
    Class ini digunakan untuk idumps dan iloads html
    """

    pass


class html_dl(list):
    """
    Class ini digunakan untuk idumps dan iloads html
    """

    pass


class html_table(list):
    """
    Class ini digunakan untuk idumps dan iloads html
    """

    pass


def iprint(
    *args,
    color=None,
    sort_dicts=False,
    **kwargs,
):
    """
    Improve print function dengan menambahkan color dan pretty print
    Color menggunakan colorama Fore + Back + Style

    ```python
    iprint('yang ini', {'12':12,'sdsd':{'12':21,'as':[88]}}, color=colorama.Fore.BLUE + colorama.Style.BRIGHT)
    ```
    """

    r = []
    for i in args:
        if is_iterable(i) and not isinstance(i, (list, set, dict, tuple)):
            i = list(i)

        if not isinstance(i, str):
            i = pprint.pformat(i, depth=math.inf, sort_dicts=sort_dicts)

        if color:
            i = color + i + colorama.Style.RESET_ALL

        r.append(i)

    print(*r, **kwargs)


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
