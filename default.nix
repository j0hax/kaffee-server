{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication {
  pname = "Kaffeesystem";
  src = ./.;
  version = "0.1";
  propagatedBuildInputs = with pkgs.python3Packages; [ flask flask-cors ];
}
