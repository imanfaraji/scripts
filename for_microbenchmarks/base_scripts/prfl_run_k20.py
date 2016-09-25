#!/home/farajii/bin/python_1_3.3/bin/python3
#MICROBENCHMARK PROFILER
import sys, getopt, os

def usage():
    print("-p Num of processes")
    print("-n Num of nodes (Need this to make the default host and rank files)")
    print("-g Num GPUs per node")
    print("-i Num of iterations")
    print("-s Num of skips")

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
                        f.write("rank " + str(r) + "=" + host + " slot="+str(s)+":"+str(c) + "\n")
                        r = r + 1
def build_def_gpuid(np, nn, path):
    ranks_per_node = int(np / nn)
    with open(path + "def_gpuidfile.txt", "w") as f:
        for node in range(nn):
            for r in range(ranks_per_node):
                f.write(str(r) + "\n")

np = ""
nn = ""
ng = ""
niters = ""
nskips = ""
ns = 2
print("Assuming 2 sockets on each node")

try:
    options, arguments = getopt.getopt(sys.argv[1:], "hp:n:g:i:s:")
except getopt.GetoptError:
    print("Error in input options or arguments")
    sys.exit(2)

for opt, val in options:
    if opt == "-h":
        usage()
        sys.exit()
    if opt == "-p":
        np = val
    elif opt == "-n":
        nn = val
    elif opt == "-g":
        ng = val
    elif opt == "-i":
        niters = val
    elif opt == "-s":
        nskips = val
try:
    int(np)
    int(nn)
    int(ng)
    int(niters)
    int(nskips)
except:
    print("Bad number of processes or GPUs or iterations or skips!")
    usage()
    sys.exit()
######## Setup benchmark #########
#START Tests from START_PROC_NUM and multiply it by 2
START_PROC_NUM = 64

#Setting up result path
RESULT_PATH = "/home/farajii/git/git_iman_hessam/project1_topo_cpu_gpu/results/microbenchmarks"

#Setting up RHG Rankfile + Hostfile + GPU ID file path
RHG = RESULT_PATH + "/rhg_files/" + str(np) + "/"

#Setting up Profiling path for CPU and GPU communication patterns
PROF = RESULT_PATH + "/prof_files/" + str(np) + "/"

#Microbenchmark executable
bench_path = "/home/farajii/tests/22_MICROBENCHMARKS/PROF"
bench_str = bench_path + "/MICRO_BENCHMARK"
#MPIRUN Profiler executable
#MPIRUN_PROF = "/home/farajii/builds/10-ompi-1.10.2_ompi-prof_cuda-prof/bin/mpirun"
MPIRUN_PROF="/home/farajii/builds/10-ompi-1.10.2_ompi-prof_cuda-prof/bin/mpirun"

#building hostnames.txt file
build_hostnames(RHG)
#building the default hostfile and rankfile
build_def_host(int(np), int(nn), RHG)
build_def_rank(int(np), int(nn), int(ns), RHG)
build_def_gpuid(int(np), int(nn), RHG)




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
bench_dim_input = {}
num_proc = 8
cnt = 0
while num_proc <= 64:
    for j in range(len(bench_list)):
        bench_dim_input[str(bench_list[j]) + "-" + str(num_proc) + "p"] = bench_dim[j + cnt*len(bench_list)]
    cnt += 1
    num_proc *= 2

'''
#uncomment this part to check the validity of input assignment
num_proc = 8
cnt = 0
while num_proc <= 64:
    for j in range(len(bench_list)):
        print str(bench_list[j]) + "-" + str(num_proc) + "p: " +  str(bench_dim_input[str(bench_list[j]) + "-" + str(num_proc) + "p"])
    cnt += 1
    num_proc *= 2
'''
########## run benchmark ##########
num_proc = START_PROC_NUM
cnt = 0
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for size in size_list:
        print("********************************************************** Size: " + str(size) + " **********************************************************\n")
        for wght in wght_list:
            print("**************************************** Weight: " + str(wght) + " ***********************************************\n")
            for cpu_bench in range(len(bench_list)):
                for gpu_bench in range(len(bench_list)):
                    print("************************** CPU BENCH: "  + str(bench_list[cpu_bench]) + " and GPU BENCH: " + str(bench_list[gpu_bench]) + " **************************\n")
                    env_list = " SHM_COMM_PATT_CNT_OUT_FILE_CPU="+ PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_cnt_out_cpu.txt "
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_CPU=" + PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_vol_out_cpu.txt "
                    env_list = env_list + " SHM_COMM_PATT_CNT_OUT_FILE_GPU=" + PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_cnt_out_gpu.txt "
                    env_list = env_list + " SHM_COMM_PATT_VOL_OUT_FILE_GPU=" + PROF + "MICROBENCHMARKS" + "_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                    "_weight_" + str(wght) + "_vol_out_gpu.txt "
                    env_list = env_list +  " IMI_GPUID_FILE=" + RHG + "def_gpuidfile.txt "
                    bash_cmd = "export " + env_list
                    ompi_export_list = " -x SHM_COMM_PATT_CNT_OUT_FILE_CPU -x SHM_COMM_PATT_VOL_OUT_FILE_CPU -x SHM_COMM_PATT_CNT_OUT_FILE_GPU -x SHM_COMM_PATT_VOL_OUT_FILE_GPU -x LD_LIBRARY_PATH -x IMI_GPUID_FILE "
                    # " --mca btl_smcuda_use_cuda_ipc_same_gpu 0 " +\ #needed if multi-processes are running on a single GPU
                    ompi_run_cmd = MPIRUN_PROF + " -n " + str(np) +  " --report-bindings  -hostfile " + RHG + "def_hostfile.txt "+ "-rankfile " + RHG + "def_rankfile.txt " + ompi_export_list +\
                                bench_str + " " + str(num_proc) + " " + str(niters) + " " + str(nskips)+ " " +\
                                str(bench_list[cpu_bench]) + " cpu " + str(size) + " " + str(wght) + " " + bench_dim_input[str(bench_list[cpu_bench]) + "-" + str(num_proc) + "p"] + " " +\
                                str(bench_list[gpu_bench]) + " gpu " + str(size) + " " + str(wght) + " " + bench_dim_input[str(bench_list[gpu_bench]) + "-" + str(num_proc) + "p"] +\
                                 " > " + str(PROF) + "out/" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_out.log " +\
                                 " 2>" + str(PROF) + "err/" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_err.log"
#                    print("\n", bash_cmd, "\n\n")
                    bash_cmd = bash_cmd + " && " + ompi_run_cmd            
                    print("\n", ompi_run_cmd, "\n\n")
                    sys.stdout.flush()
                    os.system(bash_cmd) 
    cnt += 1
    num_proc *= 2
########## benchmark ends ##########
