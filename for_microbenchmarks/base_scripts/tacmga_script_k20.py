#!/home/farajii/bin/python_1_3.3/bin/python3
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
 #                       if (host == "gpu-k20-08" and s == 0):
 #                           f.write("rank " + str(r) + "=" + host + \
 #                               " slot="+str(1)+":"+str(c+4) + "\n")
 #                       else:
  #                      
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
    int(phase1_patt)
    int(phase2_patt)
except:
    print("Invalid number of processes or nodes!")
    usage()
    sys.exit()

######## Setup benchmark #########
#START Tests from START_PROC_NUM and multiply it by 2
START_PROC_NUM = 64

#Setting up result path
RESULT_PATH = "/home/farajii/git/git_iman_hessam/project1_topo_cpu_gpu/results/microbenchmarks"
#setting up RHG Rankfile + Hostfile + GPU ID file path
RHG = RESULT_PATH + "/rhg_files/" + str(np) + "/"
#Setting up Profiling path for CPU and GPU communication patterns
PROF = RESULT_PATH + "/prof_files/" + str(np) + "/"

TACMGA_PATH = "/home/farajii/git/tacmga"
exec_file = TACMGA_PATH + "/tacmga"

#building hostnames.txt file
build_hostnames(RHG)

#building the default hostfile, rankfile, and gpuid files
build_def_files(int(np), int(nn), int(ns), RHG)

size_list = ["256", "8192", "65536", "262144", "1048576"] #small, medium, and, large message
wght_list = ["1", "3"]
bench_list = ["2DSTENCIL", "3DTORUS", "COLLSUBCOMM"]
bench_dim = ["4 2","2 2 2", "1 0 0",\
             "4 4", "4 2 2", "1 0 0",\
             "8 4", "4 4 2", "1 0 0",\
             "8 8", "4 4 4", "1 0 0"]
"""
#[8p \ 1st row of bench_dim is the input param for 8 processes
#16p \ 2nd row of bench_dim is the input param for 16 processes
#32p \ 3rd row of bench_dim is the input param for 32 processes
#64p]\ 4th row of bench_dim is the input param for 64 processes

#First record all potential benchmark input options for 8 to 64 processes regardless of
#the number of processes in bench_dim_input list
#e.g. bench_dim_input["2DSTENCIL-16p"]=#dim_x #dim_y from the bench_dim
"""
num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for size in size_list:
        print("********************************************************** Size: " + str(size) + " **********************************************************\n")
        for wght in wght_list:
            print("**************************************** Weight: " + str(wght) + " ***********************************************\n")
            for cpu_bench in range(len(bench_list)):
                for gpu_bench in range(len(bench_list)):
                    print("************************** CPU BENCH: "  + str(bench_list[cpu_bench]) + " and GPU BENCH: " + str(bench_list[gpu_bench]) + " **************************\n")
                    env_list = ""
                    env_list = env_list + " SHM_CPU_VOL_FILE="  + PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_vol_out_cpu.txt"
                    env_list = env_list + " SHM_GPU_VOL_FILE=" + PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_vol_out_gpu.txt"
#                    env_list = env_list + " SHM_GPU_PHY_FILE=" + PROF + "gpu_phy.txt"
                    env_list = env_list + " SHM_GLOB_CPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/cpu_glob_dist." + str(START_PROC_NUM)
                    env_list = env_list + " SHM_GLOB_GPU_PHY_FILE=" + "/home/farajii/git/tacmga/dist/k20/gpu_glob_dist." + str(START_PROC_NUM)
                    
                    env_list = env_list + " SHM_PHASE_1_USE_PATTERN=" + phase1_patt
                    env_list = env_list + " SHM_PHASE_2_USE_PATTERN=" + phase2_patt
                    
                    env_list = env_list + " SHM_RANK_FILE=" + RHG + "rankfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + ".txt"
                    env_list = env_list + " SHM_HOST_FILE=" + RHG + "hostfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + ".txt"
                    env_list = env_list + " IMI_GPUID_FILE=" + RHG + "gpuidfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + ".txt"
                    env_list = env_list + " SHM_HOST_NAMES_FILE=" + RHG  + "hostnames.txt"
#                    print(env_list)
                    bash_cmd = "export " + env_list
                    run_cmd = exec_file + " " + np + " " + nn +\
                    " >" + str(RHG) + "out/" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_out.tacmga" +\
                    " 2>"+ str(RHG)+ "err/" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_err.tacmga"
                    print("\n", run_cmd, "\n")
                    bash_cmd = bash_cmd + " && " + run_cmd
                    os.system(bash_cmd)
    num_proc *= 2
