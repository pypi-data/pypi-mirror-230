# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? (import
    (fetchTarball {
      url = "https://github.com/ppentchev/nixpkgs/archive/5f8fab6d7bd321cf6dda996c4041a7c41bb65570.tar.gz";
      sha256 = "1q491k72mfkwy2blmmgk63jgqjjiha6al3vpn4j7x6yg8zmxgqzf";
    })
    { })
, py-ver ? 311
}:
let
  python-name = "python${toString py-ver}";
  python = builtins.getAttr python-name pkgs;
  python-pkgs = python.withPackages (p: with p; [
    click
    typedload

    pytest
  ] ++ pkgs.lib.optionals (python.pythonOlder "3.11") [ tomli ]);
in
pkgs.mkShell {
  buildInputs = [ python-pkgs ];
  shellHook = ''
    set -e
    PYTHONPATH="$(pwd)/python" python3 -m pytest -v python/tests
    exit
  '';
}
