
CMake with call-tree
====================

This is fork of CMake, with a small number of changes to produce some
extra files when running CMake to configure a project::

  cmake.functions.tree
  cmake.files.tree
  cmake.tree
  cmake.trace.json

The file ``cmake.trace.json`` look like::

    ...
    [ "enter", "include", "/tmp/simple1/src/functions.cmake" ],
    [ "leave", "include", "/tmp/simple1/src/functions.cmake" ],
    [ "enter", "add_subdirectory", "/tmp/simple1/src/subdirA" ],
    [ "enter", "function", "some_fun" ],
    [ "enter", "macro", "some_macro" ],
    [ "leave", "macro", "some_macro" ],
    [ "leave", "function", "some_fun" ],
    [ "enter", "macro", "some_macro" ],
    [ "leave", "macro", "some_macro" ],
    [ "leave", "add_subdirectory", "/tmp/simple1/src/subdirA" ],
    [ "enter", "add_subdirectory", "/tmp/simple1/src/subdirB" ],
    [ "enter", "macro", "some_macro" ],
    [ "leave", "macro", "some_macro" ],
    [ "leave", "add_subdirectory", "/tmp/simple1/src/subdirB" ]
  ]

It records these "events" when running CMake:

- entering/leaving a sub-directory

- entering/leaving an included file

- entering/leaving a function

- entering/leaving a macro

From this information a `call_tree.pdf <examples/simple1/call_tree.pdf>`_ can be constructed (e.g. by a Python script).
A simple "ascii tree" is produced directly by the patched CMake::

  /tmp/simple1/src/functions.cmake
  /tmp/simple1/src/subdirA
  .   some_fun
  .   .   some_macro
  .   some_macro
  /tmp/simple1/src/subdirB
  .   some_macro
    

Building this patched CMake
---------------------------

::

  git clone https://github.com/holmberg556/CMake-admin.git
  cd CMake-admin
  python3 build.py call-tree--v3.26.3

If you want to see which commands would be executed, you can "dry-run" first::

  python3 build.py -n call-tree--v3.26.3

This should produce something like the following files (example on macOS)::

  $ ls -1 ../CMake.build
  ../CMake.build/cmake-3.21.1-g1aa8953-Darwin-x86_64.sh
  ../CMake.build/cmake-3.21.1-g1aa8953-Darwin-x86_64.tar.gz

There should also be a fully functional CMake installed in the directory ``../CMake.install``.

Update fork for new CMake release
---------------------------------

First "Sync fork" in the Github web interface.
Then do this to transfer tags too::

  git clone git@github.com:holmberg556/CMake.git
  cd CMake
  git remote add upstream https://gitlab.kitware.com/cmake/cmake
  git fetch upstream
  git push --tags origin

Now it is time to rebase our branch::

  git checkout call-tree--v3.25.2         # previous branch
  git checkout -b call-tree--v3.26.3      # the new branch, starting at same place
  git rebase git rebase v3.26.3           # rebase on new release
  git push
