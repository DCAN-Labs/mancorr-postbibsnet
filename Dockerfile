#This image already has nipype + FSL installed.
#Note: only certain versions of FSL are nipype compatible
#FROM nipype/nipype:py38

#Make a directory to store any of the code we need
#USER root

FROM debian:buster-slim
ENV FSLDIR="/opt/fsl-6.0.4" \
    PATH="/opt/fsl-6.0.4/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.4/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.4/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bc \
           ca-certificates \
           curl \
           dc \
           file \
           libfontconfig1 \
           libfreetype6 \
           libgl1-mesa-dev \
           libgl1-mesa-dri \
           libglu1-mesa-dev \
           libgomp1 \
           libice6 \
           libopenblas-base \
           libxcursor1 \
           libxft2 \
           libxinerama1 \
           libxrandr2 \
           libxrender1 \
           libxt6 \
           nano \
           sudo \
           wget \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Downloading FSL ..." \
    && mkdir -p /opt/fsl-6.0.4 \
    && curl -fL https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.4-centos6_64.tar.gz \
    | tar -xz -C /opt/fsl-6.0.4 --strip-components 1 \
    && echo "Installing FSL conda environment ..." \
    && bash /opt/fsl-6.0.4/etc/fslconf/fslpython_install.sh -f /opt/fsl-6.0.4
ENV CONDA_DIR="/opt/miniconda-latest" \
    PATH="/opt/miniconda-latest/bin:$PATH"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bzip2 \
           ca-certificates \
           curl \
    && rm -rf /var/lib/apt/lists/* \
    # Install dependencies.
    && export PATH="/opt/miniconda-latest/bin:$PATH" \
    && echo "Downloading Miniconda installer ..." \
    && conda_installer="/tmp/miniconda.sh" \
    && curl -fsSL -o "$conda_installer" https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash "$conda_installer" -b -p /opt/miniconda-latest \
    && rm -f "$conda_installer" \
    && conda update -yq -nbase conda \
    # Prefer packages in conda-forge
    && conda config --system --prepend channels conda-forge \
    # Packages in lower-priority channels not considered if a package with the same
    # name exists in a higher priority channel. Can dramatically speed up installations.
    # Conda recommends this as a default
    # https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html
    && conda config --set channel_priority strict \
    && conda config --system --set auto_update_conda false \
    && conda config --system --set show_channel_urls true \
    # Enable `conda activate`
    && conda init bash \
    && conda install -y  --name base \
           "nipype" \
    # Clean up
    && sync && conda clean --all --yes && sync \
    && rm -rf ~/.cache/pip/*

# Save specification to JSON.
RUN printf '{ \
  "pkg_manager": "apt", \
  "existing_users": [ \
    "root" \
  ], \
  "instructions": [ \
    { \
      "name": "from_", \
      "kwds": { \
        "base_image": "debian:buster-slim" \
      } \
    }, \
    { \
      "name": "env", \
      "kwds": { \
        "FSLDIR": "/opt/fsl-6.0.4", \
        "PATH": "/opt/fsl-6.0.4/bin:$PATH", \
        "FSLOUTPUTTYPE": "NIFTI_GZ", \
        "FSLMULTIFILEQUIT": "TRUE", \
        "FSLTCLSH": "/opt/fsl-6.0.4/bin/fsltclsh", \
        "FSLWISH": "/opt/fsl-6.0.4/bin/fslwish", \
        "FSLLOCKDIR": "", \
        "FSLMACHINELIST": "", \
        "FSLREMOTECALL": "", \
        "FSLGECUDAQ": "cuda.q" \
      } \
    }, \
    { \
      "name": "run", \
      "kwds": { \
        "command": "apt-get update -qq\\napt-get install -y -q --no-install-recommends \\\\\\n    bc \\\\\\n    ca-certificates \\\\\\n    curl \\\\\\n    dc \\\\\\n    file \\\\\\n    libfontconfig1 \\\\\\n    libfreetype6 \\\\\\n    libgl1-mesa-dev \\\\\\n    libgl1-mesa-dri \\\\\\n    libglu1-mesa-dev \\\\\\n    libgomp1 \\\\\\n    libice6 \\\\\\n    libopenblas-base \\\\\\n    libxcursor1 \\\\\\n    libxft2 \\\\\\n    libxinerama1 \\\\\\n    libxrandr2 \\\\\\n    libxrender1 \\\\\\n    libxt6 \\\\\\n    nano \\\\\\n    sudo \\\\\\n    wget\\nrm -rf /var/lib/apt/lists/*\\necho \\"Downloading FSL ...\\"\\nmkdir -p /opt/fsl-6.0.4\\ncurl -fL https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.4-centos6_64.tar.gz \\\\\\n| tar -xz -C /opt/fsl-6.0.4 --strip-components 1 \\necho \\"Installing FSL conda environment ...\\"\\nbash /opt/fsl-6.0.4/etc/fslconf/fslpython_install.sh -f /opt/fsl-6.0.4" \
      } \
    }, \
    { \
      "name": "env", \
      "kwds": { \
        "CONDA_DIR": "/opt/miniconda-latest", \
        "PATH": "/opt/miniconda-latest/bin:$PATH" \
      } \
    }, \
    { \
      "name": "run", \
      "kwds": { \
        "command": "apt-get update -qq\\napt-get install -y -q --no-install-recommends \\\\\\n    bzip2 \\\\\\n    ca-certificates \\\\\\n    curl\\nrm -rf /var/lib/apt/lists/*\\n# Install dependencies.\\nexport PATH=\\"/opt/miniconda-latest/bin:$PATH\\"\\necho \\"Downloading Miniconda installer ...\\"\\nconda_installer=\\"/tmp/miniconda.sh\\"\\ncurl -fsSL -o \\"$conda_installer\\" https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh\\nbash \\"$conda_installer\\" -b -p /opt/miniconda-latest\\nrm -f \\"$conda_installer\\"\\nconda update -yq -nbase conda\\n# Prefer packages in conda-forge\\nconda config --system --prepend channels conda-forge\\n# Packages in lower-priority channels not considered if a package with the same\\n# name exists in a higher priority channel. Can dramatically speed up installations.\\n# Conda recommends this as a default\\n# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html\\nconda config --set channel_priority strict\\nconda config --system --set auto_update_conda false\\nconda config --system --set show_channel_urls true\\n# Enable `conda activate`\\nconda init bash\\nconda install -y  --name base \\\\\\n    \\"nipype\\"\\n# Clean up\\nsync && conda clean --all --yes && sync\\nrm -rf ~/.cache/pip/*" \
      } \
    } \
  ] \
}' > /.reproenv.json



RUN mkdir /code

#Add the run.py script and readme, but also rename the run.py script
#to have a prettier entrypoint.
ADD run.py /code/mancorr_postbibsnet
ADD README.md /code/README.md

ENV FSLDIR=/usr/local/fsl

ENV FSLDIR="/usr/lib/fsl/5.0" \
    PATH="/usr/lib/fsl/5.0/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.4/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.4/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"

#This entrypoint assumes that the original run.py
#script had a header that points to the containers
#python installation. If you open the nipype container
#shown above and type "which python" you can find the
#path to the python installation that should be referenced
ENTRYPOINT ["/code/mancorr_postbibsnet"]
