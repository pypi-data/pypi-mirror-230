from __future__ import annotations

import os
import pathlib
import re
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

from seeq.base import system
from seeq.base.system import human_readable_byte_count


@pytest.mark.unit
def test_human_readable_byte_count_base_ten():
    '''
    Make sure we get the same results as SystemInfoTest#testHumanReadableByteCountBaseTen
    '''
    assert human_readable_byte_count(0, False, False) == '0 B'
    assert human_readable_byte_count(10, False, False) == '10 B'
    assert human_readable_byte_count(900, False, False) == '900 B'
    assert human_readable_byte_count(999, False, False) == '999 B'

    assert human_readable_byte_count(1000, False, False) == '1.00 KB'
    assert human_readable_byte_count(2000, False, False) == '2.00 KB'
    assert human_readable_byte_count(1000 * 1000 - 10, False, False) == '999.99 KB'

    assert human_readable_byte_count(1000 * 1000, False, False) == '1.00 MB'
    assert human_readable_byte_count(50 * 1000 * 1000, False, False) == '50.00 MB'
    assert human_readable_byte_count(1000 * 1000 * 1000 - 10000, False, False) == '999.99 MB'

    assert human_readable_byte_count(1000 * 1000 * 1000, False, False) == '1.00 GB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000, False, False) == '50.00 GB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 - 10000000, False, False) == '999.99 GB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000, False, False) == '1.00 TB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 TB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 - 1e10, False, False) == '999.99 TB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 PB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 PB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e13, False, False) == '999.99 PB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 EB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 EB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e16, False, False) == '999.99 EB'


@pytest.mark.unit
def test_spawn_list_args():
    """
    Spawns process which writes each argument in argv to a JSON file.
    That file is read back and verified that all arguments were correctly preserved.
    """
    import json

    script = textwrap.dedent(r'''
        import json, os, sys
        with open(os.getenv('_TEST_FILE_'), 'w') as f:
            json.dump(sys.argv[1:], f)
    ''')

    args = ['foo', 'Giving "NIFTY" quotes', 'Making $dollars and', ' taking\na %percent%(!) ']
    with tempfile.TemporaryDirectory() as temp:
        out_file = os.path.join(temp, f'received args.json')
        system.spawn(['python', '-c', script, *args], env={**os.environ, '_TEST_FILE_': str(out_file)})

        with open(out_file, 'r') as f:
            loaded = json.load(f)

        assert loaded == args


@pytest.mark.unit
def test_spawn_generator_args():
    """Tests that arguments from a lazy generator are interpreted correctly."""

    def get_args():
        yield sys.executable
        yield from ('-c', 'print("Hello, world")')

    ret, out, err = system.spawn(get_args(), capture_output=True)
    assert ret == 0
    assert out == 'Hello, world' + os.linesep
    assert not err


@pytest.mark.unit
def test_path_to_regex():
    path_rep1 = r'C:\Foo Bar\Baz.exe'
    path_rep2 = r'\\?\C:\Foo Bar\Baz.exe'
    path_rep3 = r'/C/Foo Bar/Baz.exe'
    # Some things mix up their path separators :(
    path_rep4 = r'C:\Foo Bar/Baz.exe'

    rx = system.path_to_regex(path_rep1)

    # Matches original input
    assert re.fullmatch(rx, path_rep1)

    # Agnostic to the drive letter or path-separator representations.
    for rep in (path_rep2, path_rep3, path_rep4):
        assert rx == system.path_to_regex(rep)
        assert re.fullmatch(rx, rep)

    # …but not blind to the drive letter itself.
    path_rep1_bad_drive = path_rep1.replace('C', 'D')
    assert rx != system.path_to_regex(path_rep1_bad_drive)
    assert not re.match(rx, path_rep1_bad_drive)

    # Does not misinterpret regex characters
    assert not re.match(rx, path_rep1.replace('.exe', '-exe'))
    assert re.match(system.path_to_regex(r'C:\Foo$Thing'), r'C:\Foo$Thing')
    assert not re.match(system.path_to_regex(r'C:\Foo*Bar'), r'C:\FoooBar')

    # …including things like backslash escapes.
    # (We have a single backslash before 'old', are checking that the `\n` is not interpreted as a newline).
    assert re.match(system.path_to_regex(r'Foo\old'), 'Foo\\old', re.MULTILINE)
    assert not re.match(system.path_to_regex(r'Foo\new'), 'Foo\new', re.MULTILINE)
    assert not re.match(system.path_to_regex(r'Foo\new'), 'Foo\\\new', re.MULTILINE)


