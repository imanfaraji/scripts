#!/home/farajii/bin/python_1_3.3/bin/python3
#FINDING OPTIMAL MAPPING USING SCOTCH
import sys, getopt, os

def usage():
    print("-p NUM_OF_PROCESSES")
    print("-n NUM_OF_NODES")
    print("--phase1-patt=0 or 1 or 2 (CPU, GPU, CPUGPU)")
    print("--phase2-patt=0 or 1 or 2 (CPU, GPU, CPUGPU)")
    print("Actual host names should be in hostnames.txt")

def build_hostnames(path):
    if "PBS_NODEFILE" in os.environ:
        os.system("sort $PBS_NODEFILE | uniq > " + path + "hostnames.txt")
    else:
        print("PBS_NODEFILE not defined. Skipping hostnames.txt build")

def build_def_host(np, nn, path):
    ranks_per_node = int (np / nn)
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
                        f.write("rank " + str(r) + "=" + host + \
                                " slot="+str(s)+":"+str(c) + "\n")
                        r = r + 1

def build_def_gpuid(np, nn, path):
    ranks_per_node = int(np / nn)
    with open(path + "def_gpuidfile.txt", "w") as f:
        for node in range(nn):
            for r in range(ranks_per_node):
                f.write(str(r) + "\n")


def build_def_files(np, nn, ns, path):
    build_def_host(np, nn, path)
    build_def_rank(np, nn, ns, path)
    build_def_gpuid(np, nn, path)


np = ""
nn = ""
ns = 2
print("Assuming 2 sockets on each node")
phase1_patt = ""
phase2_patt = ""


try:
    options, arguments = getopt.getopt(sys.argv[1:], "hp:n:", ["phase1-patt=", "phase2-patt="])
except getopt.GetoptError:
    print("Eroor in input options or arguments")
    sys.exit(2)

for opt, val in options:
    if opt == "-h":
        usage()
        sys.exit()
    if opt == "-p":
        np = val
    elif opt == "-n":
        nn = val
    elif opt == "--phase1-patt":
        phase1_patt = val
    elif opt == "--phase2-patt":
        phase2_patt = val
try:
    int(np)
    int(nn)
except:
    print("Invalid number of processes or nodes!")
    usage()
    sys.exit()


######## Start #########
START_PROC_NUM = 64   
RESULT_PATH = "/home/farajii/git/git_iman_hessam/project1_topo_cpu_gpu/results/hoomd"
#setting up RHG Rankfile + Hostfile + GPU ID file path
RHG = RESULT_PATH + "/rhg_files/" + str(np) + "/"
#Setting up Profiling path for CPU and GPU communication patterns
PROF = RESULT_PATH + "/prof_files/" + str(np) + "/"

TACMGA_PATH = "/home/farajii/git/tacmga"
exec_file = TACMGA_PATH + "/tacmga"


#building hostnames.txt file
build_hostnames(RHG)

#building the default hostfile, rankfile, and gpuid files
#build_def_files(int(np), int(nn), int(ns), RHG)

######## Start #########
#building hostnames.txt file

run_prec_type = ["SP", "DP"]
#bench_list_1 = ["lj-liquid", "microsphere", "quasicrystal", "triblock-copolymer"]
bench_run_type = ["prof"]

######### Bench list 1 -- different benchmark types ##########
bench_list_1 = []
#bench_list_1 = ["microsphere"]
#bench_list_1 = ["microsphere", "quasicrystal"]
bench_particle_size_1 = ["basic"]

