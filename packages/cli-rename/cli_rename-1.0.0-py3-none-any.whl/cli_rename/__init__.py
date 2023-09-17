

def main():
    import os
    from .app import RenameApp

    pwd = os.getcwd()
    app = RenameApp(pwd=pwd)
    app.run()