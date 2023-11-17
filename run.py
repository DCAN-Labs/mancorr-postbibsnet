import os
import argparse 
from nipype.interfaces import fsl

def main():
    parser = argparse.ArgumentParser(description="psuedo postbibsnet")
    parser.add_argument("inputfolder", help="path to folder that contains BIBSNet work and derivatives folders")
    parser.add_argument("sub", help="subject ID (eg sub-11100)")
    parser.add_argument("ses", help="subject session (eg ses-AAA)")
    args = parser.parse_args()

    basedir=args.inputfolder
    sub=args.sub 
    ses=args.ses 

    prebibsnet_work_folder=f'{basedir}/work/prebibsnet/{sub}/{ses}'
    bibsnet_work_folder=f'{basedir}/work/bibsnet/{sub}/{ses}'
    postbibsnet_work_folder=f'{basedir}/work/postbibsnet/{sub}/{ses}'
    derivatives_folder=f'{basedir}/derivatives/bibsnet/{sub}/{ses}/anat'

    tmp_brainmask_MNIspace=f'/tmp/{sub}_{ses}_brainmask_MNIspace.nii.gz'

    # create aseg-derived mask
    aseg=f'{bibsnet_work_folder}/output/{sub}_{ses}_optimal_resized.nii.gz'
    maths = fsl.ImageMaths(in_file=aseg,
                            op_string=("-bin -dilM -dilM -dilM -dilM "
                            "-fillh -ero -ero -ero -ero"),
                            out_file=tmp_brainmask_MNIspace)
    maths.run()

    # Register aseg and mask back into native space and replace derivatives
    t_mod = ['T1w', 'T2w']
    for t in t_mod:
        inv_mat=f'{postbibsnet_work_folder}/chirality_correction/seg_reg_to_{t}_native.mat'
        aseg_deriv=f'{derivatives_folder}/{sub}_{ses}_space-{t}_desc-aseg_dseg.nii.gz'
        brainmask_deriv=f'{derivatives_folder}/{sub}_{ses}_space-{t}_desc-brain_mask.nii.gz'

        if t == 'T1w':
            native_anat=f'{prebibsnet_work_folder}/averaged/{sub}_{ses}_0000.nii.gz'
        elif t == 'T2w':
            native_anat=f'{prebibsnet_work_folder}/averaged/{sub}_{ses}_0001.nii.gz'

        if os.path.exists(native_anat):
            #apply inverse transform to bibsnet output segmentation to get into native space
            flt = fsl.FLIRT(interp='nearestneighbour',
                            apply_xfm=True,
                            reference=native_anat,
                            in_file=aseg,
                            in_matrix_file=inv_mat,
                            out_file=aseg_deriv)
            flt.run()

            #apply inverse transform to brainmask to get into native space
            flt = fsl.FLIRT(interp='nearestneighbour',
                            apply_xfm=True,
                            reference=native_anat,
                            in_file=tmp_brainmask_MNIspace,
                            in_matrix_file=inv_mat,
                            out_file=brainmask_deriv)
            flt.run()
    
    os.remove(tmp_brainmask_MNIspace)
            
if __name__ == "__main__":
    main()