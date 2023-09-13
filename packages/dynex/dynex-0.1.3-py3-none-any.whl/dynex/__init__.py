"""
Dynex SDK (beta) Neuromorphic Computing Library
Copyright (c) 2021-2023, Dynex Developers

All rights reserved.

1. Redistributions of source code must retain the above copyright notice, this list of
    conditions and the following disclaimer.
 
2. Redistributions in binary form must reproduce the above copyright notice, this list
   of conditions and the following disclaimer in the documentation and/or other
   materials provided with the distribution.
 
3. Neither the name of the copyright holder nor the names of its contributors may be
   used to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__version__ = "0.1.3"
__author__ = 'Dynex Developers'
__credits__ = 'Dynex Developers, Contributors, Supporters and the Dynex Community'

################################################################################################################################
# IMPORTS
################################################################################################################################

# Encryption:
from Crypto.Cipher import AES
import base64
import binascii
import hashlib
import secrets

# required libs:
from pathlib import Path
from ftplib import FTP
import dimod
from itertools import combinations
import time
import numpy as np

# ini config reader:
import configparser

# progress information:
from IPython.display import clear_output
from tabulate import tabulate
from tqdm.notebook import tqdm

# test-net mode:
import subprocess
import os
import sys

# API functions:
import urllib.request, json
import base64

################################################################################################################################
# API FUNCTION CALLS
################################################################################################################################

FILE_IV = '';
FILE_KEY = '';
MAX_CHIPS = 0;
MAX_ANNEALING_TIME = 0;
MAX_DURATION = 0;
TOTAL_USAGE = False;

# parse config file:
try:
	config = configparser.ConfigParser();
	config.read('dynex.ini', encoding='UTF-8');
	API_ENDPOINT = config['DYNEX']['API_ENDPOINT']
	API_KEY = config['DYNEX']['API_KEY'];
	API_SECRET = config['DYNEX']['API_SECRET'];
except:
	raise Exception('ERROR: missing configuration file dynex.ini');

def account_status():
	check_api_status(logging = True);

def check_api_status(logging = False):
	global FILE_IV
	global FILE_KEY
	global MAX_CHIPS, MAX_ANNEALING_TIME, MAX_DURATION, TOTAL_USAGE
	url = API_ENDPOINT+'?api_key='+API_KEY+'&api_secret='+API_SECRET+'&method=status'
	with urllib.request.urlopen(url) as ret:
		data = json.load(ret);
		error = data['error'];
		status = data['status'];
	retval = False;
	if error == False and status == 'valid':
		FILE_IV = str.encode(data['i']);
		FILE_KEY = data['k'];
		MAX_CHIPS = data['max_chips'];
		MAX_ANNEALING_TIME = data['max_steps'];
		MAX_DURATION = data['max_duration'];
		MAX_USAGE = data['max_usage'];
		TOTAL_USAGE = data['total_usage'];
		ACCOUNT_NAME = data['account_name'];
		if logging:
			print('ACCOUNT:',ACCOUNT_NAME);
			print('API SUCCESSFULLY CONNECTED TO DYNEX');
			print('-----------------------------------');
			print('ACCOUNT LIMITS:');
			print('MAXIMUM NUM_READS:','{:,}'.format(MAX_CHIPS));
			print('MAXIMUM ANNEALING_TIME:','{:,}'.format(MAX_ANNEALING_TIME));
			print('MAXIMUM JOB DURATION:','{:,}'.format(MAX_DURATION),'MINUTES')
			print('');
			print('USAGE:');
			usage_pct = TOTAL_USAGE / MAX_USAGE * 100.0;
			print('TOTAL USAGE:','{:,}'.format(TOTAL_USAGE),'/','{:,}'.format(MAX_USAGE),'(',usage_pct,'%)','NUM_READS x ANNEALING_TIME');
		retval = True;
	else:
		raise Exception('INVALID API CREDENTIALS');
	return retval;

def update_job_api(JOB_ID, status, logging=True, workers=-1, lowest_loc=-1, lowest_energy=-1):
	url = API_ENDPOINT+'?api_key='+API_KEY+'&api_secret='+API_SECRET+'&method=update_job&job_id='+str(JOB_ID)+'&status='+str(status);
	url += '&workers='+str(workers)+'&lowest_loc='+str(lowest_loc)+'&lowest_energy='+str(lowest_energy);
	with urllib.request.urlopen(url) as ret:
		data = json.load(ret);
		error = data['error'];
	retval = False;
	if error == False:
		retval = True;
		if logging:
			print("[DYNEX] MALLOB: JOB UPDATED:",JOB_ID,"STATUS:",status);
	else:
                print("[DYNEX] ERROR DURING UPDATING JOB ON MALLOB");
                raise Exception('ERROR DURING UPDATING JOB ON MALLOB');
	return retval;

def generate_job_api(sampler, annealing_time, switchfraction, num_reads, alpha=20, beta=20, gamma=1, delta=1, epsilon=1, zeta=1, minimum_stepsize=0.00000006, logging=True):
	# retrieve additional data from sampler class:
	sampler_type = sampler.type;
	sampler_num_clauses = sampler.num_clauses;
	filehash = sampler.filehash;
	description = base64.b64encode(sampler.description.encode('ascii')).decode('ascii');
	filename = base64.b64encode(sampler.filename.encode('ascii')).decode('ascii');
	downloadurl = base64.b64encode(sampler.downloadurl.encode('ascii')).decode('ascii');
	solutionurl = base64.b64encode(sampler.solutionurl.encode('ascii')).decode('ascii');
	solutionuser = base64.b64encode(sampler.solutionuser.encode('ascii')).decode('ascii');

	url = API_ENDPOINT+'?api_key='+API_KEY+'&api_secret='+API_SECRET+'&method=generate_job&annealing_time='+str(annealing_time)+'&switchfraction='+str(switchfraction);
	url += '&num_reads='+str(num_reads)+'&alpha='+str(alpha)+'&beta='+str(beta)+'&gamma='+str(gamma)+'&delta='+str(delta)+'&epsilon='+str(epsilon)+'&zeta='+str(zeta);
	url += '&minimum_stepsize='+str(minimum_stepsize)+'&sampler_type='+sampler_type+'&num_clauses='+str(sampler_num_clauses)
	url += '&filehash='+filehash+'&description='+description+'&filename='+filename+'&downloadurl='+downloadurl+'&solutionurl='+solutionurl+'&solutionuser='+solutionuser;
	with urllib.request.urlopen(url) as ret:
		data = json.load(ret);
		error = data['error'];
	retval = False;
	if error == False:
		retval = True;
		if logging:
			print("[DYNEX] MALLOB: JOB CREATED: ",data['job_id']);
		return int(data['job_id']);
	else:
		print("[DYNEX] ERROR CREATING JOB:",data['message']);
		raise Exception(data['message']);
	return retval;

def get_status_details_api(JOB_ID, all_stopped = False):
        url = API_ENDPOINT+'?api_key='+API_KEY+'&api_secret='+API_SECRET+'&method=get_status&job_id='+str(JOB_ID)
        with urllib.request.urlopen(url) as ret:
                data = json.load(ret);
        table = [['WORKER','VERSION','CHIPS','LOC','ENERGY','RUNTIME','LAST UPDATE', 'STATUS']];
        LOC_MIN = 1.7976931348623158e+308;
        ENERGY_MIN = 1.7976931348623158e+308;
        CHIPS = 0;
        i = 0;
        for result in data:
            worker = result['worker_id'];
            chips = result['chips'];
            started = result['created_at'];
            updated = result['updated_at'];
            loc = result['loc'];
            energy = "{:.2f}".format(result['energy']);
            interval = "{:.2f}".format(result['lastupdate']/60)+' min';
            version = result['version'];
            lastupdate = "{:.2f}s ago".format(result['runtime'])

            status = "\033[1;31m%s\033[0m" %'STOPPED';
            if result['runtime']<=60:
                status = "\033[1;32m%s\033[0m" %'RUNNING';
            if all_stopped:
                status = "\033[1;31m%s\033[0m" %'STOPPED';

            table.append([worker, version, chips, loc, energy, interval, lastupdate, status]);

            CHIPS = CHIPS + result['chips'];
            if result['loc'] < LOC_MIN:
                LOC_MIN = result['loc'];
            if result['energy'] < ENERGY_MIN:
                ENERGY_MIN = result['energy'];
            i = i + 1;
        # not worked on:
        if i==0:
            table.append(['*** WAITING FOR WORKERS ***','','','','','','','']);
            LOC_MIN = 0;
            ENERGY_MIN = 0;
            CHIPS = 0;

        retval = tabulate(table, headers="firstrow", tablefmt="rounded_grid", stralign="right", floatfmt=".2f")

        return LOC_MIN, ENERGY_MIN, CHIPS, retval;

################################################################################################################################
# TEST FTP ACCESS
################################################################################################################################

def test():
	allpassed = True;
	print('[DYNEX] TEST: dimod BQM construction...')
	bqm = dimod.BinaryQuadraticModel({'a': 1.5}, {('a', 'b'): -1}, 0.0, 'BINARY')
	model = BQM(bqm, logging=False);
	print('[DYNEX] PASSED');
	print('[DYNEX] TEST: Dynex Sampler object...')
	sampler = DynexSampler(model,  mainnet=False, logging=False);
	print('[DYNEX] PASSED');
	print('[DYNEX] TEST: uploading computing file...')
	ret = upload_file_to_ftp(sampler.ftp_hostname, sampler.ftp_username, sampler.ftp_password, sampler.filepath+sampler.filename, sampler.ftp_path, sampler.logging);
	if ret==False:
		allpassed=False;
		print('[DYNEX] FAILED');
	else:
		print('[DYNEX] PASSED');
	time.sleep(1)
	print('[DYNEX] TEST: submitting sample file...')
	worker_user = sampler.solutionuser.split(':')[0]
	worker_pass = sampler.solutionuser.split(':')[1]
	ret = upload_file_to_ftp(sampler.solutionurl[6:-1], worker_user, worker_pass, sampler.filepath+sampler.filename, '', sampler.logging);
	if ret==False:
		allpassed=False;
		print('[DYNEX] FAILED');
	else:
		print('[DYNEX] PASSED');
	time.sleep(1)
	print('[DYNEX] TEST: retrieving samples...')
	try:
		files = list_files_with_text(sampler);
		print('[DYNEX] PASSED');
	except:
		allpassed=False;
		print('[DYNEX] FAILED');

	time.sleep(1)
	print('[DYNEX] TEST: worker access to computing files')
	url = sampler.downloadurl + sampler.filename
	try:
		with urllib.request.urlopen(url) as f:
			html = f.read().decode('utf-8');
			print('[DYNEX] PASSED');
	except:
		allpassed=False;
		print('[DYNEX] FAILED');

	if allpassed:
		print('[DYNEX] TEST RESULT: ALL TESTS PASSED');
	else:
		print('[DYNEX] TEST RESULT: ERRORS OCCURED');

################################################################################################################################
# conversation of k-sat to 3sat
################################################################################################################################

def check_list_length(lst):
    for sublist in lst:
        if isinstance(sublist, list) and len(sublist) > 3:
            return True
    return False

# find largest variable in clauses:
def find_largest_value(lst):
    largest_value = None

    for sublist in lst:
        for value in sublist:
            if largest_value is None or value > largest_value:
                largest_value = value

    return largest_value

# create a substitution clause:
def sat_creator(variables, clause_type, dummy_number, results_clauses):
    if clause_type == 1:
        #Beginning clause
        results_clauses.append([variables[0], variables[1], dummy_number])
        dummy_number *= -1

    elif clause_type == 2:
        #Middle clause
        for i in range(len(variables)):
            temp = dummy_number
            dummy_number *= -1
            dummy_number += 1
            results_clauses.append([temp, variables[i], dummy_number])
            dummy_number *= -1

    elif clause_type == 3:
        #Final clause
        for i in range(len(variables)-2):
            temp = dummy_number
            dummy_number *= -1
            dummy_number += 1
            results_clauses.append([temp, variables[i], dummy_number])
            dummy_number *= -1   
        results_clauses.append([dummy_number, variables[-2], variables[-1]])
        dummy_number *= -1
        dummy_number += 1
        
    return dummy_number, results_clauses

# convert from k-sat to 3sat:
def ksat(clauses):
    results_clauses = [];
    results_clauses.append([1])
    variables = find_largest_value(clauses);
    dummy_number = variables + 1;
    for values in clauses:
        total_variables = len(values)
        #Case 3 variables
        if total_variables == 3:
            results_clauses.append([values[0], values[1], values[2]])
        else:
            #Case 1 variable
            if total_variables == 1:
                results_clauses.append([values[0]])
            #Case 2 variables
            elif total_variables == 2:
                results_clauses.append([values[0], values[1]])
                dummy_number += 1
            #Case more than 3 variable
            else:
                first_clause = values[:2]
                dummy_number, results_clauses = sat_creator(first_clause, 1, dummy_number, results_clauses)

                middle_clauses = values[2:len(values)-2]
                dummy_number, results_clauses = sat_creator(middle_clauses, 2, dummy_number, results_clauses)

                last_clause = values[len(values)-2:]
                dummy_number, results_clauses = sat_creator(last_clause, 3, dummy_number, results_clauses)

    return results_clauses

################################################################################################################################
# utility functions
################################################################################################################################

def calculate_sha3_256_hash(string):
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(string.encode('utf-8'))
    return sha3_256_hash.hexdigest()

def Convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct;

def check_list_length(lst):
    for sublist in lst:
        if isinstance(sublist, list) and len(sublist) > 3:
            return True
    return False

def max_value(inputlist):
    return max([sublist[-1] for sublist in inputlist])

################################################################################################################################
# upload file to an FTP server
################################################################################################################################

def upload_file_to_ftp(hostname, username, password, local_file_path, remote_directory, logging=True):
    retval = True;
    try:
        ftp = FTP(hostname)
        ftp.login(username, password)
        # Change to the remote directory
        ftp.cwd(remote_directory)
    
        # Open the local file in binary mode for reading
        with open(local_file_path, 'rb') as file:
            total = os.path.getsize(local_file_path); # file size
            # sanity check:
            if total > 104857600:
                print("[ERROR] PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)");
                raise Exception('PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)');
    
            if logging:
                with tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, desc='file upload progress') as pbar:
                    
                    def cb(data):
                        pbar.update(len(data))
                    
                    # Upload the file to the FTP server
                    ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file, 1024, cb)
            else:
                # Upload the file to the FTP server
                ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file)
    
        if logging:
            print(f"[DYNEX] File '{local_file_path}' sent successfully to '{hostname}/{remote_directory}'")

    except Exception as e:
        print(f"[DYNEX] An error occurred while sending the file: {str(e)}")
        retval = False;
    finally:
        ftp.quit();
    return retval;

################################################################################################################################
# retrieve all files starting with "sampler.filename" from an FTP server
################################################################################################################################

def list_files_with_text(sampler):
    host = sampler.solutionurl[6:-1];
    username = sampler.solutionuser.split(":")[0];
    password = sampler.solutionuser.split(":")[1]; 
    directory = "";
    text = sampler.filename;
    # Connect to the FTP server
    ftp = FTP(host)
    ftp.login(username, password)
    
    # Change to the specified directory
    ftp.cwd(directory)
    
    # List all files in the directory
    file_list = ftp.nlst()
    
    # Filter the file list to include only files beginning with the specified text
    filtered_files = [file for file in file_list if file.startswith(text)]
    
    # Close the FTP connection
    ftp.quit()
    
    return filtered_files

################################################################################################################################
# retrieve all files starting with "sampler.filename" from test-net
################################################################################################################################

def list_files_with_text_local(sampler):
    directory = sampler.filepath_full; 
    fn = sampler.filename+".";
    # list to store files
    filtered_files = []

    for filename in os.listdir(directory):
        if filename.startswith(fn):
            filtered_files.append(filename)
    return filtered_files;    
    
################################################################################################################################
# Download file from FTP to sampler.filepath / filename
################################################################################################################################

def download_file(sampler, filename):
    host = sampler.solutionurl[6:-1];
    username = sampler.solutionuser.split(":")[0];
    password = sampler.solutionuser.split(":")[1]; 
    directory = "";
    local_path = sampler.filepath+filename;
    # Connect to the FTP server
    ftp = FTP(host)
    ftp.login(username, password)
    
    # Change to the specified directory
    ftp.cwd(directory)
    
    # Download the file
    with open(local_path, 'wb') as file:
        ftp.retrbinary('RETR ' + filename, file.write)
    
    # Close the FTP connection
    ftp.quit()

################################################################################################################################
# generate filehash for worker
################################################################################################################################

def generate_hash(filename):
    with open(filename, 'r') as file:
        data = file.read().replace('\n', '');
    return calculate_sha3_256_hash(data);

################################################################################################################################
# AES Encryption / Decryption class
################################################################################################################################

def aes_encrypt(raw):
    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    raw = pad(raw);
    cipher = AES.new(FILE_KEY.encode("utf8"), AES.MODE_CBC, FILE_IV);
    output = cipher.encrypt(raw.encode("utf8"));
    output_str = binascii.hexlify(output);
    output_str = str(output_str)[2:-1];
    return output_str

################################################################################################################################
# save clauses to SAT cnf file
################################################################################################################################

def save_cnf(clauses, filename, mainnet):
    num_variables = max(max(abs(lit) for lit in clause) for clause in clauses);
    num_clauses = len(clauses);
    
    with open(filename, 'w') as f:
        line = "p cnf %d %d" % (num_variables, num_clauses);
        
        if mainnet:
            line_enc = aes_encrypt(line);
        else:
            line_enc = line;
        
        f.write(line_enc+"\n"); 
        
        for clause in clauses:
            line = ' '.join(str(int(lit)) for lit in clause) + ' 0';
        
            if mainnet:
                line_enc = aes_encrypt(line);
            else:
                line_enc = line;
        
            f.write(line_enc+"\n");

################################################################################################################################
# save wcnf file
################################################################################################################################

def save_wcnf(clauses, filename, num_variables, num_clauses, mainnet):

    with open(filename, 'w') as f:
        line = "p wcnf %d %d" % (num_variables, num_clauses);
        
        if mainnet:
            line_enc = aes_encrypt(line);
        else:
            line_enc = line;

        f.write(line_enc+"\n"); 

        for clause in clauses:
            line = ' '.join(str(int(lit)) for lit in clause) + ' 0';
        
            if mainnet:
                line_enc = aes_encrypt(line);
            else:
                line_enc = line;
        
            f.write(line_enc+"\n"); 

        
################################################################################################################################
# functions to convert BQM to wcnf
################################################################################################################################

def convert_bqm_to_wcnf(bqm, relabel=True, logging=True):
    
    # relabel variables:
    if relabel:
        relabeled = {};
        for i in range (0,len(bqm.variables)):
            relabeled[i] = str(i+1);
        bqm_new = bqm.relabel_variables(relabeled, inplace=False)
    else:
        bqm_new = bqm;

    # convert bqm to_qubo model:
    clauses = [];
    Q = bqm_new.to_qubo();
    Q_list = list(Q[0]);
    if logging:
        print("[DYNEX] MODEL CONVERTED TO QUBO")
    
    # precision:
    newQ = [];
    for i in range(0, len(Q_list)):
        touple = Q_list[i];
        w = Q[0][touple];
        newQ.append(w);
    max_abs_coeff = np.max(np.abs(newQ));
    if max_abs_coeff == 0:
        print('[DYNEX] ERROR: AT LEAST ONE WEIGHT MUST BE > 0.0');
        return [],0,0,[],0

    precision = 10 ** (np.floor(np.log10(max_abs_coeff)) - 4);

    # max precision is 1:
    if precision>1:
        if logging:
            print("[ÐYNEX] PRECISION CUT FROM",precision,"TO 1");
        precision = 1;

    if logging:
        print("[DYNEX] PRECISION SET TO", precision);

    # constant offset:
    W_add = Q[1]; 
    if logging:
        print("[DYNEX] QUBO: Constant offset of the binary quadratic model:", W_add);

    for i in range(0, len(Q_list)):
        touple = Q_list[i];
        i = int(touple[0]);
        j = int(touple[1]);
        w = Q[0][touple];
        w_int = int(np.round(w/precision));
        
        # linear term:
        if i==j:
            if w_int > 0:
                clauses.append([w_int,-i]);
            if w_int < 0:
                clauses.append([-w_int, i]);
        
        # quadratic term:
        if i!=j:
            if w_int > 0:
                clauses.append([w_int, -i, -j]);
            if w_int < 0:
                clauses.append([-w_int, i, -j]);
                clauses.append([-w_int, j]);
        
    num_variables = len(bqm.variables);
    num_clauses = len(clauses);
    
    label_mappings = {};
    i = 1;
    for var in bqm.variables:
        label_mappings[var] = i;
        i = i + 1;
    
    return clauses, num_variables, num_clauses, label_mappings, precision

################################################################################################################################
# Supported Model Classes
################################################################################################################################

class SAT():
    def __init__(self, clauses, logging=True):
        self.clauses = clauses;
        self.type = 'cnf';
        self.bqm = "";
        self.logging = logging;
        self.typestr = 'SAT';

class BQM():
    def __init__(self, bqm, relabel=True, logging=True):
        self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision = convert_bqm_to_wcnf(bqm, relabel, logging);
        if self.num_clauses == 0 or self.num_variables == 0:
            return;
        self.type = 'wcnf';
        self.bqm = bqm;
        self.logging = logging;
        self.typestr = 'BQM';

class CQM():
    def __init__(self, cqm, relabel=True, logging=True):
        bqm, self.invert = dimod.cqm_to_bqm(cqm)
        self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision = convert_bqm_to_wcnf(bqm, relabel, logging);
        self.type = 'wcnf';
        self.bqm = bqm;
        self.logging = logging;
        self.typestr = 'CQM';

################################################################################################################################
# Dynex Sampler class
################################################################################################################################

class DynexSampler:
    def __init__(self, model, logging=True, mainnet=True, description='Dynex SDK Job'):
        
        self.description = description;

        # parse config file:
        config = configparser.ConfigParser();
        config.read('dynex.ini', encoding='UTF-8');
        
        # SDK Authenticaton:
        if not check_api_status():
            raise Exception("API credentials invalid");

        # FTP & HTTP GET data where miners are accessing problem files:
        self.ftp_hostname = config['FTP_COMPUTING_FILES']['ftp_hostname'];
        self.ftp_username = config['FTP_COMPUTING_FILES']['ftp_username'];
        self.ftp_password = config['FTP_COMPUTING_FILES']['ftp_password'];
        self.ftp_path     = config['FTP_COMPUTING_FILES']['ftp_path'];
        self.downloadurl  = config['FTP_COMPUTING_FILES']['downloadurl'];
        
        # FTP data where miners submit results:
        self.solutionurl  = 'ftp://'+config['FTP_SOLUTION_FILES']['ftp_hostname']+'/';
        self.solutionuser = config['FTP_SOLUTION_FILES']['ftp_username']+":"+config['FTP_SOLUTION_FILES']['ftp_password'];
        
        # local path where tmp files are stored
        tmppath = Path("tmp/test.bin");
        tmppath.parent.mkdir(exist_ok=True);
        with open(tmppath, 'w') as f:
            f.write('0123456789ABCDEF')
        self.filepath = 'tmp/'
        self.filepath_full = os.getcwd()+'/tmp'

        # path to testnet
        self.solverpath = 'testnet/';

        # auto generated temp filename:
        self.filename = secrets.token_hex(16)+".bin";
        self.logging = logging;
        self.mainnet = mainnet;
        self.typestr = model.typestr;
        
        if model.type == 'cnf':
            # convert to 3sat?
            if (check_list_length(model.clauses)):
                #we need to convert:
                self.clauses = ksat(model.clauses);
            else:
                self.clauses = model.clauses;
            save_cnf(self.clauses, self.filepath+self.filename, mainnet);
            self.num_clauses = len(self.clauses);
            self.num_variables = max_value(self.clauses) - 1;
        
        if model.type == 'wcnf':
            self.clauses = model.clauses;
            self.num_variables = model.num_variables;
            self.num_clauses = model.num_clauses;
            self.var_mappings = model.var_mappings;
            self.precision = model.precision;
            save_wcnf(self.clauses, self.filepath+self.filename, self.num_variables, self.num_clauses, mainnet); 

        self.filehash     = generate_hash(self.filepath+self.filename);
        self.type = model.type;
        self.assignments = {};
        self.dimod_assignments = {};
        self.bqm = model.bqm;

        if self.logging:
            print("[DYNEX] SAMPLER INITIALISED")

    def __exit__(self, exc_type, exc_value, traceback):
        print('[DYNEX] SAMPLER EXIT');
        
    def update(self, model, logging=True):
        self.logging = logging;
        self.filename     = secrets.token_hex(16)+".bin"; 
        
        if model.type == 'cnf':
            # convert to 3sat?
            if (check_list_length(model.clauses)):
                self.clauses = ksat(model.clauses);
            else:
                self.clauses = model.clauses;
            save_cnf(self.clauses, self.filepath+self.filename);
        
        if model.type == 'wcnf':
            self.clauses = model.clauses;
            self.num_variables = model.num_variables;
            self.num_clauses = model.num_clauses;
            self.var_mappings = model.var_mappings;
            save_wcnf(self.clauses, self.filepath+self.filename, self.num_variables, self.num_clauses, self.mainnet); 
        
        self.filehash     = generate_hash(self.filepath+self.filename);
        self.type = model.type;
        self.assignments = {};
        self.bqm = model.bqm;

    # print summary of sampler:
    def print(self):
        print('{DynexSampler object}');
        print('mainnet?', self.mainnet);
        print('logging?', self.logging);
        print('tmp filename:',self.filepath+self.filename);
        print('tmp filehash:',self.filehash);
        print('model type:', self.typestr);
        print('num variables:', self.num_variables);
        print('num clauses:', self.num_clauses);
        print('configuration: dynex.ini');

    # convert a sampleset[x]['sample'] into an assignment:
    def sample_to_assignments(self, lowest_set):
        sample = {};
        i = 0;
        for var in self.var_mappings:
            sample[var] = 1;
            if (float(lowest_set[i])<0):
                sample[var] = 0;
            i = i + 1
        return sample;

    # read and parse all local files which are now available:
    def read_and_parse(self):

        mainnet = self.mainnet;

        # retrieve solutions
        if mainnet:
            files = list_files_with_text(self); 
        else:
            files = list_files_with_text_local(self); 
            time.sleep(1);

        if self.logging:
            print("[DYNEX] PARSING",len(files),'VOLTAGE ASSIGNMENT FILES...');

        # now load voltages: ---------------------------------------------------------------------------------------------------
        pbar = tqdm(total = len(files), position=0, desc='progress');
        sampleset = [];
        lowest_energy = 1.7976931348623158e+308;
        lowest_loc = 1.7976931348623158e+308;
        total_chips = 0;
        total_steps = 0;
        lowest_set = [];
        for file in files:
            # 882adec77821468c57ad14f4d707be3e.cnf.32.1.0.0.000000
            # jobfile chips steps loc energy
            info = file[len(self.filename)+1:];
            chips = int(info.split(".")[0]);
            steps = int(info.split(".")[1]);
            loc = int(info.split(".")[2]);
            
            # energy can also be non decimal:
            if len(info.split("."))>4:
                energy = float(info.split(".")[3]+"."+info.split(".")[4]);
            else:
                energy = float(info.split(".")[3]);
            total_chips = total_chips + chips;
            total_steps = steps;
            
            # download file and get energies:
            if mainnet:
                download_file(self, file);
            
            with open(self.filepath+file, 'r') as file:
                data = file.read();
                # enough data?
                
                if mainnet:
                    if len(data)>100:
                        wallet = data.split("\n")[0];
                        tmp = data.split("\n")[1];
                        voltages = tmp.split(", ")[:-1];
                    else:
                        voltages = ['NaN']; # invalid file received
                else: # test-net is not returning wallet
                    voltages = data.split(", ")[:-1];

            # valid result? ignore Nan values
            if len(voltages)>0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                sampleset.append(['sample',voltages,'chips',chips,'steps',steps,'falsified softs',loc,'energy',energy]);
                if loc < lowest_loc:
                    lowest_loc = loc;
                if energy < lowest_energy:
                    lowest_energy = energy;
                    lowest_set = voltages;

            # update progress bar:
            pbar.update(1);
        
        sampleset.append(['sample',lowest_set,'chips',total_chips,'steps',total_steps,'falsified softs',lowest_loc,'energy',lowest_energy]);
        
        # build sample dict "assignments" with 0/1: -------------------------------------------------------------------------------------
        if self.type == 'wcnf' and len(lowest_set) == self.num_variables:
            sample = {};
            i = 0;
            for var in self.var_mappings:
                sample[var] = 1;
                if (float(lowest_set[i])<0):
                    sample[var] = 0;
                i = i + 1
            self.assignments = sample;

            # generate dimod format  sampleset: ---------------------------------------------------------------------------------------------
            self.dimod_assignments = dimod.SampleSet.from_samples_bqm(sample, self.bqm);

        if self.logging:
            print("[DYNEX] SAMPLESET LOADED");
        
        # create return sampleset: ------------------------------------------------------------------------------------------------------
        sampleset_clean = [];
        for sample in sampleset:
            sample_dict = Convert(sample);
            sampleset_clean.append(sample_dict);

        return sampleset_clean;
        
    # sampling process:
    def sample(self, num_reads = 32, annealing_time = 10, switchfraction = 0.0, alpha=20, beta=20, gamma=1, delta=1, epsilon=1, zeta=1, minimum_stepsize = 0.00000006, debugging=False, waittime=15):

        mainnet = self.mainnet;

        try:
        
            # step 1: upload problem file to Dynex Platform: ---------------------------------------------------------------------------------
            if mainnet:
                # create job on mallob system:
                JOB_ID = generate_job_api(self, annealing_time, switchfraction, num_reads, alpha, beta, gamma, delta, epsilon, zeta, minimum_stepsize, self.logging);
                # upload job:
                if self.logging:
                    print("[ÐYNEX] SUBMITTING JOB - UPLOADING JOB FILE...");
                ret = upload_file_to_ftp(self.ftp_hostname, self.ftp_username, self.ftp_password, self.filepath+self.filename, self.ftp_path, self.logging);
                if ret == False:
                    raise Exception("[DYNEX] ERROR: FILE UPLOAD FAILED.");

                # now set the job as ready to be worked on:
                if self.logging:
                    print("[ÐYNEX] SUBMITTING START COMMAND...");
                if not update_job_api(JOB_ID, 0, self.logging):
                    raise Exception('ERROR: CANNOT START JOB')
                # and restart some workers so work gets picked up:
                # disabled temp restart_workers(JOB_ID, self.logging);

                if self.logging:
                    print("[ÐYNEX] STARTING JOB...");
            else:
                # run on test-net:
                if self.type == 'wcnf':
                    localtype = 5;
                if self.type == 'cnf':
                    localtype = 0;
                JOB_ID = -1;
                command = self.solverpath+"np -t="+str(localtype)+" -ms="+str(annealing_time)+" -st=1 -msz="+str(minimum_stepsize)+" -c="+str(num_reads)+" --file='"+self.filepath_full+"/"+self.filename+"'";

                if alpha!=0:
                    command = command + " --alpha=" + str(alpha);
                if beta!=0:
                    command = command + " --beta=" + str(beta);
                if gamma!=0:
                    command = command + " --gamma=" + str(gamma);
                if delta!=0:
                    command = command + " --delta=" + str(delta);
                if epsilon!=0:
                    command = command + " --epsilon=" + str(epsilon);
                if zeta!=0:
                    command = command + " --zeta=" + str(zeta);

                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                if debugging:
                    for c in iter(lambda: process.stdout.read(1), b""):
                        sys.stdout.write(c.decode('utf-8'))
                else:
                    if self.logging:
                    	print("[DYNEX|TESTNET] *** WAITING FOR READS ***");
                    process.wait();

            # step 2: wait for process to be finished: -------------------------------------------------------------------------------------
            t = time.process_time();
            finished = False;
            runupdated = False;
            while finished==False:
                total_chips = 0;
                total_steps = 0;
                lowest_energy = 1.7976931348623158e+308;
                lowest_loc = 1.7976931348623158e+308;

                # retrieve solutions
                if mainnet:
                    try:
                        files = list_files_with_text(self);
                    except:
                        print('[DYNEX] CONNECTION WITH FTP ENDPOINT FAILED');
                        files = []; 
                else:
                    files = list_files_with_text_local(self); 
                    time.sleep(1);

                for file in files:
                    info = file[len(self.filename)+1:];
                    chips = int(info.split(".")[0]);
                    steps = int(info.split(".")[1]);
                    loc = int(info.split(".")[2]);
                    # energy can also be non decimal:
                    if len(info.split("."))>4:
                        energy = float(info.split(".")[3]+"."+info.split(".")[4]);
                    else:
                        energy = float(info.split(".")[3]);
                    total_chips = total_chips + chips;
                    total_steps = steps;
                    if energy < lowest_energy:
                        lowest_energy = energy;
                    if loc < lowest_loc:
                        lowest_loc = loc;
                    if self.type=='cnf' and loc == 0:
                        finished = True;
                    if total_chips >= num_reads*0.90:
                        finished = True;
                if len(files)<1:
                    if self.logging:
                        if mainnet:
                        	clear_output(wait=True);
                        if mainnet:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = get_status_details_api(JOB_ID);
                        else:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0,0,0;
                            details = "";
                        elapsed_time = time.process_time() - t;
                        # display:
                        table = ([['DYNEXJOB','ELAPSED','WORKERS','CHIPS','✔','STEPS','LOC','✔','ENERGY','✔']]);
                        table.append(['','','*** WAITING FOR READS ***','','','','','','','']);
                        ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f");
                        print(ta+'\n'+details);
                        
                    time.sleep(2); 

                else:
                    if self.logging:
                        if mainnet:
                        	clear_output(wait=True);
                        if mainnet:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = get_status_details_api(JOB_ID);
                        else:
                            LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0,0,0;
                            details = "";
                        elapsed_time = time.process_time() - t;
                        # display:
                        table = ([['DYNEXJOB','ELAPSED','WORKERS','CHIPS','✔','STEPS','LOC','✔','ENERGY','✔']]);
                        table.append([JOB_ID, elapsed_time, len(files), MALLOB_CHIPS, total_chips, total_steps, LOC_MIN, lowest_loc, ENERGY_MIN, lowest_energy]);
                        ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f");
                        print(ta+'\n'+details);

                        # update mallob - job running: -------------------------------------------------------------------------------------------------
                        if runupdated==False and mainnet:
                            update_job_api(JOB_ID, 1, self.logging);
                            runupdated = True;
                    time.sleep(2);

            # update final output (display all workers as stopped as well):
            if len(files)>0 and self.logging:
                if mainnet:
                	clear_output(wait=True);
                if mainnet:
                    LOC_MIN, ENERGY_MIN, MALLOB_CHIPS, details = get_status_details_api(JOB_ID, all_stopped = True);
                else:
                    LOC_MIN, ENERGY_MIN, MALLOB_CHIPS = 0,0,0;
                    details = "";
                elapsed_time = time.process_time() - t;
                if mainnet:
                    # display:
                    table = ([['DYNEXJOB','ELAPSED','WORKERS','CHIPS','✔','STEPS','LOC','✔','ENERGY','✔']]);
                    table.append([JOB_ID, elapsed_time, len(files), MALLOB_CHIPS, total_chips, total_steps, LOC_MIN, lowest_loc, ENERGY_MIN, lowest_energy]);
                    ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f");
                    print(ta+'\n'+details);
                
            elapsed_time = time.process_time() - t
            if self.logging:
                print("[DYNEX] FINISHED READ AFTER","%.2f" % elapsed_time,"SECONDS");

            # update mallob - job finished: -------------------------------------------------------------------------------------------------
            if mainnet:
                update_job_api(JOB_ID, 2, self.logging, workers=len(files), lowest_loc=lowest_loc, lowest_energy=lowest_energy);

            # step 3: now load voltages: ---------------------------------------------------------------------------------------------------
            if mainnet:
                print("[DYNEX] WAITING "+str(waittime)+" SECONDS FOR ALL WORKERS TO SUBMIT READS...");
                time.sleep(waittime); # allow some time until the file is fully uploaded

                try:
                    files = list_files_with_text(self);
                except:
                    print('[DYNEX] CONNECTION WITH FTP ENDPOINT FAILED');
                    files = []; 

                print("[DYNEX] READING ",len(files),"VOLTAGES...")

                pbar = tqdm(total = len(files), position=0, desc='progress');

            sampleset = [];
            lowest_energy = 1.7976931348623158e+308;
            lowest_loc = 1.7976931348623158e+308;
            total_chips = 0;
            total_steps = 0;
            lowest_set = [];
            for file in files:
                # format: xxx.bin.32.1.0.0.000000
                # jobfile chips steps loc energy
                info = file[len(self.filename)+1:];
                chips = int(info.split(".")[0]);
                steps = int(info.split(".")[1]);
                loc = int(info.split(".")[2]);

                # energy can also be non decimal:
                if len(info.split("."))>4:
                    energy = float(info.split(".")[3]+"."+info.split(".")[4]);
                else:
                    energy = float(info.split(".")[3]);
                total_chips = total_chips + chips;
                total_steps = steps;

                # download file and get energies:
                if mainnet:
                    download_file(self, file);

                with open(self.filepath+file, 'r') as file:
                    data = file.read();
                    # enough data?
                    if mainnet:
                    	if len(data)>96:
                    		wallet = data.split("\n")[0];
                    		tmp = data.split("\n")[1];
                    		voltages = tmp.split(", ")[:-1];
                    	else:
                    		voltages = ['NaN']; # invalid file received
                    else: # test-net is not returning wallet
                    	voltages = data.split(", ")[:-1];

                # valid result? ignore Nan values
                if len(voltages)>0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                    sampleset.append(['sample',voltages,'chips',chips,'steps',steps,'falsified softs',loc,'energy',energy]);
                    if loc < lowest_loc:
                        lowest_loc = loc;
                    if energy < lowest_energy:
                        lowest_energy = energy;
                        lowest_set = voltages;

                # update progress bar:
                if mainnet:
                    pbar.update(1);

            sampleset.append(['sample',lowest_set,'chips',total_chips,'steps',total_steps,'falsified softs',lowest_loc,'energy',lowest_energy]);
            elapsed_time = time.process_time() - t;
            
            # build sample dict "assignments" with 0/1: -------------------------------------------------------------------------------------
            if self.type == 'wcnf' and len(lowest_set) == self.num_variables:
                sample = {};
                i = 0;
                for var in self.var_mappings:
                    sample[var] = 1;
                    if (float(lowest_set[i])<0):
                        sample[var] = 0;
                    i = i + 1
                self.assignments = sample;

                # generate dimod format  sampleset: ---------------------------------------------------------------------------------------------
                self.dimod_assignments = dimod.SampleSet.from_samples_bqm(sample, self.bqm);

            if self.logging:
                print("[DYNEX] SAMPLESET LOADED");
            
            # create return sampleset: ------------------------------------------------------------------------------------------------------
            sampleset_clean = [];
            for sample in sampleset:
                sample_dict = Convert(sample);
                sampleset_clean.append(sample_dict);

        except KeyboardInterrupt:
            if mainnet:
                update_job_api(JOB_ID, 2, self.logging);
            print("[DYNEX] Keyboard interrupt");
            return {};

        except Exception as e:
            if mainnet:
                update_job_api(JOB_ID, 2, self.logging);
            print("[DYNEX] Exception encountered:", e);
            return {};

        return sampleset_clean;
        
