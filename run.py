#!/opt/miniconda-latest/envs/neuro/bin/python
import os, glob
import shutil
import argparse 
from nipype.interfaces import fsl

def main():
    parser = argparse.ArgumentParser(description="psuedo postbibsnet")
    parser.add_argument("input_folder", help="path to folder that contains BIBSNet work folders")
    parser.add_argument("output_folder", help="path to output folder that will contain study-wide BIBSNet derivatives folders")
    parser.add_argument('--participant_label', '--participant-label', help="The name/label of the subject to be processed (i.e. sub-01 or 01)", type=str)
    parser.add_argument('-w', '--w', help='Optional working for current pipeline where intermediate results are stored.')
    args = parser.parse_args()

    input_folder = os.path.abspath(args.input_folder)
    input_bibsnet_folder = os.path.join(input_folder, 'bibsnet')
    #output_folder = os.path.abspath(args.output_folder)
    output_bibsnet_folder = os.path.join(os.path.abspath(args.output_folder), 'bibsnet')
    original_bibsnet_folder = os.path.join(input_folder, 'derivatives', 'bibsnet')

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
        os.chdir(input_bibsnet_folder)
        participants = glob.glob('sub-*')

    for temp_sub in participants:
        os.chdir(os.path.join(input_folder, 'bibsnet', temp_sub))
        sessions = glob.glob('ses*')

        for temp_ses in sessions:
            session_input_derivatives_path = os.path.join(input_bibsnet_folder, temp_sub, temp_ses, 'anat')
            session_output_derivatives_path = os.path.join(output_bibsnet_folder, temp_sub, temp_ses, 'anat')
            if os.path.exists(session_output_derivatives_path) == False:
                os.makedirs(session_output_derivatives_path)

            #copy dataset_description.json to output derivatives folder if it doesn't exist already
            dataset_description_json_src=os.path.join(original_bibsnet_folder, 'dataset_description.json')
            dataset_description_json_dest=os.path.join(output_bibsnet_folder, 'dataset_description.json')
            if not os.path.exists(dataset_description_json_dest):
                shutil.copy(dataset_description_json_src, dataset_description_json_dest)

            derivatives_work_folder=os.path.join(input_folder, f'derivatives/bibsnet/{temp_sub}/{temp_ses}/anat')
            prebibsnet_work_folder= os.path.join(input_folder, f'prebibsnet/{temp_sub}/{temp_ses}')
            bibsnet_work_folder= os.path.join(input_folder, f'bibsnet/{temp_sub}/{temp_ses}')
            postbibsnet_work_folder=os.path.join(session_input_derivatives_path, f'postbibsnet/{temp_sub}/{temp_ses}')

            #specify pathname for intermediate brainmask derived from the segmentation prior to transformation into native space
            tmp_brainmask_MNIspace= os.path.join(work_folder, f'{temp_sub}_{temp_ses}_brainmask_MNIspace.nii.gz')

            # copy jsons to session_derivatives folder
            #jsons=glob.glob(f'{session_input_derivatives_path}/*json')
            #[shutil.copy(json, session_output_derivatives_path) for json in jsons]

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
                inv_mat=f'{postbibsnet_work_folder}/chirality_correction/seg_reg_to_{t}_native.mat' #exists
                aseg_deriv=f'{session_input_derivatives_path}/{temp_sub}_{temp_ses}_space-{t}_desc-aseg_dseg.nii.gz' #should exist 
                brainmask_deriv=f'{session_input_derivatives_path}/{temp_sub}_{temp_ses}_space-{t}_desc-brain_mask.nii.gz' #should exist

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
                    flt.outputs.no_save_mats=True
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

            # FLIRT saves a separate transformation matrix applied to generate the output file even when an external transform is                  # supplied. These files are not needed, however, so define the automated filepaths created and remove them.
            tmp_aseg_mat=f'{temp_sub}_{temp_ses}_optimal_resized_flirt.mat'
            tmp_brainmask_mat=f'{temp_sub}_{temp_ses}_brainmask_MNIspace_flirt.mat'
            
            os.remove(tmp_aseg_mat)
            os.remove(tmp_brainmask_mat)

            #Copy to the output derivatives path
            shutil.copytree(session_input_derivatives_path, session_output_derivatives_path)
            
if __name__ == "__main__":
    main()