num_proc = START_PROC_NUM 
while num_proc <= int(np):
    print("*********************************************************************** Using TACMGA for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for bench in bench_list_1:
        print("**************************************************************************** Benchmark: ", bench, "**********************************************************")
        for particle_size in bench_particle_size_1:
            print("**************************************************** Particle Size: ", particle_size, " ********************************************** ")
            for run_type in bench_run_type:
                print("************************************** Run type: ", run_type, " **************************************")
                for prec_type in run_prec_type:
                    print("*********************** Precision type: ", prec_type, " ***********************")
                    bench_str = bench + "_" + particle_size + "_" + run_type
                    env_list = ""
                    env_list = env_list + " SHM_CPU_VOL_FILE=" + PROF + bench_str + "_" + prec_type + "_vol_out_cpu.txt"
                    env_list = env_list + " SHM_GPU_VOL_FILE=" + PROF + bench_str + "_" + prec_type + "_vol_out_gpu.txt"
#                    env_list = env_list + " SHM_GPU_PHY_FILE=" + PROF + "gpu_phy.txt"
                    env_list = env_list + " SHM_GLOB_CPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/cpu_glob_lat." + str(START_PROC_NUM)
                    env_list = env_list + " SHM_GLOB_GPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/gpu_glob_lat." + str(START_PROC_NUM)
                    
                    
                    env_list = env_list + " SHM_PHASE_1_USE_PATTERN=" + phase1_patt
                    env_list = env_list + " SHM_PHASE_2_USE_PATTERN=" + phase2_patt
                    
                    env_list = env_list + " SHM_RANK_FILE=" + RHG + "rankfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " SHM_HOST_FILE=" + RHG + "hostfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " IMI_GPUID_FILE=" + RHG + "gpuidfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " SHM_HOST_NAMES_FILE=" + RHG  + "hostnames.txt"

                    print(env_list)
                    
                    #print env_list
                    bash_cmd = "export " + env_list
                    run_cmd = exec_file + " " + np + " " + nn +\
                    " >" + str(RHG) + "out/" + bench + "_size_" + str(particle_size) + "_out.tacmga" +\
                    " 2>"+ str(RHG) + "err/" + bench + "_size_" + str(particle_size) + "_err.tacmga"
                    print("\n", run_cmd, "\n")
                    bash_cmd = bash_cmd + " && " + run_cmd
                    os.system(bash_cmd)
    num_proc *= 2
    
######## Bench list 2 --- different particle size on one benchmark ########

bench_list_2 = ["lj"]
bench_particle_size_2 = ["512K", "1M", "2M"]

num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Using TACMGA for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for bench in bench_list_2:
        print("**************************************************************************** Benchmark: ", bench, "**********************************************************")
        for particle_size in bench_particle_size_2:
            print("**************************************************** Particle Size: ", particle_size, " ********************************************** ")
            for run_type in bench_run_type:
                print("************************************** Run type: ", run_type, " **************************************")
                for prec_type in run_prec_type:
                    print("*********************** Precision type: ", prec_type, " ***********************")
                    bench_str = bench + "_" + particle_size + "_" + run_type
                    env_list = ""
                    env_list = env_list + " SHM_CPU_VOL_FILE=" + PROF + bench_str + "_" + prec_type + "_cnt_out_cpu.txt"
                    env_list = env_list + " SHM_GPU_VOL_FILE=" + PROF + bench_str + "_" + prec_type + "_cnt_out_gpu.txt"
#                    env_list = env_list + " SHM_GPU_PHY_FILE=" + PROF + "gpu_phy.txt"
                    env_list = env_list + " SHM_GLOB_CPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/cpu_glob_lat." + str(START_PROC_NUM)
                    env_list = env_list + " SHM_GLOB_GPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/gpu_glob_lat." + str(START_PROC_NUM)
                    

                    env_list = env_list + " SHM_PHASE_1_USE_PATTERN=" + phase1_patt
                    env_list = env_list + " SHM_PHASE_2_USE_PATTERN=" + phase2_patt
                    
                    env_list = env_list + " SHM_RANK_FILE=" + RHG + "rankfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " SHM_HOST_FILE=" + RHG + "hostfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " IMI_GPUID_FILE=" + RHG + "gpuidfile_" + bench_str + "_" + prec_type + ".txt"
                    env_list = env_list + " SHM_HOST_NAMES_FILE=" + RHG  + "hostnames.txt"
    
#                    print(env_list)
                    
                    bash_cmd = "export " + env_list
                    run_cmd = exec_file + " " + np + " " + nn +\
                    " >" + str(RHG) + "out/" + bench + "_size_" + str(particle_size) + "_out.tacmga" +\
                    " 2>"+ str(RHG) + "err/" + bench + "_size_" + str(particle_size) + "_err.tacmga"
                    print("\n", run_cmd, "\n")
                    bash_cmd = bash_cmd + " && " + run_cmd
    
                    os.system(bash_cmd)
    num_proc *= 2
