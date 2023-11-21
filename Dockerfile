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

#ENV 

#This entrypoint assumes that the original run.py
#script had a header that points to the containers
#python installation. If you open the nipype container
#shown above and type "which python" you can find the
#path to the python installation that should be referenced
ENTRYPOINT ["/code/mancorr_postbibsnet"]
