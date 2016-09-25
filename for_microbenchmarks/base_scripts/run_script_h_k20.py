#!/home/farajii/bin/python_1_3.3/bin/python3

#RUNNING MICROBENCHMARKS 
import sys, getopt, os

def usage():
    print("-p Num of processes")
    print("-n Num of nodes (Need this to make the default host and rank files)")
    print("-g Num GPUs per node")
    print("-i Num of iterations")
    print("-s Num of skips")

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

#Setting up Output (Result) path
OUT= RESULT_PATH + "/out_files/" + str(np) + "/"

#Microbenchmark executable
bench_path = "/home/farajii/tests/22_MICROBENCHMARKS/RUN"
bench_str = bench_path + "/MICRO_BENCHMARK"
#MPIRUN executable
MPIRUN = "/home/farajii/builds/9-ompi-1.10.2/bin/mpirun"
size_list = ["256", "8192", "65536", "262144", "1048576"] #small, medium, and, large message
wght_list = ["1", "3"]
bench_run_type = ["opt"]

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
iter_mul = 1
########## run benchmark ##########
num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for run_type in bench_run_type:
        print("********************************************************** Run type : " + str(run_type) + " **********************************************************\n")
        for size in size_list:
            if (int(size) > 65536):
                iter_mul = 1
            else:
                iter_mul = 10
            print("********************************************************** Size: " + str(size) + " **********************************************************\n")
            for wght in wght_list:
                print("**************************************** Weight: " + str(wght) + " ***********************************************\n")
                for cpu_bench in range(len(bench_list)):
                    for gpu_bench in range(len(bench_list)):
                        if run_type == "def":
                            rankfile = RHG + "def_rankfile.txt"
                            hostfile = RHG + "def_hostfile.txt"
                            env_list = RHG + "def_gpuidfile.txt"
                        else:
                            rankfile = RHG + "rankfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                            "_weight_" + str(wght) + ".txt"
                            hostfile =  RHG + "hostfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                           "_weight_" + str(wght) + ".txt"
                            env_list = "SKIP"
                            #env_list = RHG + "gpuidfile_MICROBENCHMARKS_" + bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) +\
                            #"_weight_" + str(wght) + ".txt"
                        #print(env_list, "-----\n")
                        bash_cmd = "export " + "IMI_GPUID_FILE=" + env_list        
#                       " --mca btl_smcuda_use_cuda_ipc_same_gpu"
                        ompi_run_cmd = MPIRUN + " -n " + str(np) +  " --report-bindings -hostfile " + hostfile + " -rankfile " + rankfile + " -x IMI_GPUID_FILE -x LD_LIBRARY_PATH " +\
                                    bench_str + " " + str(num_proc) + " " + str(int( int(niters) * int(iter_mul))) + " " + str(int(int(nskips) * int(iter_mul))) + " " +\
                                    str(bench_list[cpu_bench]) + " cpu " + str(size) + " " + str(wght) + " " + bench_dim_input[str(bench_list[cpu_bench]) + "-" + str(num_proc) + "p"] + " " +\
                                    str(bench_list[gpu_bench]) + " gpu " + str(size) + " " + str(wght) + " " + bench_dim_input[str(bench_list[gpu_bench]) + "-" + str(num_proc) + "p"] +\
                                    " >" + str(OUT) + "out/"+run_type+"_"+bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_out.log" +\
                                    " 2>"+ str(OUT)+ "err/"+run_type+"_"+bench_list[cpu_bench] + "_" + bench_list[gpu_bench] + "_size_" + str(size) + "_weight_" + str(wght) + "_err.log" 
                        bash_cmd = bash_cmd + " && " + ompi_run_cmd
                        print("\n",ompi_run_cmd,"\n")
                        sys.stdout.flush()
                        os.system(bash_cmd)
    num_proc *= 2
########## benchmark ends ##########
