#!/home/farajii/bin/python_1_3.3/bin/python3
# FINDING OPTIMAL MAPPING USING HEURSTIC
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

########  Setup benchmark #########
START_PROC_NUM = 64 
#setting up result path
RESULT_PATH = "/home/farajii/git/git_iman_hessam/project1_topo_cpu_gpu/results/hoomd"
#setting up RHG Rankfile + Hostfile + GPU ID file path
RHG = RESULT_PATH + "/rhg_files/" + str(np) + "/"
#Setting up Output (Result) path
OUT= RESULT_PATH + "/out_files/" + str(np) + "/"

#Hoomd executables
HOOMD_SP = "/home/farajii/tests/14_HOOMD-blue/build5_ompi_1_10_default/bin/hoomd"
HOOMD_DP = "/home/farajii/tests/14_HOOMD-blue/build7_ompi_1_10_default_double/bin/hoomd"

#MPIRUN executable
MPIRUN = "/home/farajii/builds/9-ompi-1.10.2/bin/mpirun"

BENCH = "/home/farajii/tests/14_HOOMD-blue/hoomd-benchmarks/"

run_prec_type = ["SP", "DP"]
bench_run_type = ["opt"]

######### Bench list 1 -- different benchmark types ##########
bench_list_1 = []
#bench_list_1 = ["microsphere"]
#bench_list_1 = ["microsphere", "quasicrystal"]
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
                    bench_files = bench + "_" + particle_size
                    if run_type == "def":
                        rankfile = RHG + "def_rankfile.txt"
                        hostfile = RHG + "def_hostfile.txt"
                    else:
                        rankfile = RHG + "rankfile_" + bench_files + "_prof_" + prec_type + ".txt"
                        hostfile = RHG + "hostfile_" + bench_files + "_prof_" + prec_type + ".txt"
                    
                    env_list = RHG + "gpuidfile_" + bench_files + "_prof_" + prec_type + ".txt"
                    bash_cmd = "export " + " IMI_GPUID_FILE=" + env_list
    
                    OUTPUT = OUT + bench_str + "_" + prec_type + ".out"
                    ompi_run_cmd = MPIRUN + " -n " + str(np) +  " -hostfile " + hostfile + " -rankfile " + rankfile  + " -x LD_LIBRARY_PATH "   \
                                   + " -x IMI_GPUID_FILE " + locals()["HOOMD_" + prec_type] + " " + BENCH + bench + "/" + bench_str + ".py" + " --mode=gpu" +\
                                   " >" + str(OUT) + "out/" + str(particle_size) + "_" + run_type + "_" + prec_type + "_out.log" + " 2>" + str(OUT) + "err/" + str(particle_size) + "_" + run_type + "_" + prec_type + "_err.log"  
                    print("\n",ompi_run_cmd,"\n")
                    sys.stdout.flush()
                    mv_cmd = " mv /home/farajii/tests/14_HOOMD-blue/hoomd-benchmarks/microsphere/fpmpi_profile.txt " + str(OUT) + "out/" + str(particle_size) + "_" + run_type + "_" + prec_type + "_comm.log"
                    bash_cmd = bash_cmd + " && " + ompi_run_cmd + " && " + mv_cmd
                    os.system(bash_cmd)
    num_proc *= 2

######### Bench list 2 -- different Message Sizes ##########
bench_list_2 = ["lj"]

bench_particle_size_2 = ["512K", "1M", "2M"]
num_proc = START_PROC_NUM
while num_proc <= int(np):
    print("*********************************************************************** Test for " + str(num_proc) + " Processes ***********************************************************************\n") 
    for bench in bench_list_2:
        os.chdir(BENCH + bench)
        os.system("pwd")
        print("**************************************************************************** Benchmark: ", bench, "**********************************************************")
        for particle_size in bench_particle_size_2:
            print("**************************************************** Particle Size: ", particle_size, " ********************************************** ")
            for run_type in bench_run_type:
                print("************************************** Run type: ", run_type, " **************************************")
                for prec_type in run_prec_type:
                    print("*********************** Precision type: ", prec_type, " ***********************")
                    bench_str = bench + "_" + particle_size + "_" + run_type
                    bench_files = bench + "_" + particle_size
                    if run_type == "def":
                        rankfile = RHG + "def_rankfile.txt"
                        hostfile = RHG + "def_hostfile.txt"
                    else:
                        rankfile = RHG + "rankfile_" + bench_files + "_prof_" + prec_type + ".txt"
                        hostfile = RHG + "hostfile_" + bench_files + "_prof_" + prec_type + ".txt"
                    
                    env_list = RHG + "gpuidfile_" + bench_files + "_prof_" + prec_type + ".txt"
                    bash_cmd = "export " + " IMI_GPUID_FILE=" + env_list
    
                    OUTPUT = OUT + bench_str + "_" + prec_type + ".out"
                    ompi_run_cmd = MPIRUN + " -n " + str(np) +  " -hostfile " + hostfile + " -rankfile " + rankfile  + " -x LD_LIBRARY_PATH "   \
                                   + " -x IMI_GPUID_FILE " + locals()["HOOMD_" + prec_type] + " " + BENCH + bench + "/" + bench_str + ".py" + " --mode=gpu" +\
                                   " >" + str(OUT) + "out/" + str(particle_size) + "_" + run_type + "_" + prec_type +  "_out.log" + " 2>" + str(OUT) + "err/" + str(particle_size) + "_" + run_type + "_" + prec_type + "_err.log" 
                    print("\n",ompi_run_cmd,"\n")
                    sys.stdout.flush()
                    #mv_cmd = " mv /home/farajii/tests/14_HOOMD-blue/hoomd-benchmarks/lj/fpmpi_profile.txt " + str(OUT) + "out/" + str(particle_size) + "_" + run_type + "_" + prec_type + "_comm.log"
                    #bash_cmd = bash_cmd + " && " + ompi_run_cmd + " && " + mv_cmd 
                    bash_cmd = bash_cmd + " && " + ompi_run_cmd
                    os.system(bash_cmd)
    num_proc *= 2
