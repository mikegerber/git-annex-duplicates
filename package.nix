{ pkgs }:

let
  inherit (pkgs) lib;

  pyproject-nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/pyproject.nix.git";
    rev = "489adad94b0360044ae9b16f5265925f73d439f0";
  };

  uv2nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/uv2nix.git";
    rev = "c361746c7d630d98b972378290547c8d35542a7a";
  };

  build-system-pkgs-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/build-system-pkgs.git";
    rev = "a17819c85163988e063806ffc4f6d2716bc8ead8";
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


  src = lib.cleanSource ./.;

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
