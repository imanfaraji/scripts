#! /home/farajii/bin/python_1_3.3/bin/python3
#HOOMD-BLUE PROFILER
import sys, getopt, os

def usage():
    print("-p Num of processes")
    print("-n Num of node (Need this to make the default host and rank files)")
    print("-g Num GPUs per node")

def build_hostnames(path):
    if "PBS_NODEFILE" in os.environ:
        os.system("sort $PBS_NODEFILE | uniq > " + path + "hostnames.txt")
    else:
        print("PBS_NODEFILE not defined. Skipping hostnames.txt build")

def build_def_host(np, nn, path):
    ranks_per_node = int(np / nn)
    with open(path + "hostnames.txt", "r") as fh:
        with open(path + "def_hostfile.txt", "w") as f:
            hostnames = fh.read().splitlines()
            for host in hostnames:
                for i in range(ranks_per_node):
                    f.write(host + "\n")

def build_def_rank(np, nn, ns, path):
    ranks_per_node = int(np / nn)
    ranks_per_socket = int(ranks_per_node / ns)
    r = 0   
    with open(path + "hostnames.txt", "r") as fh:
        with open(path + "def_rankfile.txt", "w") as f:
            hostnames = fh.read().splitlines()
            for host in hostnames:
                for s in range(ns):
                    for c in range(ranks_per_socket):
                        if (host == "gpu-k80-03"):
                            if(s == 0 and c ==5):
                                f.write("rank " + str(r) + "=" + host + \
                                                " slot=0:8\n")
                            elif (s == 1 and c ==1):
                                f.write("rank " + str(r) + "=" + host + \
                                        " slot=0:9\n")
                            else :
                                f.write("rank " + str(r) + "=" + host + \
                                    " slot="+str(s)+":"+str(c) + "\n")
                        else:
                                f.write("rank " + str(r) + "=" + host + \
                                    " slot="+str(s)+":"+str(c) + "\n")
                        r = r + 1

def build_def_gpuid(np, nn, path):
    ranks_per_node = int(np / nn)
    with open(path + "def_gpuidfile.txt", "w") as f:
        for node in range(nn):
            for r in range(ranks_per_node):
                f.write(str(r) + "\n")

np = ""
ng = ""
nn = ""
ns = 2
print("Assuming 2 sockets on each node")

try:
    options, arguments = getopt.getopt(sys.argv[1:], "hp:n:g:")
except getopt.GetoptError:
    print("Error in input options or arguments")
    sys.exit(2)

for opt, val in options:
    if opt == "-h":
        usage()
        sys.exit()
    if opt == "-p":
        np = val
    if opt == "-n":
        nn = val
    elif opt == "-g":
        ng = val
try:
    int(np)
    int(nn)
    int(ng)
except:
    print("Bad number of processes or nodes or GPUs!")
    usage()
    sys.exit()
########  Setup benchmark #########
#setting up result path
RESULT_PATH = "/home/farajii/git/git_iman_hessam/project1_topo_cpu_gpu/results/hoomd"

START_PROC_NUM = 64 

#setting up RHG Rankfile + Hostfile + GPU ID file path
RHG = RESULT_PATH + "/rhg_files/" + str(np) + "/"
#Setting up Profiling path for CPU and GPU communication patterns
PROF = RESULT_PATH + "/prof_files/" + str(np) + "/"

#setting up HOOMD executable
#Hoomd executables

HOOMD_PROF_SP = "/home/farajii/tests/14_HOOMD-blue/build6_ompi_cpu_gpu_prof_MPI_GPU/bin/hoomd"
HOOMD_PROF_DP = "/home/farajii/tests/14_HOOMD-blue/build8_ompi_cpu_gpu_prof_MPI_GPU_double/bin/hoomd"

#MPIRUN Profiler executable
MPIRUN_PROF = "//home/farajii/builds/10-ompi-1.10.2_ompi-prof_cuda-prof/bin/mpirun"

#BENCHMARK PATH
BENCH = "/home/farajii/tests/14_HOOMD-blue/hoomd-benchmarks/"

#building hostnames.txt file
build_hostnames(RHG)
    
#building the default hostfile and rankfile
build_def_host(int(np), int(nn), RHG)
build_def_rank(int(np), int(nn), int(ns), RHG)
build_def_gpuid(int(np), int(nn), RHG)

bench_run_type = ["prof"]
run_prec_type = ["SP", "DP"]
#bench_list_1 = ["lj-liquid", "microsphere", "quasicrystal", "triblock-copolymer"]

######### Bench list 1 -- different benchmark types ##########
bench_list_1 = []
#bench_list_1 = ["microsphere"]
bench_particle_size_1 = ["basic"]

