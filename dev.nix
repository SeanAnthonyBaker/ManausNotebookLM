{ pkgs, ... }: {
  # Which nixpkgs channel to use
  channel = "stable-23.11";

  # System packages needed for the project
  packages = [
    # Python and pip
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv

    # Docker and container tools
    pkgs.docker
    pkgs.docker-compose

    # System utilities
    pkgs.curl
    pkgs.wget
    pkgs.git
    pkgs.bash
    pkgs.coreutils
    pkgs.findutils
    pkgs.gnugrep
    pkgs.gnused
    pkgs.gawk

    # Network tools
    pkgs.nettools
    pkgs.iproute2

    # Text editors and development tools
    pkgs.nano
    pkgs.vim

    # Process management
    pkgs.procps
    pkgs.psmisc
  ];

  # Environment variables
  env = {
    FLASK_ENV = "development";
    PYTHONPATH = "/workspace/notebooklm-automation";
    DOCKER_HOST = "unix:///var/run/docker.sock";
    COMPOSE_PROJECT_NAME = "notebooklm-automation";
  };

  # VS Code extensions for development
  idx.extensions = [
    "ms-python.python"
    "ms-python.flake8"
    "ms-python.black-formatter"
    "ms-azuretools.vscode-docker"
    "bradlc.vscode-tailwindcss"
    "esbenp.prettier-vscode"
  ];

  # Preview configuration for the Flask app
  # When using docker-compose, Firebase Studio should ideally detect exposed ports automatically.
  # The 'command' here is typically for applications run directly by Nix, not Docker.
  idx.previews = {
    enable = true;
    previews = {
      web = {
        # No 'command' here, rely on Docker Compose
        manager = "web";
      };
    };
  };

  # Workspace configuration
  idx.workspace = {
    onCreate = {
      # Install Python dependencies - This might be redundant if Dockerfile handles it, but keeping for safety.
      install-deps = "cd /workspace/notebooklm-automation && python -m pip install -r requirements.txt";

      # Make scripts executable
      make-executable = "cd /workspace/notebooklm-automation && chmod +x start.sh stop.sh";

      # Create environment file from example
      setup-env = "cd /workspace/notebooklm-automation && cp .env.example .env";
    };

    onStart = {
      # Pull required Docker images
      pull-images = "cd /workspace/notebooklm-automation && docker-compose pull || true";
      # Start Docker Compose services
      start-docker-services = "cd /workspace/notebooklm-automation && docker-compose up -d";
    };
  };

  # Services configuration
  services = {
    docker = {
      enable = true;
    };
  };
}
