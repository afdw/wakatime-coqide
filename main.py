import json
import subprocess
import psutil
import inspect

def run(pid, code):
    return subprocess.run(["gdb", "-q", "-p", str(pid)], input=f"""set $h = (void *) dlopen("/usr/lib/libpython3.so", 0x00001 | 0x00100)
print ((void (*)()) dlsym($h, "Py_Initialize"))()
print ((void (*)(char *)) dlsym($h, "PyRun_SimpleString"))({json.dumps(code)})
# print ((void (*)()) dlsym($h, "Py_FinalizeEx"))()
print (int) dlclose($h)""".encode("utf-8"), stdout=subprocess.DEVNULL)

def inner():
    import subprocess
    import time
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkSource", "3.0")
    from gi.repository import Gtk, GtkSource

    global last_time
    last_time = 0

    def scan_for_source_view(name, widgets):
        for widget in widgets:
            if isinstance(widget, GtkSource.View):
                # print(f"-> {name} {widget}")
                if not hasattr(widget, "listening-0.0.1"):
                    setattr(widget, "listening-0.0.1", True)
                    def handler(*_):
                        global last_time
                        if time.time() - last_time > 0.3:
                            subprocess.Popen(["wakatime-cli", "--plugin", "coqide/0.0.1", "--language", "Coq", "--write", "--project", "Unknown Coq project", "--entity-type", "app", "--entity", f"coq://{name}"])
                            last_time = time.time()
                    widget.connect("event", handler)
                # else:
                #     print("--> Already listening")
            elif isinstance(widget, Gtk.Container):
                scan_for_source_view(name, Gtk.Container.get_children(widget))

    def scan_for_notebook(widgets):
        for widget in widgets:
            if isinstance(widget, Gtk.Notebook):
                for i in range(widget.get_n_pages()):
                    child = widget.get_nth_page(i)
                    scan_for_source_view(Gtk.Container.get_children(widget.get_tab_label(child))[1].get_text(), child)
            elif isinstance(widget, Gtk.Container):
                scan_for_notebook(Gtk.Container.get_children(widget))

    scan_for_notebook(Gtk.Window.list_toplevels())

for proc in psutil.process_iter():
    if proc.name().endswith("coqide"):
        print(proc)
        run(proc.pid, f"{inspect.getsource(inner)}\ninner()")
