#!/bin/bash
# PBS -S /bin/bash
# PBS -A dri-911-aa
# PBS -l walltime=06:00:00
# PBS -l feature=k20
# PBS -l nodes=8:gpus=8
# PBS -r n
# Date: JUNE, 28, 2016 - 14:15
# Job: MAGC Test on 8 nodes 64 GPUs - 4th Run 
# Developped by: Iman Faraji
cd ${PBS_O_WORKDIR}


##################
#SET ALL PATHS AND LOAD ALL REQUIRED MODULES

STAT=64P_8N_8G_run5_CAMERA_READY_CASE1

#CUDA
module load cuda/7.5.18
module load apps/cmake/3.4.0
module load libs/fftw/3.3.3

#Python
export PATH=/home/farajii/bin/python_1_3.3/bin/:$PATH
export PYTHONPATH=/home/farajii/bin/python_1_3.3/lib/python3.3/site-packages/
export LD_LIBRARY_PATH=/home/farajii/bin/python_1_3.3/lib/:$LD_LIBRARY_PATH

#Boost
export BOOST_ROOT=/home/farajii/bin/boost_3_1.55/
export LD_LIBRARY_PATH=/home/farajii/bin/boost_3_1.55/lib:$LD_LIBRARY_PATH

##############################################################    MICRO BENCHMARKS   #######################################################################################
MY_DIR=/home/farajii/git/project1_topo_cpu_gpu/scripts/for_microbenchmarks/

echo '--------------MICROBENCHMARK SCOTCH TEST on 64 Proc 8 GPUs 8 Nodes - Camera Ready Starts----------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------Profiling Starts-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/prfl_run_k20.py -p 64 -n 8 -g 8 -i 1 -s 1 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------Profiling ENDS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------TACMGA SCOTCH STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/tacmga_script_k20.py -p 64 -n 8 --phase1-patt=0 --phase2-patt=0 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------TACMGA SCOTCH ENDS---------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------Running SCOTCH and DEFAULT STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/run_script_k20.py -p 64 -n 8 -g 8 -i 100 -s 10 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------Running SCOTCH and DEFAULT ENDS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '***********************************MICROBENCHMARK SCOTCH TEST ON 64 Proc 16 GPUs 4 Nodes ENDS*******************************************' >> ${MY_DIR}/out/"$STAT"_timing.out

echo '---------------------------------------MICROBENCHMARK HEURISTIC TEST ON 64 Proc 8 GPUs 8 Nodes STARTS----------------------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------TACMGA HEURISTIC STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/tacmga_script_h_k20.py -p 64 -n 8 --phase1-patt=0 --phase2-patt=0 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------TACMGA HEURISTIC ENDS---------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

echo '-----------------------Running HEURISTIC STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/run_script_h_k20.py -p 64 -n 8 -g 8 -i 100 -s 10 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------Running HEURISTIC ENDS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

echo '---------------------------------------MICROBENCHMARK HEURISTIC TEST ON 64 Proc 16 GPUs 4 Nodes ENDS----------------------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
##############################################################    APPLICATION   #######################################################################################

MY_DIR=/home/farajii/git/project1_topo_cpu_gpu/scripts/for_hoomd/

echo '---------------------------------------APP-HOOMD-Blue Test on 64 Proc 16 GPUs 4 Nodes Starts----------------------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------Profiling Starts-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/prfl_run_k20.py -p 64 -n 8 -g 8  #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------Profiling ENDS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------TACMGA SCOTCH STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/tacmga_script_k20.py -p 64 -n 8 --phase1-patt=0 --phase2-patt=0 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------TACMGA SCOTCH ENDS---------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------Running SCOTCH and DEFAULT STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/run_script_k20_run2.py -p 64 -n 8 -g 8 -i 100 -s 10 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------Running SCOTCH and DEFAULT ENDS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

echo '---------------------------------------APP-HOOMD-Blue Test on 64 Proc 16 GPUs 4 Nodes Starts----------------------------------' >> $DIR/out/"$STAT"_timing.out

																			  
date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------TACMGA HEURISTIC STARTS-------------------' >> ${MY_DIR}/out/"$STAT"_timing.out
${MY_DIR}/base_scripts/tacmga_script_h_k20.py -p 64 -n 8 --phase1-patt=0 --phase2-patt=0 #>> ${MY_DIR}/out/"$STAT".out
echo '-----------------------TACMGA HEURISTIC ENDS---------------------' >> ${MY_DIR}/out/"$STAT"_timing.out

date >> ${MY_DIR}/out/"$STAT"_timing.out
echo '-----------------------Running HEURISTIC STARTS-------------------' 
${MY_DIR}/base_scripts/run_script_h_k20_run2.py -p 64 -n 8 -g 8 -i 100 -s 10 #>> ${MY_DIR}/out/"$STAT".out

echo '-----------------------Running HEURISTIC and DEFAULT ENDS-------------------' 
date >> ${MY_DIR}/out/"$STAT"_timing.out
###########################################################################################################################################################################
