import subprocess

SVNPATH_SERVER = "/server"
SVNPATH_CLIENT = "/client/UnityClient2021New/Assets"

def get_svn_info():
    #svn log -r {2024-10-01}:{2024-10-10}/client/UnityClient2021New/Assets
    svn_path = ""
    start_time = "2024-10-01"
    end_time = "2024-10-11T23:59:59"
    cmd_client = f"svn log -r {{{start_time}}}:{{{end_time}}} {SVNPATH_CLIENT}" 
    client_result = execute_bash(cmd_client)

    cmd_server = f"svn log -r {{{start_time}}}:{{{end_time}}} {SVNPATH_SERVER}" 
    server_result = execute_bash(cmd_server)
    print(cmd_client)
    client_log = svn_log(client_result)
    server_log = svn_log(server_result)
    result = client_log.msg_list + server_log.msg_list
    return result

def execute_bash(bash_cmd):
    result = subprocess.run(bash_cmd, capture_output=True, text=True,shell=True,)
    
    if result.returncode != 0:
        print("Error executing script:")
        print(result.stderr)
        return result.stderr
    #print(result.stdout)
    return result.stdout

class svn_log:
    def __init__(self, log_str):
        self.msg_list = []
        temp_list = log_str.split('------------------------------------------------------------------------')
        temp_list = list(filter(None,temp_list))
        temp_list.pop()
        for one in temp_list:
            log_list = one.split('|')
            #print log_list
            msg = log_list[3]
            
            msg = msg.splitlines()
            commint_msg = msg[2]
            if len(msg) > 3:
                for i in range(3,len(msg)):
                    commint_msg += msg[i]

            self.msg_list.append(commint_msg)
