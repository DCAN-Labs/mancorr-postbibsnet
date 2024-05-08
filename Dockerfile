#This image already has nipype + FSL installed.
#Note: only certain versions of FSL are nipype compatible
FROM nipype/nipype:py38

#Make a directory to store any of the code we need
USER root
RUN mkdir /code

#Add the run.py script and readme, but also rename the run.py script
#to have a prettier entrypoint.
ADD run.py /code/mancorr_postbibsnet
ADD README.md /code/README.md

ENV FSLWISH=/usr/bin/wish
ENV FSLDIR=/usr/share/fsl/5.0
ENV FSLBROWSER=/etc/alternatives/x-www-browser
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLMULTIFILEQUIT=TRUE
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/common/software/install/migrated/anaconda/python3-2020.07-mamba/bin:/opt/miniconda-latest/envs/neuro/bin:/opt/miniconda-latest/condabin:/usr/lib/fsl/5.0:/opt/freesurfer-6.0.0-min/bin:/opt/freesurfer-6.0.0-min/fsfast/bin:/opt/freesurfer-6.0.0-min/tktools:/opt/freesurfer-6.0.0-min/mni/bin:/opt/miniconda-latest/bin:/usr/lib/ants:/opt/dcm2niix-v1.0.20190902/bin:/opt/freesurfer-6.0.0-min/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/afni/bin
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:/opt/matlabmcr-2010a/v713/runtime/glnxa64:/opt/matlabmcr-2010a/v713/bin/glnxa64:/opt/matlabmcr-2010a/v713/sys/os/glnxa64:/opt/matlabmcr-2010a/v713/extern/bin/glnxa64:/.singularity.d/libs


#This entrypoint assumes that the original run.py
#script had a header that points to the containers
#python installation. If you open the nipype container
#shown above and type "which python" you can find the
#path to the python installation that should be referenced
ENTRYPOINT ["/code/mancorr_postbibsnet"]
