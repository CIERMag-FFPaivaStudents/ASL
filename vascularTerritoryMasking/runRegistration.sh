#!/usr/bin/bash

flirt -in data/ASL/perfusion_calib.nii.gz -ref data/struct_space/ch2better.nii.gz -out data/struct_perfusion_calib.nii.gz -omat data/native2struct.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear

convert_xfm -omat data/struct2native.mat -inverse data/native2struct.mat

flirt -in data/mask/Vascular_territory_atlas.nii -applyxfm -init data/struct2native.mat -out data/native_vascular_territory_atlas.nii.gz -paddingsize 0.0 -interp nearestneighbour -ref data/ASL/perfusion_calib.nii.gz
