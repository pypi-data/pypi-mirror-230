import os


def copy_package(src_dir, dest_dir):
    package = os.path.basename(src_dir)
    test_package = os.path.basename(dest_dir)
    for root, _, files in os.walk(src_dir):
        for filename in files:
            src_file = os.path.join(root, filename)
            rel_path = os.path.relpath(src_dir, root)
            dest_file = os.path.join(dest_dir, rel_path, filename)
            with open(src_file) as source:
                with open(dest_file, 'w') as destination:
                    for line in source.readlines():
                        destination.write(line.replace(package, test_package))