num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for bench in bench_list_1:
        os.chdir(BENCH + bench)
        os.system("pwd")
        print("**************************************************************************** Benchmark: ", bench, "**********************************************************")
        for particle_size in bench_particle_size_1:
            print("**************************************************** Particle Size: ", particle_size, " ********************************************** ")
            for run_type in bench_run_type:
                print("************************************** Run type: ", run_type, " **************************************")
                for prec_type in run_prec_type:
                    print("*********************** Precision type: ", prec_type, " ***********************")
                    bench_str = bench + "_" + particle_size + "_" + run_type
                    env_list = " SHM_COMM_PATT_CNT_OUT_FILE_CPU=" + PROF + bench_str + "_" + prec_type + "_cnt_out_cpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_CPU=" + PROF + bench_str + "_" + prec_type + "_vol_out_cpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_CNT_OUT_FILE_GPU=" + PROF + bench_str + "_" + prec_type + "_cnt_out_gpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_GPU=" + PROF + bench_str + "_" + prec_type + "_vol_out_gpu.txt"
                    bash_cmd = "export " + env_list
                    ompi_export_list = " -x SHM_COMM_PATT_CNT_OUT_FILE_CPU -x SHM_COMM_PATT_VOL_OUT_FILE_CPU -x SHM_COMM_PATT_CNT_OUT_FILE_GPU -x SHM_COMM_PATT_VOL_OUT_FILE_GPU -x LD_LIBRARY_PATH "
                    ompi_run_cmd = MPIRUN_PROF + " -n " + str(np) +  " --report-bindings -hostfile " + RHG + "def_hostfile.txt "+ "-rankfile " + RHG + "def_rankfile.txt " + ompi_export_list +\
                                   locals()["HOOMD_PROF_" + prec_type] + " " + BENCH + bench + "/" + bench_str + ".py" + " --mode=gpu" +\
                                   " >" + str(PROF) + "out/" + str(particle_size) + "_out.log" + " 2>" + str(PROF) + "err/" + str(particle_size) + "_err.log"
                    bash_cmd = bash_cmd + " && " + ompi_run_cmd
                    print("\n", ompi_run_cmd,"\n\n")
                    sys.stdout.flush()
                    os.system(bash_cmd)
    num_proc *= 2

######## Bench list 2 --- different particle size on one benchmark ########
bench_list_2 = ["lj"]
bench_particle_size_2 = ["512K", "1M", "2M"]

num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for bench in bench_list_2:
#        os.chdir(BENCH + bench)
        os.system("pwd")
        print("**************************************************************************** Benchmark: ", bench, "**********************************************************")
        for particle_size in bench_particle_size_2:
            print("**************************************************** Particle Size: ", particle_size, " ********************************************** ")
            for run_type in bench_run_type:
                print("************************************** Run type: ", run_type, " **************************************")
                for prec_type in run_prec_type:
                    print("*********************** Precision type: ", prec_type, " ***********************")
                    bench_str = bench + "_" + particle_size + "_" + run_type
                    env_list = " SHM_COMM_PATT_CNT_OUT_FILE_CPU=" + PROF + bench_str + "_" + prec_type + "_cnt_out_cpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_CPU=" + PROF + bench_str + "_" + prec_type + "_vol_out_cpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_CNT_OUT_FILE_GPU=" + PROF + bench_str + "_" + prec_type + "_cnt_out_gpu.txt"
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_GPU=" + PROF + bench_str + "_" + prec_type + "_vol_out_gpu.txt"
                    bash_cmd = "export " + env_list
                    ompi_export_list = " -x SHM_COMM_PATT_CNT_OUT_FILE_CPU -x SHM_COMM_PATT_VOL_OUT_FILE_CPU -x SHM_COMM_PATT_CNT_OUT_FILE_GPU -x SHM_COMM_PATT_VOL_OUT_FILE_GPU -x LD_LIBRARY_PATH "
                    ompi_run_cmd = MPIRUN_PROF + " -n " + str(np) +  " -hostfile " + RHG + "def_hostfile.txt "+ "-rankfile " + RHG + "def_rankfile.txt " + ompi_export_list +\
                                   locals()["HOOMD_PROF_" + prec_type] + " " + BENCH + bench + "/" + bench_str + ".py" + " --mode=gpu " +\
                                   " >" + str(PROF) + "out/" + bench + "_" + str(particle_size) + "_out.log" + " 2>" + str(PROF) + "err/" + bench + "_" + str(particle_size) + "_err.log"
                    bash_cmd = bash_cmd + " && " + ompi_run_cmd
                    print("\n", ompi_run_cmd,"\n\n")
                    sys.stdout.flush()
                    os.system(bash_cmd)
    num_proc *= 2
########## benchmark ends ##########