@pytest.mark.unit
def test_path_to_regex_pathlikes():
    win_str = r'C:\Foo Bar\Baz.exe'
    assert system.path_to_regex(pathlib.PureWindowsPath(win_str)) == system.path_to_regex(win_str)

    nix_str = '/usr/local/bin/baz qux.sh'
    assert system.path_to_regex(pathlib.PurePosixPath(nix_str)) == system.path_to_regex(nix_str)


@pytest.mark.unit
def test_replace_in_file():
    with tempfile.TemporaryDirectory() as temp:
        service_file = os.path.join(temp, f'bogus.service')
        if not os.path.exists(service_file):
            with open(service_file, 'w') as f:
                f.write(textwrap.dedent(f"""
                    [Service]
                    Type=simple
                    User=mark
                    ExecStart=/opt/seeq/seeq start --from-service
                    ExecStop=/opt/seeq/seeq stop
                    Restart=on-failure

                    [Install]
                    WantedBy=multi-user.target
                """))

        system.replace_in_file(service_file, [
            (r'User=.*', 'User=alan'),
            (r'ExecStart=.*', 'ExecStart=/stuff/seeq start --from-service'),
            (r'ExecStop=.*', 'ExecStop=/stuff/seeq stop')
        ])

        with open(service_file, 'r') as f:
            content = f.read()
            assert 'User=alan' in content
            assert 'ExecStart=/stuff/seeq start --from-service' in content
            assert 'ExecStop=/stuff/seeq stop' in content


@pytest.mark.unit
def test_copy_tree_exclude_folder_relative_path():
    # It was discovered in CRAB-20621 that robocopy's /XD flag to exclude directories wasn't working for relative
    # paths to subdirectories. This tests system#copy_tree to be compatible with non-Windows systems.
    # See https://superuser.com/a/690842 and follow-up comments
    with tempfile.TemporaryDirectory() as src:
        tree = DirectoryTestTree(src)
        with tempfile.TemporaryDirectory() as dest:
            system.copytree(src, dest, exclude=tree.exclude)

            all_root_contents = os.listdir(dest)
            # Destination should only have KeepParent and KeepMe.txt
            assert len(all_root_contents) == 2
            assert str(tree.keep_parent_dir_relative) in all_root_contents
            assert tree.root_keep_file_name in all_root_contents

            # Destination should have only KeepParent/KeepMe subdir
            all_subdirs = os.listdir(dest / tree.keep_parent_dir_relative)
            assert len(all_subdirs) == 1
            assert tree.keep_subdir_name in all_subdirs


@pytest.mark.unit
def test_copytree_destination_excludes(tmp_path: Path):
    src = tmp_path / 'src'
    dst = tmp_path / 'dst'

    src.mkdir()
    (src / 'dir').mkdir()
    (src / 'dir' / 'file.txt').touch()
    (src / 'dir2').mkdir()
    (src / 'dir2' / 'file2.txt').touch()
    (src / 'dir3').mkdir()
    (src / 'dir3' / 'file3.txt').touch()
    (src / 'file4.txt').touch()
    (src / 'file5.txt').touch()
    dst.mkdir()
    (dst / 'important').mkdir()
    (dst / 'important' / 'secrets.txt').touch()
    system.copytree(str(src), str(dst), mirror=True, exclude=['dir', 'important'])
    assert not (dst / 'dir').exists()
    assert not (dst / 'dir' / 'file.txt').exists()
    assert (dst / 'dir2').exists()
    assert (dst / 'dir2' / 'file2.txt').exists()
    assert (dst / 'dir3').exists()
    assert (dst / 'dir3' / 'file3.txt').exists()
    assert (dst / 'file4.txt').exists()
    assert (dst / 'file5.txt').exists()
    assert (dst / 'important').exists()
    assert (dst / 'important' / 'secrets.txt').exists()


