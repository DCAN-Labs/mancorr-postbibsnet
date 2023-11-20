import os, glob
import shutil
import argparse 
from nipype.interfaces import fsl

def main():
    parser = argparse.ArgumentParser(description="psuedo postbibsnet")
    parser.add_argument("input_folder", help="path to folder that contains BIBSNet work folders")
    parser.add_argument("derivatives_folder", help="path to folder that contains study-wide BIBSNet derivatives folders")
    parser.add_argument('--participant_label', '--participant-label', help="The name/label of the subject to be processed (i.e. sub-01 or 01)", type=str)
    parser.add_argument('-w', '--w', help='Optional working for current pipeline where intermediate results are stored.')
    args = parser.parse_args()

    input_folder = os.path.abspath(args.input_folder)
    derivatives_folder = os.path.abspath(args.derivatives_folder)

    if args.w:
        work_folder = os.path.abspath(args.w)
    else:
        work_folder = '/tmp'

    #Find participants to try running
    if args.participant_label:
        participant_split = args.participant_label.split(' ')
        participants = []
        for temp_participant in participant_split:
            if 'sub-' not in temp_participant:
                participants.append('sub-' + temp_participant)
            else:
                participants.append(temp_participant)
    else:
        os.chdir(os.path.join(input_folder, 'bibsnet'))
        participants = glob.glob('sub-*')

    for temp_sub in participants:
        os.chdir(os.path.join(input_folder, 'bibsnet', temp_sub))
        sessions = glob.glob('ses*')

        for temp_ses in sessions:
            session_derivatives_path = os.path.join(derivatives_folder, temp_sub, temp_ses, 'anat')
            if os.path.exists(session_derivatives_path) == False:
                os.makedirs(session_derivatives_path)
        
            # copy jsons to session_derivatives folder
            sesion_orig_derivs=os.path.join(input_folder, f'derivatives/bibsnet/{temp_sub}/{temp_ses}', 'anat')
            jsons=glob.glob(f'{sesion_orig_derivs}/*json')
            [shutil.copy(json, session_derivatives_path) for json in jsons]

            #copy dataset_description.json to output derivatives folder if it doesn't exist already
            dataset_description_json_src=os.path.join(input_folder, 'derivatives/bibsnet/dataset_description.json')
            dataset_description_json_dest=os.path.join(derivatives_folder, 'dataset_description.json')

            if not os.path.exists(dataset_description_json_dest):
                shutil.copy(dataset_description_json_src, dataset_description_json_dest)

            prebibsnet_work_folder= os.path.join(input_folder, f'prebibsnet/{temp_sub}/{temp_ses}')
            bibsnet_work_folder= os.path.join(input_folder, f'bibsnet/{temp_sub}/{temp_ses}')
            postbibsnet_work_folder=os.path.join(input_folder, f'postbibsnet/{temp_sub}/{temp_ses}')
            derivatives_folder=session_derivatives_path

            tmp_brainmask_MNIspace= os.path.join(work_folder, f'{temp_sub}_{temp_ses}_brainmask_MNIspace.nii.gz')

            # create aseg-derived mask
            aseg= os.path.join(bibsnet_work_folder, f'output/{temp_sub}_{temp_ses}_optimal_resized.nii.gz')
            maths = fsl.ImageMaths(in_file=aseg,
                                    op_string=("-bin -dilM -dilM -dilM -dilM "
                                    "-fillh -ero -ero -ero -ero"),
                                    out_file=tmp_brainmask_MNIspace)
            maths.run()

            # Register aseg and mask back into native space and replace derivatives
            t_mod = ['T1w', 'T2w']
            for t in t_mod:
                inv_mat=f'{postbibsnet_work_folder}/chirality_correction/seg_reg_to_{t}_native.mat'
                aseg_deriv=f'{derivatives_folder}/{temp_sub}_{temp_ses}_space-{t}_desc-aseg_dseg.nii.gz'
                brainmask_deriv=f'{derivatives_folder}/{temp_sub}_{temp_ses}_space-{t}_desc-brain_mask.nii.gz'

                if t == 'T1w':
                    native_anat=f'{prebibsnet_work_folder}/averaged/{temp_sub}_{temp_ses}_0000.nii.gz'
                elif t == 'T2w':
                    native_anat=f'{prebibsnet_work_folder}/averaged/{temp_sub}_{temp_ses}_0001.nii.gz'

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