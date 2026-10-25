"""
Package KIYA Piano Studio Pro into clean distribution ZIP archive.
"""
import os
import zipfile

def package():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_zip = os.path.join(root_dir, "KIYA_Piano_Studio_Pro_PSR_S975.zip")

    exclude_dirs = {'.pytest_cache', '__pycache__', '.git', '.idea', '.vscode'}
    exclude_exts = {'.pyc', '.pyo'}

    count = 0
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Prune excluded directories in-place
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            
            for f in filenames:
                if f == "KIYA_Piano_Studio_Pro_PSR_S975.zip":
                    continue
                _, ext = os.path.splitext(f)
                if ext.lower() in exclude_exts:
                    continue

                full_path = os.path.join(dirpath, f)
                rel_path = os.path.relpath(full_path, root_dir)
                zf.write(full_path, rel_path)
                count += 1

    size_kb = os.path.getsize(out_zip) / 1024
    print(f"Packaged {count} files into {out_zip} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    package()
