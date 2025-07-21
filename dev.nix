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
  idx.previews = {
    enable = true;
    previews = {
      web = {
        command = [
          "python"
          "src/main.py"
        ];
        manager = "web";
        env = {
          PORT = "$PORT";
          FLASK_ENV = "development";
        };
      };
    };
  };

  # Workspace configuration
  idx.workspace = {
    onCreate = {
      # Install Python dependencies
      install-deps = "cd /workspace/notebooklm-automation && python -m pip install -r requirements.txt";
      
      # Make scripts executable
      make-executable = "cd /workspace/notebooklm-automation && chmod +x start.sh stop.sh";
      
      # Create environment file from example
      setup-env = "cd /workspace/notebooklm-automation && cp .env.example .env";
    };
    
    onStart = {
      # Start Docker daemon (if not already running)
      start-docker = "sudo service docker start || true";
      
      # Pull required Docker images
      pull-images = "cd /workspace/notebooklm-automation && docker-compose pull || true";
    };
  };

  # Services configuration
  services = {
    docker = {
      enable = true;
    };
  };
}

