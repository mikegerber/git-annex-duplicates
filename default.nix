{ pkgs }:

let
  inherit (pkgs) lib;

  pyproject-nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/pyproject.nix.git";
    rev = "1b1485546d85f6f6c7aadb10c4923dbc09633263";
  };

  uv2nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/uv2nix.git";
    rev = "7f9c6b613d2e749e54854b1d60ab6a2192db889e";
  };

  build-system-pkgs-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/build-system-pkgs.git";
    rev = "150839ac67b5a34db56a55e8f6b7099a4e7878ab";
  };

  pyproject-nix = import pyproject-nix-src {
    inherit lib;
  };

  uv2nix = import uv2nix-src {
    inherit lib pyproject-nix;
  };

  pyproject-build-systems = import build-system-pkgs-src {
    inherit lib pyproject-nix uv2nix;
  };


  src = builtins.fetchGit {
    url = "https://cvs.moegen-wir.net/mikegerber/git-annex-duplicates.git";
    rev = "1e8ea44ba8fade7ef396f0fbe65262f023138d05";
  };


  workspace = uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = src;
  };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  python = pkgs.python3;

  pythonSet =
    (pkgs.callPackage pyproject-nix.build.packages {
      inherit python;
    }).overrideScope (
      lib.composeManyExtensions [
        pyproject-build-systems.overlays.default
        overlay
      ]
    );

  venv = pythonSet.mkVirtualEnv
    "git-annex-duplicates-env"
    workspace.deps.default;

  inherit (pkgs.callPackages pyproject-nix.build.util { })
    mkApplication;

in
mkApplication {
  inherit venv;
  package = pythonSet.git-annex-duplicates;
}