@pytest.mark.unit
def test_removetree_keep_top(tmp_path: Path):
    (tmp_path / 'dir').mkdir()
    (tmp_path / 'dir' / 'file.txt').touch()
    (tmp_path / 'file2.txt').touch()
    system.removetree(str(tmp_path), keep_top_folder=True)
    assert not (tmp_path / 'dir').exists()
    assert not (tmp_path / 'dir' / 'file.txt').exists()
    assert not (tmp_path / 'file2.txt').exists()
    assert tmp_path.exists()


@pytest.mark.unit
def test_removetree_with_exclusions(tmp_path: Path):
    (tmp_path / 'dir').mkdir()
    (tmp_path / 'dir' / 'file.txt').touch()
    (tmp_path / 'dir2').mkdir()
    (tmp_path / 'dir2' / 'file2.txt').touch()
    (tmp_path / 'dir3').mkdir()
    (tmp_path / 'dir3' / 'file3.txt').touch()
    (tmp_path / 'file4.txt').touch()
    (tmp_path / 'file5.txt').touch()
    system.removetree(str(tmp_path), exclude_subdirectories=['dir'])
    assert (tmp_path / 'dir').exists()
    assert (tmp_path / 'dir' / 'file.txt').exists()
    assert not (tmp_path / 'dir2').exists()
    assert not (tmp_path / 'dir2' / 'file2.txt').exists()
    assert not (tmp_path / 'dir3').exists()
    assert not (tmp_path / 'dir3' / 'file3.txt').exists()
    assert not (tmp_path / 'file4.txt').exists()
    assert not (tmp_path / 'file5.txt').exists()
    system.removetree(str(tmp_path), exclude_subdirectories=['nonexistant'])
    assert not (tmp_path / 'dir').exists()
    assert not (tmp_path / 'dir' / 'file.txt').exists()
    assert tmp_path.exists()


class DirectoryTestTree():
    def __init__(self, root):
        self.root = root
        self.keep_parent_dir_relative = Path('KeepParent')
        self.keep_subdir_name = 'KeepMe'
        self.exclude_subdir_name = 'ExcludeMe'
        self.exclude_parent_dir_relative = Path('ExcludeParent')

        self.root_keep_file_name = 'KeepMe.txt'
        self.root_exclude_file_name = 'ExcludeMe.txt'

        self.keep_subdir_relative = self.keep_parent_dir_relative / self.keep_subdir_name
        self.exclude_subdir_relative = self.keep_parent_dir_relative / self.exclude_subdir_name

        self.exclude = [str(self.exclude_parent_dir_relative), str(self.exclude_subdir_relative),
                        self.root_exclude_file_name]

        self._create_tree()

    def _create_tree(self):
        # tmpDir
        # |
        # ---- KeepMe.txt
        # -----ExcludeMe.txt
        # ---- ExcludeParent
        # ---- KeepParent
        #          |
        #          ----- KeepMe
        #          |
        #          ----- ExcludeMe
        os.makedirs(self.root / self.keep_subdir_relative)
        os.makedirs(self.root / self.exclude_parent_dir_relative)
        os.makedirs(self.root / self.exclude_subdir_relative)

        open(Path(self.root) / self.root_keep_file_name, 'a').close()
        open(Path(self.root) / self.root_exclude_file_name, 'a').close()
